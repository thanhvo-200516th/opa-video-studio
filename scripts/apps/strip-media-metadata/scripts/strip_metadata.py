#!/usr/bin/env python3
"""Strip identifying metadata (EXIF, XMP, IPTC, C2PA/JUMBF, AI prompts, comments)
from images and videos, in place.

Images (JPEG, PNG, WebP, GIF) are rewritten at the container level; pixel data is
copied byte for byte, never re-encoded. Videos (MP4/MOV, MKV/WebM, AVI) are
remuxed with ffmpeg -c copy, which drops container tags and unknown boxes.

Usage: strip_metadata.py [--check] [--keep-icc] FILE...
  --check     only report the metadata found; change nothing
  --keep-icc  keep embedded ICC colour profiles (removed by default, like exiftool -all=)
Exit status is 1 if any file failed, is unsupported, or still has metadata.
"""
import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

ORIENTATION_TAG = 0x0112


def read_orientation(tiff):
    """Return a non-default EXIF Orientation (2-8) from TIFF bytes, else None."""
    if tiff.startswith(b"Exif\0\0"):
        tiff = tiff[6:]
    try:
        endian = {b"II": "<", b"MM": ">"}[tiff[:2]]
        ifd = struct.unpack(endian + "I", tiff[4:8])[0]
        count = struct.unpack(endian + "H", tiff[ifd:ifd + 2])[0]
        for i in range(count):
            entry = tiff[ifd + 2 + 12 * i:ifd + 14 + 12 * i]
            tag, typ = struct.unpack(endian + "HH", entry[:4])
            if tag == ORIENTATION_TAG and typ == 3:
                value = struct.unpack(endian + "H", entry[8:10])[0]
                return value if 2 <= value <= 8 else None
    except (KeyError, struct.error):
        pass
    return None


def minimal_exif(orientation):
    """TIFF block holding only the Orientation tag, so rotated photos still display upright."""
    return (b"MM\0*" + struct.pack(">IH", 8, 1)
            + struct.pack(">HHIHH", ORIENTATION_TAG, 3, 1, orientation, 0)
            + struct.pack(">I", 0))


def label(raw):
    """Short printable name for a metadata block identifier."""
    text = raw.split(b"\0", 1)[0][:32].decode("latin-1")
    return "".join(c if c.isprintable() else "?" for c in text)


# ---------------------------------------------------------------- JPEG

def strip_jpeg(data, keep_icc):
    out, removed = [data[:2]], []
    orientation, jfif = None, False
    pos = 2
    while True:
        if pos + 2 > len(data) or data[pos] != 0xFF:
            raise ValueError("truncated or corrupt JPEG")
        marker = data[pos + 1]
        if marker == 0xFF:  # fill byte
            pos += 1
            continue
        if marker == 0xD9:  # EOI; anything after it (MPF images, trailers) is dropped
            out.append(data[pos:pos + 2])
            if pos + 2 < len(data):
                removed.append(f"{len(data) - pos - 2} bytes after end of image")
            break
        if 0xD0 <= marker <= 0xD7 or marker == 0x01:
            out.append(data[pos:pos + 2])
            pos += 2
            continue
        end = pos + 2 + struct.unpack(">H", data[pos + 2:pos + 4])[0]
        segment, payload = data[pos:end], data[pos + 4:end]
        if marker == 0xDA:  # start of scan: copy entropy-coded data up to the next marker
            scan = end
            while not (data[scan] == 0xFF and data[scan + 1] != 0x00
                       and not 0xD0 <= data[scan + 1] <= 0xD7):
                scan += 1
            out.append(data[pos:scan])
            pos = scan
            continue
        keep = True
        if marker == 0xE0:
            keep = payload.startswith(b"JFIF\0")
            jfif = jfif or keep
        elif marker == 0xE2 and payload.startswith(b"ICC_PROFILE\0"):
            keep = keep_icc
        elif marker == 0xEE:  # Adobe APP14 carries the colour transform needed to decode
            keep = True
        elif 0xE1 <= marker <= 0xEF or marker == 0xFE:
            keep = False
            if marker == 0xE1 and payload.startswith(b"Exif\0\0"):
                orientation = read_orientation(payload)
        if keep:
            out.append(segment)
        else:
            name = "COM comment" if marker == 0xFE else f"APP{marker - 0xE0} {label(payload)}"
            removed.append(name)
        pos = end
    if orientation:
        tiff = b"Exif\0\0" + minimal_exif(orientation)
        out.insert(2 if jfif else 1, b"\xff\xe1" + struct.pack(">H", len(tiff) + 2) + tiff)
    return b"".join(out), removed


# ---------------------------------------------------------------- PNG

PNG_KEEP = {b"tRNS", b"gAMA", b"cHRM", b"sRGB", b"sBIT", b"pHYs", b"bKGD", b"hIST",
            b"acTL", b"fcTL", b"fdAT", b"cICP", b"mDCV", b"cLLI"}


def png_chunk(ctype, body):
    return struct.pack(">I", len(body)) + ctype + body + struct.pack(">I", zlib.crc32(ctype + body))


def strip_png(data, keep_icc):
    out, removed, orientation = [data[:8]], [], None
    pos = 8
    while True:
        if pos + 12 > len(data):
            raise ValueError("truncated PNG (no IEND)")
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 12 + length
        critical = ctype[:1].isupper()
        if critical or ctype in PNG_KEEP or (ctype == b"iCCP" and keep_icc):
            if ctype == b"IDAT" and orientation:
                out.append(png_chunk(b"eXIf", minimal_exif(orientation)))
                orientation = None
            out.append(data[pos:end])
        else:
            if ctype == b"eXIf":
                orientation = read_orientation(data[pos + 8:end - 4])
            keyword = label(data[pos + 8:pos + 40]) if ctype in (b"tEXt", b"zTXt", b"iTXt") else ""
            removed.append(f"{ctype.decode('latin-1')} {keyword}".strip())
        pos = end
        if ctype == b"IEND":
            if pos < len(data):
                removed.append(f"{len(data) - pos} bytes after IEND")
            break
    return b"".join(out), removed


# ---------------------------------------------------------------- WebP

WEBP_KEEP = {b"VP8 ", b"VP8L", b"VP8X", b"ALPH", b"ANIM", b"ANMF"}
VP8X_ICC, VP8X_EXIF, VP8X_XMP = 0x20, 0x08, 0x04


def strip_webp(data, keep_icc):
    chunks, removed = [], []
    riff_end = min(len(data), 8 + struct.unpack("<I", data[4:8])[0])
    pos = 12
    while pos + 8 <= riff_end:
        size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        ctype = data[pos:pos + 4]
        end = pos + 8 + size + (size & 1)
        if ctype in WEBP_KEEP or (ctype == b"ICCP" and keep_icc):
            chunks.append(bytearray(data[pos:end]))
        else:
            removed.append(ctype.decode("latin-1").strip())
        pos = end
    if riff_end < len(data):
        removed.append(f"{len(data) - riff_end} bytes after RIFF")
    for chunk in chunks:
        if chunk[:4] == b"VP8X":
            chunk[8] &= ~(VP8X_EXIF | VP8X_XMP | (0 if keep_icc else VP8X_ICC)) & 0xFF
    body = b"WEBP" + b"".join(chunks)
    return b"RIFF" + struct.pack("<I", len(body)) + body, removed


# ---------------------------------------------------------------- GIF

GIF_KEEP_APPS = {b"NETSCAPE2.0", b"ANIMEXTS1.0"}  # animation loop count


def strip_gif(data, keep_icc):
    def blocks_end(p):
        while data[p]:
            p += data[p] + 1
        return p + 1

    pos = 13
    if data[10] & 0x80:
        pos += 3 << ((data[10] & 7) + 1)
    out, removed = [data[:pos]], []
    while True:
        kind = data[pos]
        if kind == 0x3B:
            out.append(b";")
            if pos + 1 < len(data):
                removed.append(f"{len(data) - pos - 1} bytes after trailer")
            break
        if kind == 0x21:
            ext, end = data[pos + 1], blocks_end(pos + 2)
            ident = data[pos + 3:pos + 14]
            if ext == 0xFE:
                removed.append("comment")
            elif ext == 0xFF and not (ident in GIF_KEEP_APPS or (ident == b"ICCRGBG1012" and keep_icc)):
                removed.append(f"application extension {label(ident)}")
            else:
                out.append(data[pos:end])
        elif kind == 0x2C:
            table = 3 << ((data[pos + 9] & 7) + 1) if data[pos + 9] & 0x80 else 0
            end = blocks_end(pos + 10 + table + 1)
            out.append(data[pos:end])
        else:
            raise ValueError(f"corrupt GIF block 0x{kind:02x}")
        pos = end
    return b"".join(out), removed


# ---------------------------------------------------------------- video

BENIGN_TAGS = {"major_brand", "minor_version", "compatible_brands", "handler_name",
               "vendor_id", "language", "duration", "encoder"}
HEIF_BRANDS = {b"heic", b"heix", b"heim", b"heis", b"mif1", b"msf1", b"avif", b"avis"}
QT_ATOMS = {b"ftyp", b"moov", b"mdat", b"wide", b"free", b"skip", b"pnot"}


def video_leftovers(path):
    """Metadata ffprobe still reports, plus top-level MP4 boxes that carry XMP/C2PA."""
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format_tags:stream_tags:chapters",
         "-of", "json", path], capture_output=True, text=True, check=True)
    info = json.loads(probe.stdout)
    found = [f"tag {k}={v!r}" for k, v in info.get("format", {}).get("tags", {}).items()
             if k.lower() not in BENIGN_TAGS]
    for i, stream in enumerate(info.get("streams", [])):
        found += [f"stream {i} tag {k}={v!r}" for k, v in stream.get("tags", {}).items()
                  if k.lower() not in BENIGN_TAGS]
    if info.get("chapters"):
        found.append(f"{len(info['chapters'])} chapters")
    with open(path, "rb") as f:
        if f.read(8)[4:8] in QT_ATOMS:
            f.seek(0)
            while header := f.read(8):
                if len(header) < 8:
                    break
                size, box = struct.unpack(">I4s", header)
                if size == 1:
                    size = struct.unpack(">Q", f.read(8))[0] - 8
                if box in (b"uuid", b"meta", b"udta", b"XMP_"):
                    found.append(f"top-level box {box.decode('latin-1')}")
                if size == 0:
                    break
                f.seek(size - 8, os.SEEK_CUR)
    return found


def strip_video(path, tmp):
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", path,
           "-map", "0:v", "-map", "0:a?", "-map", "0:s?", "-c", "copy",
           "-map_metadata", "-1", "-map_metadata:s", "-1", "-map_chapters", "-1",
           "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact"]
    if os.path.splitext(path)[1].lower() in (".mp4", ".m4v", ".mov"):
        cmd += ["-movflags", "+faststart"]
    result = subprocess.run(cmd + [tmp], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"ffmpeg failed: {result.stderr.strip()[-400:]}")


# ---------------------------------------------------------------- driver

IMAGE_STRIPPERS = {"JPEG": strip_jpeg, "PNG": strip_png, "WebP": strip_webp, "GIF": strip_gif}


def detect(head):
    if head[:3] == b"\xff\xd8\xff":
        return "JPEG"
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "WebP"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "GIF"
    if head[4:8] == b"ftyp" and head[8:12] in HEIF_BRANDS:
        return None  # HEIC/AVIF still images
    if head[4:8] in QT_ATOMS or head[:4] == b"\x1a\x45\xdf\xa3" or (
            head[:4] == b"RIFF" and head[8:12] == b"AVI "):
        return "video"
    return None


def replace_atomically(path, write):
    """Write the cleaned file next to the original, then swap it in."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)),
                               prefix=".strip-", suffix=os.path.splitext(path)[1])
    os.close(fd)
    try:
        write(tmp)
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def process(path, check, keep_icc):
    with open(path, "rb") as f:
        kind = detect(f.read(16))
    if kind is None:
        print(f"UNSUPPORTED {path}: convert to JPEG/PNG/WebP/GIF/MP4 first")
        return False
    if kind == "video":
        before = video_leftovers(path)
        if check:
            print(f"{'CLEAN' if not before else 'FOUND'} {path} [video] {'; '.join(before)}")
            return True
        replace_atomically(path, lambda tmp: strip_video(path, tmp))
        after = video_leftovers(path)
        print(f"{'STRIPPED' if not after else 'LEFTOVER'} {path} [video] "
              + (f"still has: {'; '.join(after)}" if after else f"removed: {'; '.join(before) or 'container metadata'}"))
        return not after
    with open(path, "rb") as f:
        data = f.read()
    stripper = IMAGE_STRIPPERS[kind]
    cleaned, removed = stripper(data, keep_icc)
    if check:  # an Orientation-only EXIF is what stripping leaves behind, so it counts as clean
        found = removed if cleaned != data else []
        print(f"{'FOUND' if found else 'CLEAN'} {path} [{kind}] {'; '.join(found)}")
        return True
    changed = cleaned != data
    if changed:
        def write(tmp):
            with open(tmp, "wb") as f:
                f.write(cleaned)
        replace_atomically(path, write)
    clean_again = stripper(cleaned, keep_icc)[0] == cleaned
    status = "STRIPPED" if changed else "CLEAN"
    print(f"{status if clean_again else 'LEFTOVER'} {path} [{kind}] {'; '.join(removed) if changed else ''}")
    return clean_again


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("files", nargs="+")
    parser.add_argument("--check", action="store_true", help="report only, change nothing")
    parser.add_argument("--keep-icc", action="store_true", help="keep embedded ICC colour profiles")
    args = parser.parse_args()
    ok = True
    for path in args.files:
        try:
            ok &= process(path, args.check, args.keep_icc)
        except (OSError, ValueError, IndexError, struct.error, subprocess.CalledProcessError) as exc:
            print(f"ERROR {path}: {exc}")
            ok = False
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
