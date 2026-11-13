#!/usr/bin/env python3
"""
script-aroll-broll-analyzer: analyze_and_scaffold.py

Thực thi Bước 01 -> Bước 03 và tạo khung Thư mục con đánh số (Bước 06) cho từng kịch bản:
1. Chuẩn hóa văn bản lời thoại tiếng Việt cho TTS (HeyGen & ElevenLabs).
2. Phân tích file Spec Markdown (như SPEC-10-KICH-BAN-V4.md) hoặc file JSON kịch bản mới.
3. Đánh số thứ tự kép:
   - Thứ tự xuất hiện trên Timeline: 01_, 02_, 03_, 04_...
   - Thứ tự theo nhóm: a-roll-1, b-roll-1, a-roll-2, b-roll-2...
   - Định danh file chuẩn cho AI hiểu:
     * A-Roll (HeyGen):       <STT>_a-roll-<N>.mp4
     * B-Roll Hình (Muse/Veo): <STT>_b-roll-<M>.mp4   (Rule: KHÔNG VOICE, KHÔNG TEXT)
     * B-Roll Tiếng (Eleven):  <STT>_voice-b-roll-<M>.mp3
4. Tự động tạo Thư Mục Con cho từng kịch bản trong 1 Thư Mục Tổng, kèm:
   - 00_BANG_PHAN_CANH.md
   - 00_storyboard_manifest.json
   - prompts_heygen_aroll.json
   - prompts_elevenlabs_voice.json
   - prompts_muse_veo_broll.json
"""
import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from edit_rules import find_pain_in_text   # luật 2026-11-06: ưu tiên edit vào từ khoá NỖI ĐAU
except Exception:                                   # script chạy rời khỏi skill vẫn không vỡ
    def find_pain_in_text(text, extra=None):
        return []


# ============================================================================
# 1. BỘ CHUẨN HÓA SỐ & KÝ HIỆU TIẾNG VIỆT CHO VOICE AI (HEYGEN & ELEVENLABS)
# ============================================================================

DIGITS_VI = {
    0: "không",
    1: "một",
    2: "hai",
    3: "ba",
    4: "bốn",
    5: "năm",
    6: "sáu",
    7: "bảy",
    8: "tám",
    9: "chín",
}


def _read_two_digits(n: int) -> str:
    if n < 10:
        return DIGITS_VI[n]
    tens = n // 10
    unit = n % 10
    if tens == 1:
        prefix = "mười"
    else:
        prefix = f"{DIGITS_VI[tens]} mươi"

    if unit == 0:
        return prefix
    if unit == 1 and tens > 1:
        return f"{prefix} mốt"
    if unit == 4 and tens > 1:
        return f"{prefix} tư"
    if unit == 5:
        return f"{prefix} lăm"
    return f"{prefix} {DIGITS_VI[unit]}"


def _read_three_digits(n: int, full_hundred: bool = False) -> str:
    if n < 100 and not full_hundred:
        return _read_two_digits(n)
    hundreds = n // 100
    rem = n % 100
    res = f"{DIGITS_VI[hundreds]} trăm"
    if rem == 0:
        return res
    if rem < 10:
        return f"{res} lẻ {DIGITS_VI[rem]}"
    return f"{res} {_read_two_digits(rem)}"


def int_to_vietnamese(n: int) -> str:
    if n == 0:
        return "không"
    if n < 0:
        return f"âm {int_to_vietnamese(-n)}"
    if n < 1000:
        return _read_three_digits(n, full_hundred=False)

    units = ["", "nghìn", "triệu", "tỷ"]
    parts = []
    group_idx = 0
    temp = n
    groups = []
    while temp > 0:
        groups.append(temp % 1000)
        temp //= 1000

    for i in range(len(groups) - 1, -1, -1):
        val = groups[i]
        if val == 0:
            continue
        is_highest = (i == len(groups) - 1)
        chunk_str = _read_three_digits(val, full_hundred=not is_highest)
        unit_name = units[i] if i < len(units) else "tỷ"
        if unit_name:
            parts.append(f"{chunk_str} {unit_name}")
        else:
            parts.append(chunk_str)
    return " ".join(parts)


def normalize_vi_tts(text: str) -> str:
    """Chuẩn hóa câu thoại tiếng Việt để gửi API HeyGen & ElevenLabs không bị đọc sai."""
    s = text.strip()
    # Loại bỏ dấu * hoặc ngoặc kép bao ngoài không cần thiết
    s = re.sub(r'^[\*"“”]+|[\*"“”]+$', "", s).strip()

    # Thay thế một số cụm thông dụng trước
    replacements = [
        (r"\b24/7\b", "hai mươi tư trên bảy"),
        (r"\b30fps\b", "ba mươi khung hình trên giây"),
        (r"\b60fps\b", "sáu mươi khung hình trên giây"),
        (r"\b0đ\b", "không đồng"),
        (r"(\d+)\s*k\b", lambda m: f"{int_to_vietnamese(int(m.group(1)))} nghìn"),
        (r"(\d+)\s*tr\b", lambda m: f"{int_to_vietnamese(int(m.group(1)))} triệu"),
        (r"(\d+)%", lambda m: f"{int_to_vietnamese(int(m.group(1)))} phần trăm"),
    ]
    for pat, rep in replacements:
        s = re.sub(pat, rep, s, flags=re.IGNORECASE)

    # Số có dấu chấm phân cách hàng nghìn (VD: 50.000 -> 50000)
    s = re.sub(
        r"\b(\d{1,3}(?:\.\d{3})+)\b",
        lambda m: int_to_vietnamese(int(m.group(1).replace(".", ""))),
        s,
    )

    # Số thập phân có dấu phẩy hoặc chấm (VD: 1.5, 0,1)
    s = re.sub(
        r"\b(\d+)[\.,](\d+)\b",
        lambda m: f"{int_to_vietnamese(int(m.group(1)))} phẩy {int_to_vietnamese(int(m.group(2)))}",
        s,
    )

    # Các số nguyên độc lập còn lại (không nằm trong mã như V1, V10, B1, A1)
    s = re.sub(
        r"(?<![A-Za-z])(\d+)(?![A-Za-z])",
        lambda m: int_to_vietnamese(int(m.group(1))),
        s,
    )
    return re.sub(r"\s+", " ", s).strip()


def slugify_vi(text: str) -> str:
    """Chuyển tiêu đề tiếng Việt sang tên thư mục an toàn (ASCII)."""
    text = text.replace("đ", "d").replace("Đ", "D")
    norm = unicodedata.normalize("NFKD", text)
    ascii_str = "".join(c for c in norm if not unicodedata.combining(c))
    ascii_str = re.sub(r"[^A-Za-z0-9]+", "_", ascii_str).strip("_")
    return ascii_str[:55]


# ============================================================================
# 2. BỘ ĐÁNH SỐ THỨ TỰ KÉP & TẠO THƯ MỤC CON CHO TỪNG KỊCH BẢN
# ============================================================================

BROLL_STRICT_RULE_VI = (
    "RULE BẮT BUỘC: Chỉ tạo video hình ảnh minh họa / motion khớp lời thoại — "
    "TUYỆT ĐỐI KHÔNG TẠO VOICE (No Audio/Voice), KHÔNG TẠO TEXT / PHỤ ĐỀ / WATERMARK. "
    "TRUNG THỰC: cảnh phải minh họa đúng câu thoại; không logo / thương hiệu thật, không số liệu, "
    "không giao diện phần mềm bịa — số liệu chỉ hiện bằng chữ dựng từ kịch bản."
)
BROLL_STRICT_SUFFIX_EN = (
    "Pure visual footage/motion only, vertical 9:16 (1080x1920), photorealistic, "
    "NO text, NO subtitles, NO captions, NO UI text, NO watermark, muted / NO voice, "
    "NO logos or brand marks, NO numbers or charts with values, NO invented app / software interfaces."
)


def enrich_script_manifest(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Đánh số thứ tự kép cho từng phân đoạn trong 1 kịch bản:
      - seq_index: 1, 2, 3... (Thứ tự xuất hiện trên Timeline)
      - role_id:   a-roll-1, b-roll-1, a-roll-2, b-roll-2...
      - files:
          * A-Roll: <STT>_a-roll-<N>.mp4
          * B-Roll: <STT>_b-roll-<M>.mp4 + <STT>_voice-b-roll-<M>.mp3
    """
    aroll_count = 0
    broll_count = 0
    aroll_total_sec = 0.0
    broll_total_sec = 0.0
    enriched_segments = []

    raw_segments = script_data.get("segments", [])
    for idx, seg in enumerate(raw_segments, start=1):
        seq_prefix = f"{idx:02d}"
        seg_type = seg.get("type", "").strip().lower()
        if seg_type not in ("a-roll", "b-roll"):
            seg_type = "a-roll" if "a" in seg_type else "b-roll"

        dur = float(seg.get("duration_sec", 3.5))
        display_text = seg.get("display_text", "").strip()
        tts_text = seg.get("tts_text", "").strip() or normalize_vi_tts(display_text)

        if seg_type == "a-roll":
            aroll_count += 1
            aroll_total_sec += dur
            role_idx = aroll_count
            role_id = f"a-roll-{role_idx}"
            video_filename = f"{seq_prefix}_{role_id}.mp4"
            voice_filename = None
            script_setup = script_data.get("aroll_setup") or {}
            aroll_bg = (
                seg.get("aroll_background")
                or script_setup.get("background_name")
                or "BG-01: Góc Bàn Làm Việc Founder Trầm Ấm Tại Văn Phòng OPA (Ánh sáng Warm-Cool 2900K/5200K, xóa phông f/2.0, vùng tối 1/3 trên cho chữ)"
            )
            aroll_style = (
                seg.get("aroll_shooting_style")
                or script_setup.get("shooting_style")
                or "MCU ngang ngực (35mm/50mm Eye-level) · Sơ mi/Polo tối màu hoặc Blazer · Nhìn thẳng ống kính chân thành, điềm tĩnh, tốc độ 0.97x, tay đặt trong vùng ngực chuẩn HeyGen Avatar IV"
            )
            existing_routing = seg.get("api_routing") or {}
            is_live_shoot = (
                bool(seg.get("live_shoot"))
                or existing_routing.get("video_generator") == "live_shoot"
                or "QUAY THẬT" in (seg.get("visual_direction") or "").upper()
            )
            if is_live_shoot:
                api_info = {
                    "video_generator": "live_shoot",
                    "voice_generator": "live_camera_audio",
                    "aroll_background": aroll_bg,
                    "aroll_shooting_style": aroll_style,
                    "rule": "🎥 QUAY THẬT — không gọi HeyGen. File giao vẫn giữ tên <STT>_a-roll-<N>.mp4 (có cả hình + tiếng).",
                }
                for extra_k in ("shotlist_group", "live_action", "location", "props"):
                    if extra_k in existing_routing:
                        api_info[extra_k] = existing_routing[extra_k]
            else:
                api_info = {
                    "video_generator": "heygen_api",
                    "voice_generator": "heygen_embedded_voice",
                    "aroll_background": aroll_bg,
                    "aroll_shooting_style": aroll_style,
                    "rule": "Video A-Roll từ HeyGen đã bao gồm cả hình nhân vật nói và tiếng đọc khớp khẩu hình.",
                }
            broll_prompt = None
            visual_dir = seg.get("visual_direction") or "Avatar người nói nhìn thẳng ống kính, thần thái tự nhiên."
        else:
            broll_count += 1
            broll_total_sec += dur
            role_idx = broll_count
            role_id = f"b-roll-{role_idx}"
            video_filename = f"{seq_prefix}_{role_id}.mp4"
            voice_filename = f"{seq_prefix}_voice-{role_id}.mp3"
            raw_prompt = (seg.get("broll_prompt") or seg.get("visual_direction") or "").strip()
            broll_prompt = f"{raw_prompt} ({BROLL_STRICT_SUFFIX_EN})".strip()
            visual_dir = raw_prompt
            aroll_bg = None
            aroll_style = None
            api_info = {
                "video_generator": "muse_or_veo3_api",
                "voice_generator": "elevenlabs_api",
                "strict_broll_rule": BROLL_STRICT_RULE_VI,
                "no_voice_in_broll_video": True,
                "no_text_in_broll_video": True,
            }

        enriched_segments.append(
            {
                "seq_index": idx,
                "seq_prefix": seq_prefix,
                "type": seg_type,
                "role_index": role_idx,
                "role_id": role_id,
                "original_shot_code": seg.get("original_shot_code", role_id),
                "time_range": seg.get("time_range", ""),
                "duration_sec": round(dur, 2),
                "beat_name": seg.get("beat_name", ""),
                "display_text": display_text,
                "tts_text": tts_text,
                "visual_direction": visual_dir,
                "aroll_background": aroll_bg,
                "aroll_shooting_style": aroll_style,
                "broll_prompt": broll_prompt,
                "keywords": seg.get("keywords", []),
                "pain_keywords": find_pain_in_text(display_text, extra=seg.get("keywords", [])),
                "post_fx_note": seg.get("post_fx_note", ""),
                # tầng quyết định của đạo diễn (chốt ở khâu kịch bản, trước khi tốn credit) — chỉ chép nếu kịch bản có:
                # belief = người xem phải tin điều gì · element = key_word | proof_card | b_roll_shot | list_as_typography |
                # live_clip | caption_only · landing_word = từ chốt để hiệu ứng nổ · truth = REAL | ILLUSTRATIVE | SCHEMATIC
                **{k: seg[k] for k in ("belief", "element", "landing_word", "truth") if seg.get(k)},
                "files": {
                    "video_file": video_filename,
                    "voice_file": voice_filename,
                },
                "api_routing": api_info,
            }
        )

    total_sec = round(aroll_total_sec + broll_total_sec, 2)
    aroll_pct = round((aroll_total_sec / total_sec) * 100, 1) if total_sec > 0 else 0.0
    broll_pct = round(100.0 - aroll_pct, 1) if total_sec > 0 else 0.0

    # Tự động xác định chế độ tỷ lệ nếu chưa truyền vào
    ratio_mode = script_data.get("ratio_mode")
    if not ratio_mode:
        if aroll_pct >= 45.0:
            ratio_mode = "aroll_heavy (A-Roll nhiều, B-Roll ít)"
        elif aroll_pct <= 29.0:
            ratio_mode = "broll_heavy (A-Roll ít, B-Roll nhiều)"
        else:
            ratio_mode = "balanced_credit_saver (Cân bằng tối ưu Credit HeyGen)"

    # Tạo mô tả chuỗi lắp ráp tuần tự cho AI hiểu ngay
    sequence_chain = []
    for s in enriched_segments:
        if s["type"] == "a-roll":
            sequence_chain.append(f"[{s['seq_prefix']}] {s['role_id']} ({s['files']['video_file']})")
        else:
            sequence_chain.append(
                f"[{s['seq_prefix']}] {s['role_id']} ({s['files']['video_file']} + {s['files']['voice_file']})"
            )

    default_setup = script_data.get("aroll_setup") or {
        "setup_code": "BG-01",
        "background_name": "BG-01: Góc Bàn Làm Việc Founder Trầm Ấm Tại Văn Phòng OPA",
        "background_detail": "Bàn gỗ tối màu, hậu cảnh kệ sách + đèn ấm 2900K kết hợp mảng tường xám xanh trầm (xóa phông f/2.0, vùng 1/3 trên tối để đặt chữ tiêu đề @__dviet).",
        "wardrobe": "Sơ mi tối màu xắn tay hoặc Polo dệt kim + Blazer không cài cúc (Smart-Casual Founder tuổi 32).",
        "shooting_style": "Trung cận MCU (35mm/50mm Eye-level) · Nhìn thẳng ống kính chân thành, điềm tĩnh, tốc độ 0.97x · Không cười liên tục, cử động tay gọn trong vùng ngực chuẩn HeyGen Avatar IV.",
    }

    _sid = str(
        script_data.get("script_id")
        or script_data.get("id")
        or "KB01"
    ).strip()
    return {
        "script_id": _sid,
        "slug": script_data.get("slug") or f"{_sid}_Kich_Ban",
        "title": script_data.get("title", ""),
        "phase": script_data.get("phase", ""),
        "viral_direction": script_data.get("viral_direction", ""),
        "aspect_ratio": script_data.get("aspect_ratio", "9:16"),
        "resolution": script_data.get("resolution", "1080x1920"),
        "fps": script_data.get("fps", 30),
        "ratio_mode": ratio_mode,
        "aroll_setup": default_setup,
        "summary_metrics": {
            "total_segments": len(enriched_segments),
            "aroll_segments_count": aroll_count,
            "broll_segments_count": broll_count,
            "total_duration_sec": total_sec,
            "aroll_duration_sec": round(aroll_total_sec, 2),
            "broll_duration_sec": round(broll_total_sec, 2),
            "aroll_percentage": f"{aroll_pct}%",
            "broll_percentage": f"{broll_pct}%",
        },
        "ai_assembly_guide": {
            "instruction": (
                "Skill master-video-edit lắp ráp các phân đoạn theo đúng số thứ tự seq_prefix (01 -> 02 -> 03...). "
                "Với phân đoạn a-roll: đặt video_file (đã có cả hình + tiếng từ HeyGen) lên V1 + A1. "
                "Với phân đoạn b-roll: đặt video_file (hình câm từ Muse/Veo3) lên V1/V2 và đặt voice_file (tiếng từ ElevenLabs) xuống A1 khớp khít nhau."
            ),
            "ordered_chain": " ➔ ".join(sequence_chain),
        },
        "segments": enriched_segments,
    }


def write_subfolder_bundle(manifest: Dict[str, Any], out_root: Path) -> Path:
    """Ghi trọn bộ Thư mục con của 1 kịch bản vào Thư mục tổng."""
    subfolder = out_root / manifest["slug"]
    subfolder.mkdir(parents=True, exist_ok=True)

    # 1. Ghi 00_storyboard_manifest.json
    manifest_path = subfolder / "00_storyboard_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. Tách 3 file payload riêng cho 3 API (HeyGen, ElevenLabs, Muse/Veo3)
    heygen_payloads = []
    elevenlabs_payloads = []
    muse_veo_payloads = []

    for seg in manifest["segments"]:
        if seg["type"] == "a-roll":
            routing = seg.get("api_routing") or {}
            if routing.get("video_generator") == "live_shoot":
                continue
            heygen_payloads.append(
                {
                    "seq_index": seg["seq_index"],
                    "role_id": seg["role_id"],
                    "output_file": seg["files"]["video_file"],
                    "duration_hint_sec": seg["duration_sec"],
                    "tts_text": seg["tts_text"],
                    "display_text": seg["display_text"],
                    "visual_direction": seg["visual_direction"],
                    "aroll_background": seg.get("aroll_background"),
                    "aroll_shooting_style": seg.get("aroll_shooting_style"),
                }
            )
        else:
            elevenlabs_payloads.append(
                {
                    "seq_index": seg["seq_index"],
                    "role_id": seg["role_id"],
                    "output_file": seg["files"]["voice_file"],
                    "paired_broll_video": seg["files"]["video_file"],
                    "duration_hint_sec": seg["duration_sec"],
                    "tts_text": seg["tts_text"],
                    "display_text": seg["display_text"],
                }
            )
            muse_veo_payloads.append(
                {
                    "seq_index": seg["seq_index"],
                    "role_id": seg["role_id"],
                    "output_file": seg["files"]["video_file"],
                    "paired_voice_file": seg["files"]["voice_file"],
                    "duration_target_sec": seg["duration_sec"],
                    "prompt_vi": seg["visual_direction"],
                    "prompt_full": seg["broll_prompt"],
                    "rules": {
                        "no_voice": True,
                        "no_text": True,
                        "no_subtitles": True,
                        "aspect_ratio": manifest["aspect_ratio"],
                    },
                }
            )

    (subfolder / "prompts_heygen_aroll.json").write_text(
        json.dumps(heygen_payloads, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (subfolder / "prompts_elevenlabs_voice.json").write_text(
        json.dumps(elevenlabs_payloads, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (subfolder / "prompts_muse_veo_broll.json").write_text(
        json.dumps(muse_veo_payloads, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 3. Ghi 00_BANG_PHAN_CANH.md trực quan cho người và AI đọc
    m = manifest["summary_metrics"]
    asetup = manifest.get("aroll_setup") or {}
    md_lines = [
        f"# 🎬 BẢNG PHÂN CẢNH & ĐỊNH DANH FILE CHO AI — {manifest['script_id']}: {manifest['title']}",
        "",
        f"- **Thư mục con của kịch bản:** `{subfolder}`",
        f"- **Giai đoạn / Nhóm nội dung:** `{manifest.get('phase') or 'Chuẩn 10 Bước'}` · **Hướng kể chuyện:** `{manifest.get('viral_direction') or 'Thực chiến'}`",
        f"- **Chế độ phân bổ A-Roll / B-Roll:** `{manifest['ratio_mode']}`",
        f"- **Tổng thời lượng dự kiến:** `{m['total_duration_sec']}s` "
        f"(`{m['aroll_segments_count']} đoạn A-Roll = {m['aroll_duration_sec']}s ({m['aroll_percentage']})` + "
        f"`{m['broll_segments_count']} đoạn B-Roll = {m['broll_duration_sec']}s ({m['broll_percentage']})`)",
        f"- **Mạch ghép nối tiếp cho AI (`01 ➔ {m['total_segments']:02d}`):**",
        f"  `{manifest['ai_assembly_guide']['ordered_chain']}`",
        "",
        "## 🎥 Chỉ Dẫn Quay Phôi `A-Roll` (Background & Style Quay Cho Kịch Bản Này)",
        "",
        f"- **Mã Phôi & Bối cảnh (`Background`):** **{asetup.get('background_name', 'BG-01')}** — {asetup.get('background_detail', '')}",
        f"- **Trang phục (`Wardrobe`):** {asetup.get('wardrobe', '')}",
        f"- **Góc máy, Ánh sáng & Phong thái (`Shooting Style`):** {asetup.get('shooting_style', '')}",
        "",
        "---",
        "",
        "## 1. Bảng Phân Tách Chi Tiết (`A-Roll` / `B-Roll` / `Voice-off`)",
        "",
        "| Thứ tự Timeline | Phân loại & Đánh số (`a-roll` / `b-roll`) | Mốc giờ (`Độ dài`) | Câu thoại chuẩn hóa để tạo Voice (HeyGen / ElevenLabs) | Chỉ dẫn Hình ảnh / Background & Style `A-Roll` / Prompt `B-Roll` (KHÔNG VOICE, KHÔNG TEXT) | Tên File Đầu Ra Trong Thư Mục Con (Để AI Hiểu) | Ghi chú Hậu kỳ (`master-video-edit`) |",
        "| :---: | :--- | :---: | :--- | :--- | :--- | :--- |",
    ]

    for seg in manifest["segments"]:
        if seg["type"] == "a-roll":
            role_badge = f"**👤 `{seg['role_id']}`**<br>*(API HeyGen)*"
            files_cell = f"🎬 `{seg['files']['video_file']}`<br>*(Có sẵn Hình + Tiếng)*"
            bg_info = seg.get("aroll_background") or asetup.get("background_name", "")
            st_info = seg.get("aroll_shooting_style") or asetup.get("shooting_style", "")
            vis_raw = (
                f"{seg['visual_direction']}<br>"
                f"• **Background:** {bg_info}<br>"
                f"• **Style quay:** {st_info}"
            )
        else:
            role_badge = f"**🎞️ `{seg['role_id']}`**<br>*(MUSE/Veo3 + ElevenLabs)*"
            files_cell = (
                f"🎬 Hình: `{seg['files']['video_file']}`<br>"
                f"🔊 Tiếng: `{seg['files']['voice_file']}`"
            )
            vis_raw = f"{seg['visual_direction']}<br>• **Rule B-Roll:** `KHÔNG VOICE, KHÔNG TEXT`"
        time_cell = f"`{seg['time_range']}`<br>(`{seg['duration_sec']}s`)"
        tts_cell = f"*\"{seg['tts_text']}\"*"
        vis_cell = vis_raw.replace("|", "\\|")
        fx_cell = (seg["post_fx_note"] or "—").replace("|", "\\|")
        if seg.get("pain_keywords"):
            fx_cell += "<br>🔥 **Nỗi đau (ưu tiên chữ chính + zoom):** " + ", ".join(f"`{k}`" for k in seg["pain_keywords"])
        md_lines.append(
            f"| **`{seg['seq_prefix']}`** | {role_badge} | {time_cell} | {tts_cell} | {vis_cell} | {files_cell} | {fx_cell} |"
        )

    md_lines.extend(
        [
            "",
            "---",
            "",
            "## 2. Danh Sách File Cần Có Trong Thư Mục Con Này Trước Khi Chạy `master-video-edit`",
            "",
            "### A. Các đoạn Video `A-Roll` (Tạo từ API HeyGen — Đã có Hình + Tiếng):",
        ]
    )
    for item in heygen_payloads:
        md_lines.append(
            f"- `{item['output_file']}` (`{item['role_id']}` · `~{item['duration_hint_sec']}s`): *\"{item['tts_text']}\"*"
        )

    md_lines.extend(
        [
            "",
            "### B. Các file `Voice-off` cho cảnh `B-Roll` (Tạo từ API ElevenLabs):",
        ]
    )
    for item in elevenlabs_payloads:
        md_lines.append(
            f"- `{item['output_file']}` (Đi cặp với `{item['paired_broll_video']}` · `~{item['duration_hint_sec']}s`): *\"{item['tts_text']}\"*"
        )

    md_lines.extend(
        [
            "",
            "### C. Các đoạn Video trám cảnh `B-Roll` (Tạo từ API MUSE / MCP Veo 3 — KHÔNG VOICE, KHÔNG TEXT):",
        ]
    )
    for item in muse_veo_payloads:
        md_lines.append(
            f"- `{item['output_file']}` (Khớp độ dài với `{item['paired_voice_file']}` · `~{item['duration_target_sec']}s`): {item['prompt_vi']}"
        )

    (subfolder / "00_BANG_PHAN_CANH.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return subfolder


# ============================================================================
# 3. BỘ ĐỌC FILE SPEC MARKDOWN (NHƯ SPEC-10-KICH-BAN-V4.md)
# ============================================================================

def parse_spec_markdown(spec_path: Path) -> List[Dict[str, Any]]:
    """
    Đọc file đặc tả dạng Markdown (như SPEC-10-KICH-BAN-V4.md) và bóc tách toàn bộ
    các kịch bản cùng từng dòng phân cảnh trong bảng Markdown.
    """
    text = spec_path.read_text(encoding="utf-8")
    # Tìm các khối: ### KỊCH BẢN #01 (`mkq-01`): Tiêu đề
    header_pattern = re.compile(
        r"^###\s+KỊCH BẢN\s+#?(\d+)\s*(?:\(`([^`]+)`\))?\s*:\s*(.+)$",
        re.MULTILINE,
    )
    matches = list(header_pattern.finditer(text))
    scripts = []

    for i, m in enumerate(matches):
        kb_num = int(m.group(1))
        kb_code = f"KB{kb_num:02d}"
        title = m.group(3).strip()
        slug = f"{kb_code}_{slugify_vi(title)}"

        start_pos = m.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start_pos:end_pos]

        # Nếu trong block có dòng: - **Mã định danh & Thư mục con:** `XM01` ➔ `.../01_XM01_.../`
        id_slug_match = re.search(
            r"\*\*Mã định danh\s*&\s*Thư mục con:\*\*\s*`([^`]+)`\s*➔\s*`(?:[^`/]+/)?([^`/]+)/?`",
            block,
        )
        if id_slug_match:
            kb_code = id_slug_match.group(1).strip()
            slug = id_slug_match.group(2).strip()

        segments = []
        for line in block.splitlines():
            line_s = line.strip()
            if not line_s.startswith("|"):
                continue
            cols = [c.strip() for c in line_s.strip("|").split("|")]
            if len(cols) < 5:
                continue
            first_col = cols[0]
            # Kiểm tra xem cột đầu có chứa mã A1..An hoặc B1..Bn không
            code_match = re.search(r"`?([AB]\d+)`?", first_col)
            if not code_match:
                continue

            shot_code = code_match.group(1)
            time_col = cols[1]
            source_col = cols[2]
            dialogue_col = cols[3]
            visual_col = cols[4]
            fx_col = " | ".join(cols[5:]) if len(cols) > 5 else ""

            seg_type = "a-roll" if shot_code.upper().startswith("A") or "A-Roll" in source_col else "b-roll"
            is_live_shoot = "QUAY THẬT" in source_col.upper() or "QUAY THẬT" in visual_col.upper()

            # Tách time_range và duration_sec từ cột 2, VD: `00s – 02.5s` (`2.5s`)
            dur_match = re.search(r"\(`?([\d\.]+)\s*s`?\)", time_col)
            dur_sec = float(dur_match.group(1)) if dur_match else 3.5
            range_match = re.search(r"`([^`]+)`", time_col)
            time_range = range_match.group(1) if range_match else time_col

            clean_dialogue = re.sub(r'^[\*"“”]+|[\*"“”]+$', "", dialogue_col).strip()
            clean_dialogue = re.sub(r"^\.\.\.\s*", "", clean_dialogue).strip()

            segments.append(
                {
                    "original_shot_code": shot_code,
                    "type": seg_type,
                    "live_shoot": is_live_shoot,
                    "time_range": time_range,
                    "duration_sec": dur_sec,
                    "display_text": clean_dialogue,
                    "tts_text": normalize_vi_tts(clean_dialogue),
                    "visual_direction": visual_col,
                    "broll_prompt": visual_col if seg_type == "b-roll" else None,
                    "post_fx_note": fx_col,
                }
            )

        if segments:
            scripts.append(
                {
                    "script_id": kb_code,
                    "slug": slug,
                    "title": title,
                    "segments": segments,
                }
            )

    return scripts


# ============================================================================
# 4. KIỂM ĐỊNH THƯ MỤC TỔNG & THƯ MỤC CON (VALIDATE)
# ============================================================================

def validate_root_folder(root_dir: Path, check_media_exists: bool = False) -> int:
    if not root_dir.exists():
        print(f"[ERROR] Thư mục không tồn tại: {root_dir}")
        return 1

    manifests = sorted(root_dir.glob("*/00_storyboard_manifest.json"))
    if not manifests:
        print(f"[ERROR] Không tìm thấy thư mục con nào có 00_storyboard_manifest.json trong: {root_dir}")
        return 1

    errors = 0
    print(f"=== KIỂM ĐỊNH {len(manifests)} THƯ MỤC KỊCH BẢN TRONG: {root_dir} ===")
    for mp in manifests:
        sub = mp.parent
        data = json.loads(mp.read_text(encoding="utf-8"))
        segs = data.get("segments", [])
        aroll_n = sum(1 for s in segs if s.get("type") == "a-roll")
        broll_n = sum(1 for s in segs if s.get("type") == "b-roll")

        # Kiểm tra tính liên tục của seq_index
        seq_indices = [s.get("seq_index") for s in segs]
        if seq_indices != list(range(1, len(segs) + 1)):
            print(f"  [FAIL] {sub.name}: seq_index không liên tục: {seq_indices}")
            errors += 1
            continue

        # Kiểm tra các file JSON đi kèm
        for req_file in (
            "00_BANG_PHAN_CANH.md",
            "prompts_heygen_aroll.json",
            "prompts_elevenlabs_voice.json",
            "prompts_muse_veo_broll.json",
        ):
            if not (sub / req_file).exists():
                print(f"  [FAIL] {sub.name}: Thiếu file {req_file}")
                errors += 1

        if check_media_exists:
            missing_media = []
            for s in segs:
                vf = s["files"]["video_file"]
                af = s["files"]["voice_file"]
                if not (sub / vf).exists():
                    missing_media.append(vf)
                if af and not (sub / af).exists():
                    missing_media.append(af)
            if missing_media:
                print(f"  [WARN-MEDIA] {sub.name}: Chưa render {len(missing_media)} file media ({missing_media[:3]}...)")

        print(
            f"  [OK] {sub.name}: {len(segs)} phân đoạn "
            f"({aroll_n} A-Roll + {broll_n} B-Roll · Tỷ lệ {data['summary_metrics']['aroll_percentage']} : {data['summary_metrics']['broll_percentage']})"
        )

    if errors == 0:
        print("==> ĐẠT 100%: Tất cả thư mục con đã được đánh số và đóng gói chuẩn cho AI!")
        return 0
    print(f"==> CÓ {errors} LỖI CẦN SỬA!")
    return 1


def write_master_index(manifests: List[Dict[str, Any]], out_root: Path) -> Path:
    """Tạo file 00_DANH_MUC_TONG_KICH_BAN.md ở thư mục tổng."""
    index_path = out_root / "00_DANH_MUC_TONG_KICH_BAN.md"
    lines = [
        "# 📁 DANH MỤC TỔNG CÁC THƯ MỤC KỊCH BẢN (ĐÃ ĐÁNH SỐ CHO AI)",
        "",
        f"- **Thư mục tổng:** `{out_root}`",
        f"- **Tổng số kịch bản:** `{len(manifests)} kịch bản`",
        "- **Quy ước đánh số trong từng thư mục con để AI / Skill Edit hiểu ngay:**",
        "  - `01_a-roll-1.mp4`, `03_a-roll-2.mp4`...: Video người nói từ **API HeyGen** (đã có cả Hình + Tiếng).",
        "  - `02_b-roll-1.mp4`, `04_b-roll-2.mp4`...: Video trám cảnh từ **API MUSE / MCP Veo 3** (**Chỉ hình minh họa, KHÔNG VOICE, KHÔNG TEXT**).",
        "  - `02_voice-b-roll-1.mp3`, `04_voice-b-roll-2.mp3`...: File âm thanh `Voice-off` từ **API ElevenLabs** đi cặp 1-1 với video `B-Roll` cùng số thứ tự đầu.",
        "",
        "| Mã KB | Thư mục con của kịch bản | Tổng độ dài | Số đoạn `👤 A-Roll` | Số đoạn `🎞️ B-Roll (+ Voice)` | Tỷ lệ `A-Roll : B-Roll` | Bảng phân cảnh chi tiết |",
        "| :---: | :--- | :---: | :---: | :---: | :---: | :--- |",
    ]
    for m in manifests:
        sm = m["summary_metrics"]
        slug = m["slug"]
        lines.append(
            f"| **{m['script_id']}** | `{slug}/` | `{sm['total_duration_sec']}s` | "
            f"`{sm['aroll_segments_count']} đoạn` (`{sm['aroll_duration_sec']}s`) | "
            f"`{sm['broll_segments_count']} đoạn` (`{sm['broll_duration_sec']}s`) | "
            f"**{sm['aroll_percentage']} : {sm['broll_percentage']}** | "
            f"[00_BANG_PHAN_CANH.md](./{slug}/00_BANG_PHAN_CANH.md) |"
        )
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index_path


def write_analysis_report(manifests: List[Dict[str, Any]], out_root: Path) -> Path:
    """
    Tạo Báo cáo tổng hợp 00_BAO_CAO_PHAN_TICH_AROLL_BROLL.md tích hợp trực tiếp
    với quy trình 10 bước của skill master-video-edit.
    """
    report_path = out_root / "00_BAO_CAO_PHAN_TICH_AROLL_BROLL.md"
    total_kb = len(manifests)
    total_segs = sum(m["summary_metrics"]["total_segments"] for m in manifests)
    total_aroll_segs = sum(m["summary_metrics"]["aroll_segments_count"] for m in manifests)
    total_broll_segs = sum(m["summary_metrics"]["broll_segments_count"] for m in manifests)
    total_dur = round(sum(m["summary_metrics"]["total_duration_sec"] for m in manifests), 2)
    total_aroll_dur = round(sum(m["summary_metrics"]["aroll_duration_sec"] for m in manifests), 2)
    total_broll_dur = round(sum(m["summary_metrics"]["broll_duration_sec"] for m in manifests), 2)
    avg_aroll_pct = round((total_aroll_dur / total_dur) * 100, 1) if total_dur > 0 else 0.0
    avg_broll_pct = round(100.0 - avg_aroll_pct, 1) if total_dur > 0 else 0.0

    # Kiểm tra xem có file media nào đã được render vào thư mục con chưa
    rendered_aroll = 0
    rendered_broll = 0
    rendered_voice = 0
    for m in manifests:
        sub = out_root / m["slug"]
        for s in m["segments"]:
            vf = sub / s["files"]["video_file"]
            af = (sub / s["files"]["voice_file"]) if s["files"]["voice_file"] else None
            if s["type"] == "a-roll" and vf.exists():
                rendered_aroll += 1
            elif s["type"] == "b-roll":
                if vf.exists():
                    rendered_broll += 1
                if af and af.exists():
                    rendered_voice += 1

    # Thống kê theo nhóm Phôi Background A-Roll
    bg_groups: Dict[str, List[str]] = {}
    bg_meta: Dict[str, Dict[str, str]] = {}
    for m in manifests:
        asetup = m.get("aroll_setup") or {}
        scode = asetup.get("setup_code", "BG-01")
        bg_groups.setdefault(scode, []).append(m["script_id"])
        if scode not in bg_meta:
            bg_meta[scode] = asetup

    lines = [
        "# 📊 BÁO CÁO PHÂN TÍCH KỊCH BẢN (`A-ROLL` & `B-ROLL`), BACKGROUND / STYLE QUAY `A-ROLL` & LỘ TRÌNH DỰNG `MASTER-VIDEO-EDIT`",
        "",
        "## 1. Tổng Quan Lô Kịch Bản Đã Phân Tích",
        "",
        f"- **Thư mục tổng chứa các kịch bản:** `{out_root}`",
        f"- **Tổng số kịch bản đã phân tích:** `{total_kb} kịch bản` (`{total_segs} phân cảnh`)",
        f"- **Tổng thời lượng toàn lô:** `{total_dur}s` (`~{round(total_dur / 60, 1)} phút`)",
        f"- **Phân bổ thời lượng `A-Roll` vs `B-Roll` toàn lô:**",
        f"  - **👤 `A-Roll` (API HeyGen — Hình + Tiếng):** `{total_aroll_segs} phân đoạn` · `{total_aroll_dur}s` (**`{avg_aroll_pct}%`**)",
        f"  - **🎞️ `B-Roll` (API MUSE / MCP Veo 3 — Chỉ Hình, KHÔNG VOICE, KHÔNG TEXT):** `{total_broll_segs} phân đoạn` · `{total_broll_dur}s` (**`{avg_broll_pct}%`**)",
        f"  - **🔊 `Voice-off B-Roll` (API ElevenLabs — Đi cặp 1-1 với B-Roll):** `{total_broll_segs} file âm thanh` · `{total_broll_dur}s`",
        f"- **Tỷ lệ tiết kiệm Credit HeyGen ước tính:** **`~{avg_broll_pct}%`** *(nhờ chuyển phần giải thích/chứng minh sang B-Roll + Voice-off ElevenLabs)*",
        "",
        "---",
        "",
        "## 2. Hệ Thống Phôi Background & Style Quay `A-Roll` Đề Xuất Cho Toàn Lô",
        "",
        "| Mã Phôi | Tên Background & Thiết Kế Bối Cảnh / Ánh Sáng | Trang Phục (`Wardrobe`) | Style Quay, Góc Máy & Diễn Xuất (Chuẩn HeyGen Avatar IV) | Các Kịch Bản Áp Dụng |",
        "| :---: | :--- | :--- | :--- | :--- |",
    ]

    for scode in sorted(bg_groups.keys()):
        meta = bg_meta[scode]
        kbs_str = ", ".join(f"`{k}`" for k in bg_groups[scode])
        lines.append(
            f"| **`{scode}`** | **{meta.get('background_name', scode)}**<br>{meta.get('background_detail', '')} | "
            f"{meta.get('wardrobe', '')} | {meta.get('shooting_style', '')} | "
            f"**{len(bg_groups[scode])} bài:** {kbs_str} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 3. Bảng Phân Tích Chi Tiết `A-Roll` / `B-Roll`, Background Quay & Chuỗi Đánh Số Từng Kịch Bản",
            "",
            "| Mã KB | Tiêu đề Kịch bản | Chế độ Tỷ lệ (`ratio_mode`) | Phôi Background & Style Quay `A-Roll` | Thời lượng | `👤 A-Roll` : `🎞️ B-Roll` | Mạch ghép nối tiếp (`01 ➔ N`) cho AI | Hồ sơ Thư mục con |",
            "| :---: | :--- | :--- | :--- | :---: | :---: | :--- | :--- |",
        ]
    )

    for m in manifests:
        sm = m["summary_metrics"]
        slug = m["slug"]
        asetup = m.get("aroll_setup") or {}
        bg_cell = f"**`{asetup.get('setup_code', 'BG-01')}`**: {asetup.get('background_name', '')}<br>*(Trang phục: {asetup.get('wardrobe', '')})*"
        short_chain = " ➔ ".join(
            f"`{s['seq_prefix']}_{s['role_id']}`" for s in m["segments"]
        )
        lines.append(
            f"| **{m['script_id']}** | {m['title']} | `{m['ratio_mode']}` | {bg_cell} | `{sm['total_duration_sec']}s` | "
            f"`{sm['aroll_segments_count']}A` (`{sm['aroll_percentage']}`) : `{sm['broll_segments_count']}B` (`{sm['broll_percentage']}`) | "
            f"{short_chain} | "
            f"[Bảng phân cảnh](./{slug}/00_BANG_PHAN_CANH.md) · [Manifest JSON](./{slug}/00_storyboard_manifest.json) |"
        )

    step4_status = (
        f"✅ Đã có `{rendered_aroll}/{total_aroll_segs}` A-Roll & `{rendered_broll}/{total_broll_segs}` B-Roll"
        if (rendered_aroll == total_aroll_segs and rendered_broll == total_broll_segs and total_segs > 0)
        else f"⏳ Đã xuất Payload JSON (`{rendered_aroll}/{total_aroll_segs}` A-Roll, `{rendered_broll}/{total_broll_segs}` B-Roll đã render)"
    )
    step5_status = (
        f"✅ Đã có `{rendered_voice}/{total_broll_segs}` file Voice-off"
        if (rendered_voice == total_broll_segs and total_broll_segs > 0)
        else f"⏳ Đã xuất Payload JSON (`{rendered_voice}/{total_broll_segs}` file Voice-off đã render)"
    )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 3. Bảng Theo Dõi Quy Trình Dựng Video Tự Động 10 Bước (`master-video-edit`)",
            "",
            "| Bước | Tên Bước Trong Quy Trình Chuẩn | Công Cụ / Skill Đảm Nhận | File Đầu Ra Trong Thư Mục Con | Trạng Thái |",
            "| :---: | :--- | :--- | :--- | :--- |",
            "| **01** | **Nhận Brief & Kịch bản** | `master-video-edit` (`Bước 1 — Brief`) | Đặc tả đầu vào / `input_scripts.json` | ✅ Hoàn tất |",
            "| **02** | **Phân tích kịch bản (`A-Roll` / `B-Roll` linh hoạt)** | `scripts/analyze_and_scaffold.py` | `00_storyboard_manifest.json`, `00_BANG_PHAN_CANH.md` | ✅ Hoàn tất |",
            "| **03** | **Tách lời thoại tạo Voice (`tts_text`) & Viết Prompt B-Roll (`no_voice`, `no_text`)** | `scripts/analyze_and_scaffold.py` | `prompts_heygen_aroll.json`, `prompts_elevenlabs_voice.json`, `prompts_muse_veo_broll.json` | ✅ Hoàn tất |",
            f"| **04** | **Tạo Video `A-Roll` (HeyGen) & Video `B-Roll` câm (MUSE / Veo 3)** | API HeyGen + `scripts/muse_gen.py` (hoặc MCP Veo 3) | `<STT>_a-roll-<N>.mp4`, `<STT>_b-roll-<M>.mp4` | {step4_status} |",
            f"| **05** | **Tạo `Voice-off` cho các cảnh `B-Roll` (ElevenLabs)** | API ElevenLabs (`audio-jingle` / REST API) | `<STT>_voice-b-roll-<M>.mp3` | {step5_status} |",
            "| **06** | **Đóng gói vào Thư mục con đánh số thứ tự kép (`01_`, `02_`, `03_`...)** | `scripts/analyze_and_scaffold.py validate` | `<Thư_Mục_Tổng>/<KBxx_Slug>/` | ✅ Đã đóng gói khung chuẩn 100% |",
            "| **07** | **Đưa Thư mục con vào `master-video-edit` để chuẩn bị Timeline** | `master-video-edit` (`silence_cut.py`, `build_kit.py`, `text_fx.py`) | `work/build_spec.py`, `OUT.craft.json` | ⏭️ Sẵn sàng khi có đủ file `.mp4`/`.mp3` |",
            "| **08** | **Dựng tự động đa rãnh (`V1–V6`, `A1–A4`: Chữ `@__dviet`, Chuyển cảnh, SFX, BGM)** | `scripts/apps/craft-handoff/tools/fc_build.py` + `limit_master.py` + `audit_sfx.py` | `<KBxx>.fcproj` / `.prproj` | ⏭️ Sẵn sàng chạy tự động |",
            "| **09** | **Kiểm định QA khung hình & âm thanh (`-14 LUFS`, `TP <= -1.5 dBTP`)** | `scripts/qa_frames.py`, `scripts/qa_audio.py` | Báo cáo QA + mở cửa sổ Project | ⏭️ Chờ sau Bước 08 |",
            "| **10** | **Người Duyệt & Quyết định Xuất File Cuối (Luật số 1: Không tự xuất MP4)** | Người dùng duyệt trực tiếp trên Timeline | Xuất MP4 khi được lệnh + `strip-media-metadata` | ⏭️ Chờ người dùng duyệt |",
            "",
            "---",
            "",
            "## 4. Lệnh Thực Thi Nhanh Trong `master-video-edit`",
            "",
            "```bash",
            "# 1. Kiểm tra lại toàn bộ cấu trúc thư mục con & tiến độ render media:",
            f"python3 scripts/analyze_and_scaffold.py validate \"{out_root}\" --check-media",
            "",
            "# 2. Tạo nhanh B-Roll câm (không voice, không text) bằng Muse local cho 1 phân cảnh:",
            "python3 scripts/muse_gen.py video \"<prompt_full>\" --size 9:16 --seconds 5 -o 02_b-roll-1.mp4",
            "```",
        ]
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


# ============================================================================
# 5. CLI ENTRYPOINT
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phân tích kịch bản A-Roll / B-Roll & tạo Thư mục con đánh số chuẩn cho AI."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_spec = sub.add_parser("from-spec", help="Phân tích từ file Spec Markdown (VD: SPEC-10-KICH-BAN-V4.md)")
    p_spec.add_argument("spec_file", type=Path, help="Đường dẫn file .md đặc tả kịch bản")
    p_spec.add_argument("--out-dir", type=Path, required=True, help="Thư mục tổng để tạo các thư mục con")
    p_spec.add_argument("--filter-id", type=str, default=None, help="Chỉ chạy 1 mã kịch bản (VD: KB01, KB10)")

    p_json = sub.add_parser("from-json", help="Phân tích từ file JSON kịch bản đã bóc tách")
    p_json.add_argument("json_file", type=Path, help="Đường dẫn file .json")
    p_json.add_argument("--out-dir", type=Path, required=True, help="Thư mục tổng để tạo các thư mục con")

    p_tts = sub.add_parser("normalize-tts", help="Chuẩn hóa nhanh câu thoại tiếng Việt sang dạng chữ cho TTS")
    p_tts.add_argument("text", type=str, help="Câu thoại cần chuẩn hóa")

    p_val = sub.add_parser("validate", help="Kiểm tra cấu trúc Thư mục tổng và các Thư mục con")
    p_val.add_argument("root_dir", type=Path, help="Đường dẫn Thư mục tổng")
    p_val.add_argument("--check-media", action="store_true", help="Kiểm tra cả sự tồn tại của file .mp4/.mp3")

    p_rep = sub.add_parser("report", help="Xuất lại Báo cáo phân tích A-Roll / B-Roll & tiến độ 10 bước từ Thư mục tổng")
    p_rep.add_argument("root_dir", type=Path, help="Đường dẫn Thư mục tổng")

    p_aroll = sub.add_parser("render-aroll", help="Gọi API HeyGen tạo video A-Roll từ prompts_heygen_aroll.json")
    p_aroll.add_argument("target_dir", type=Path, help="Thư mục con kịch bản hoặc Thư mục tổng")
    p_aroll.add_argument("--filter-id", type=str, default=None, help="Lọc theo mã kịch bản (VD: XM01, KB10)")
    p_aroll.add_argument("--shot", type=str, default=None, help="Chỉ chạy 1 shot (VD: a-roll-2)")
    p_aroll.add_argument("--avatar-id", type=str, default=None, help="Ghi đè HeyGen Avatar ID")
    p_aroll.add_argument("--voice-id", type=str, default=None, help="Ghi đè HeyGen Voice ID")
    p_aroll.add_argument("--resolution", type=str, default="1080p", choices=["720p", "1080p"])
    p_aroll.add_argument("--force", action="store_true", help="Render đè file .mp4 đã tồn tại")
    p_aroll.add_argument("--yes", action="store_true", help="Xác nhận gọi API HeyGen thật (bỏ cờ này sẽ chạy DRY-RUN)")

    p_broll = sub.add_parser("render-broll", help="Gọi API Muse tạo video B-Roll câm từ prompts_muse_veo_broll.json")
    p_broll.add_argument("target_dir", type=Path, help="Thư mục con kịch bản hoặc Thư mục tổng")
    p_broll.add_argument("--filter-id", type=str, default=None, help="Lọc theo mã kịch bản (VD: XM01, KB10)")
    p_broll.add_argument("--shot", type=str, default=None, help="Chỉ chạy 1 shot (VD: b-roll-1)")
    p_broll.add_argument("--mode", type=str, default="image-to-video", choices=["image-to-video", "direct-video"])
    p_broll.add_argument("--force", action="store_true", help="Render đè file .mp4 đã tồn tại")
    p_broll.add_argument("--dry-run", action="store_true", help="Chỉ xem trước danh sách B-Roll, không gọi API")

    # render-all (chạy liền A-roll rồi B-roll, không điểm dừng kiểm) đã bỏ ở opa-video-studio vì là chuỗi pipeline.
    # Chạy render-aroll rồi render-broll riêng từng bước (SKILL.md mục 2).

    args = parser.parse_args()
    scripts_dir = Path(__file__).resolve().parent

    if args.cmd == "render-aroll":
        cmd_list = [sys.executable, str(scripts_dir / "render_heygen_aroll.py"), str(args.target_dir)]
        if args.filter_id:
            cmd_list += ["--filter-id", args.filter_id]
        if args.shot:
            cmd_list += ["--shot", args.shot]
        if args.avatar_id:
            cmd_list += ["--avatar-id", args.avatar_id]
        if args.voice_id:
            cmd_list += ["--voice-id", args.voice_id]
        if args.resolution:
            cmd_list += ["--resolution", args.resolution]
        if args.force:
            cmd_list.append("--force")
        if args.yes:
            cmd_list.append("--yes")
        return subprocess.run(cmd_list).returncode

    if args.cmd == "render-broll":
        cmd_list = [
            sys.executable,
            str(scripts_dir / "render_muse_broll.py"),
            str(args.target_dir),
            "--mode",
            args.mode,
        ]
        if args.filter_id:
            cmd_list += ["--filter-id", args.filter_id]
        if args.shot:
            cmd_list += ["--shot", args.shot]
        if args.force:
            cmd_list.append("--force")
        if args.dry_run:
            cmd_list.append("--dry-run")
        return subprocess.run(cmd_list).returncode

    if args.cmd == "normalize-tts":
        print(normalize_vi_tts(args.text))
        return 0

    if args.cmd == "validate":
        return validate_root_folder(args.root_dir, check_media_exists=args.check_media)

    if args.cmd == "report":
        manifests = [
            json.loads(mp.read_text(encoding="utf-8"))
            for mp in sorted(args.root_dir.glob("*/00_storyboard_manifest.json"))
        ]
        if not manifests:
            print(f"[ERROR] Không tìm thấy 00_storyboard_manifest.json trong: {args.root_dir}")
            return 1
        idx_file = write_master_index(manifests, args.root_dir)
        rep_file = write_analysis_report(manifests, args.root_dir)
        print(f"[MASTER INDEX] {idx_file}")
        print(f"[ANALYSIS REPORT] {rep_file}")
        return 0

    out_root: Path = args.out_dir
    out_root.mkdir(parents=True, exist_ok=True)

    raw_scripts: List[Dict[str, Any]] = []
    if args.cmd == "from-spec":
        raw_scripts = parse_spec_markdown(args.spec_file)
        if args.filter_id:
            fid = args.filter_id.strip().upper()
            raw_scripts = [s for s in raw_scripts if s["script_id"].upper() == fid]
    elif args.cmd == "from-json":
        payload = json.loads(args.json_file.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and "scripts" in payload:
            raw_scripts = payload["scripts"]
        elif isinstance(payload, list):
            raw_scripts = payload
        else:
            raw_scripts = [payload]

    if not raw_scripts:
        print("[ERROR] Không tìm thấy kịch bản nào trong đầu vào!")
        return 1

    all_manifests = []
    for raw_s in raw_scripts:
        manifest = enrich_script_manifest(raw_s)
        sub_path = write_subfolder_bundle(manifest, out_root)
        all_manifests.append(manifest)
        sm = manifest["summary_metrics"]
        print(
            f"[CREATED] {sub_path.name} -> {sm['total_segments']} phân đoạn "
            f"({sm['aroll_segments_count']} a-roll + {sm['broll_segments_count']} b-roll)"
        )

    idx_file = write_master_index(all_manifests, out_root)
    rep_file = write_analysis_report(all_manifests, out_root)
    print(f"[MASTER INDEX] {idx_file}")
    print(f"[ANALYSIS REPORT] {rep_file}")
    return validate_root_folder(out_root)


if __name__ == "__main__":
    sys.exit(main())
