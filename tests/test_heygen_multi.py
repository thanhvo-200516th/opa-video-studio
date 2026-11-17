#!/usr/bin/env python3
"""HeyGen nhiều góc (look): heygen_looks + render_heygen_aroll (bank, link, estimate, dry-run, resume). Không gọi mạng (mock).
Chạy: ~/.venvs/video-skills/bin/python tests/test_heygen_multi.py"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import heygen_looks as hl  # noqa: E402
import render_heygen_aroll as rh  # noqa: E402

LOOKS = [
    {"id": "L1", "name": "ban lam viec", "group_id": "G", "preview_image_url": "http://x/1.jpg", "supported_api_engines": ["avatar_iv"]},
    {"id": "L2", "name": "sofa", "group_id": "G", "preview_image_url": "http://x/2.jpg", "supported_api_engines": ["avatar_iii"]},
    {"id": "L3", "name": "cua so", "group_id": "G", "preview_image_url": "http://x/3.jpg", "supported_api_engines": ["avatar_iv", "avatar_iii"]},
]
BIG = b"0" * 20_000


def fake_poll(**kw):
    kw["out_path"].parent.mkdir(parents=True, exist_ok=True)
    kw["out_path"].write_bytes(BIG)
    return {"duration": 6}


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = rh.main(argv)
    return rc, buf.getvalue()


def fake_urlopen(pages):
    seen = []

    def _open(req, timeout=0):
        seen.append((req.full_url, req.get_method(), dict(req.header_items())))
        body = json.dumps(pages.pop(0)).encode()
        return mock.MagicMock(__enter__=lambda s: mock.MagicMock(read=lambda: body), __exit__=lambda *a: False)
    return _open, seen


def make_root(d: Path, n_videos=2, shots=3, bank=False) -> Path:
    for v in range(n_videos):
        sub = d / f"KB{v + 8:02d}_demo"
        sub.mkdir()
        items = [{"role_id": f"R{i}", "output_file": f"{v + 1:02d}_a-roll-{i + 1}.mp4", "tts_text": f"cau {i}", "duration_hint_sec": 6.0}
                 for i in range(shots)]
        if bank:
            items[0]["bank_id"] = "B1"
        (sub / "prompts_heygen_aroll.json").write_text(json.dumps(items), encoding="utf-8")
    return d


def test_list_mock_no_network_and_json():
    pages = [{"data": [LOOKS[0], LOOKS[1]], "has_more": True, "next_token": "t2"}, {"data": [LOOKS[2]], "has_more": False}]
    op, seen = fake_urlopen(pages)
    with mock.patch("urllib.request.urlopen", op):
        looks = hl.fetch_looks("KEY", group_id="G")
    assert [lk["id"] for lk in looks] == ["L1", "L2", "L3"] and looks[0]["engines"] == ["avatar_iv"]
    assert "group_id=G" in seen[0][0] and "token=t2" in seen[1][0] and seen[0][1] == "GET"
    with tempfile.TemporaryDirectory() as t:
        out = Path(t) / "looks.json"
        hl.save_looks(looks, out)
        assert "KEY" not in out.read_text() and [x["id"] for x in hl.load_looks(out)] == ["L1", "L2", "L3"]


def test_list_cli_needs_key_and_writes_file():
    with tempfile.TemporaryDirectory() as t:
        out = Path(t) / "looks.json"
        env = {k: v for k, v in os.environ.items() if k != "HEYGEN_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), contextlib.redirect_stdout(io.StringIO()):
            assert hl.main(["list", "--all", "--out", str(out)]) == 1 and not out.exists()
        kf = Path(t) / "k.txt"
        kf.write_text("HEYGEN_API_KEY=sk_test\n")
        op, seen = fake_urlopen([{"data": LOOKS}])
        with mock.patch("urllib.request.urlopen", op), contextlib.redirect_stdout(io.StringIO()) as o:
            assert hl.main(["list", "--all", "--key-file", str(kf), "--out", str(out)]) == 0
        assert "group_id" not in seen[0][0] and seen[0][2].get("X-api-key") == "sk_test"
        assert "sk_test" not in out.read_text() and "sk_test" not in o.getvalue()
        assert "L1" in o.getvalue() and "http://x/1.jpg" in o.getvalue() and "avatar_iv" in o.getvalue()


def test_pick_no_consecutive_and_angles():
    ids = ["L1", "L2", "L3", "L4", "L5"]
    for n in range(1, 9):
        for ang in (2, 3, 4):
            seq = hl.pick_for_video(n, ids, {}, ang)
            assert len(seq) == n and len(set(seq)) <= ang
            assert all(a != b for a, b in zip(seq, seq[1:])), seq
    assert len(set(hl.pick_for_video(6, ids, {}, 3))) == 3 and len(set(hl.pick_for_video(6, ids, {}, 9))) == 4   # kẹp 2-4
    assert len(set(hl.pick_for_video(6, ["a", "b"], {}, 4))) == 2                                                # ít look hơn góc


def test_pick_batch_balanced():
    ids = ["L1", "L2", "L3", "L4"]
    res = hl.pick_batch({f"KB{i:02d}": 3 for i in range(8)}, ids, 3)
    use = {i: sum(s.count(i) for s in res.values()) for i in ids}
    assert max(use.values()) - min(use.values()) <= 1, use
    assert all(all(a != b for a, b in zip(s, s[1:])) for s in res.values())
    assert hl.pick_batch({"a": 3}, ids, 3) == hl.pick_batch({"a": 3}, ids, 3)                                    # tất định


def test_choose_engine():
    iv, iii, unk = hl.normalize_look(LOOKS[0]), hl.normalize_look(LOOKS[1]), {"engines": []}
    assert hl.choose_engine(iv) is None and hl.choose_engine(iv, "avatar_iv") == "avatar_iv"
    assert hl.choose_engine(iii) == "avatar_iii" and hl.choose_engine(iii, "avatar_iv") == "avatar_iii"
    assert hl.choose_engine(unk) is None and hl.choose_engine(unk, "avatar_iv") == "avatar_iv"


def test_submit_payload():
    sent = {}
    with mock.patch.object(rh, "api_request", lambda m, p, k, b=None: sent.update(body=b, path=p) or {"data": {"video_id": "V"}}):
        rh.submit_heygen_video("k", "t", "x", "L3", "voice", "9:16", "1080p", "", engine="avatar_iii", background="#ffffff")
        assert sent["body"]["avatar_id"] == "L3" and sent["body"]["engine"] == "avatar_iii" and sent["body"]["background"] == "#ffffff"
        rh.submit_heygen_video("k", "t", "x", "L3", "voice", "9:16", "1080p", "")
        assert "engine" not in sent["body"] and "background" not in sent["body"]


def test_dry_run_per_shot_look_and_fallback():
    with tempfile.TemporaryDirectory() as t:
        root = make_root(Path(t), 1, 3)
        pj = next(root.glob("*/prompts_heygen_aroll.json"))
        items = json.loads(pj.read_text())
        items[1]["avatar_id"] = "LX"
        pj.write_text(json.dumps(items))
        with mock.patch.object(rh, "submit_heygen_video", side_effect=AssertionError("không được gọi")):
            rc, out = run([str(root), "--avatar-id", "DEF"])
        assert rc == 0 and "DRY-RUN" in out and "look: LX" in out and out.count("look: DEF") == 2


def test_auto_assign_and_engine():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        root = make_root(d / "r" if (d / "r").mkdir() is None else d, 2, 4)
        lj = d / "looks.json"
        lj.write_text(json.dumps({"looks": LOOKS}))
        calls = []
        with mock.patch.object(rh, "submit_heygen_video", lambda **kw: calls.append(kw) or "V"), \
                mock.patch.object(rh, "poll_and_download_heygen", fake_poll), \
                mock.patch.object(rh, "load_heygen_key", lambda kf=None: "K"):
            rc, _ = run([str(root), "--looks", str(lj), "--assign", "auto", "--yes", "--engine", "avatar_iv"])
        assert rc == 0 and len(calls) == 8
        for v in range(2):
            seq = [c["avatar_id"] for c in calls[v * 4:(v + 1) * 4]]
            assert all(a != b for a, b in zip(seq, seq[1:])), seq
        eng = {c["avatar_id"]: c["engine"] for c in calls}
        assert eng["L2"] == "avatar_iii" and eng["L1"] == "avatar_iv" and eng["L3"] == "avatar_iv"   # L2 không hỗ trợ iv
        # resume: chạy lại không gọi thêm
        again = []
        with mock.patch.object(rh, "submit_heygen_video", lambda **kw: again.append(kw) or "V"):
            rc, out = run([str(root), "--looks", str(lj), "--assign", "auto", "--yes"])
        assert rc == 0 and not again and "đã được render" in out
        with mock.patch.object(rh, "submit_heygen_video", lambda **kw: again.append(kw) or "V"), \
                mock.patch.object(rh, "poll_and_download_heygen", fake_poll), \
                mock.patch.object(rh, "load_heygen_key", lambda kf=None: "K"):
            run([str(root), "--yes", "--force", "--shot", "01_a-roll-1.mp4"])
        assert len(again) == 1


def test_assign_stable_on_resume():
    with tempfile.TemporaryDirectory() as t:
        root = make_root(Path(t), 2, 3)
        subs = rh.discover_subfolders(root)
        full = rh.auto_assign(subs, ["L1", "L2", "L3"], 3)
        (subs[0] / "01_a-roll-1.mp4").write_bytes(BIG)                  # đã render -> không đổi chia cho shot còn lại
        assert rh.auto_assign(subs, ["L1", "L2", "L3"], 3) == full


def test_yes_needs_key_and_never_writes_key():
    with tempfile.TemporaryDirectory() as t:
        root = make_root(Path(t), 1, 1)
        with mock.patch.dict(os.environ, {}, clear=True):
            rc, out = run([str(root), "--yes"])
        assert rc == 1 and "HEYGEN_API_KEY" in out
        kf = Path(t) / "key.txt"
        kf.write_text("sk_secret_value\n")
        with mock.patch.object(rh, "submit_heygen_video", lambda **kw: "V"), \
                mock.patch.object(rh, "poll_and_download_heygen", fake_poll):
            rc, out = run([str(root), "--yes", "--key-file", str(kf)])
        assert rc == 0 and "sk_secret_value" not in out
        assert all("sk_secret_value" not in p.read_text() for p in Path(t).rglob("*.json"))


def test_estimate():
    with tempfile.TemporaryDirectory() as t:
        root = make_root(Path(t), 2, 3)
        rc, out = run([str(root), "--estimate", "--avatar-id", "DEF"])
        assert rc == 0 and "36.0" in out and "Chưa có đơn giá" in out and "USD" not in out.replace("--usd-per-min", "")
        rc, out = run([str(root), "--estimate", "--avatar-id", "DEF", "--usd-per-min", "2.0"])
        assert "USD" in out and "1.20" in out                                                  # 36 s = 0.6 phút × 2.0


def test_bank_render_once_and_link():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        (d / "vids").mkdir()
        root = make_root(d / "vids", 2, 2, bank=True)
        bank = [{"bank_id": "B1", "text": "cau chung", "look_id": "L3", "used_in": ["KB08", "KB09"]},
                {"bank_id": "B2", "text": "cau khac", "look_id": "L1", "used_in": ["KB08"]}]
        bj = d / "bank.json"
        bj.write_text(json.dumps(bank))
        calls = []
        patches = (mock.patch.object(rh, "submit_heygen_video", lambda **kw: calls.append(kw) or "V"),
                   mock.patch.object(rh, "poll_and_download_heygen", fake_poll),
                   mock.patch.object(rh, "load_heygen_key", lambda kf=None: "K"))
        with patches[0], patches[1], patches[2]:
            rc, _ = run(["--bank", str(bj), "--yes"])
            assert rc == 0 and sorted(c["avatar_id"] for c in calls) == ["L1", "L3"]
            assert (d / "bank/B1.mp4").exists() and (d / "bank/B2.mp4").exists()
            run(["--bank", str(bj), "--yes"])
            assert len(calls) == 2                                                             # resume: không render lại
        rc, out = run(["--bank", str(bj)])
        assert rc == 0 and "đã được render" in out                                             # dry-run bank cũng skip
        msgs = rh.link_bank(bank, root, d / "bank")
        assert sum(m.startswith("linked") for m in msgs) == 2, msgs
        for sub in sorted(root.glob("KB*")):
            first = json.loads((sub / "prompts_heygen_aroll.json").read_text())[0]["output_file"]
            assert (sub / first).read_bytes() == BIG and not (sub / first).is_symlink()
        assert all(m.startswith("skip") for m in rh.link_bank(bank, root, d / "bank"))
        sub = sorted(root.glob("KB*"))[0]
        (sub / json.loads((sub / "prompts_heygen_aroll.json").read_text())[0]["output_file"]).unlink()
        assert rh.link_bank(bank, root, d / "bank", symlink=True)[0].startswith("linked")
        assert next(sub.glob("*_a-roll-1.mp4")).is_symlink()
        assert rh.main(["link", str(bj), str(root), "--force"]) == 0
        (d / "bank/B1.mp4").unlink()
        assert any(m.startswith("missing-file") for m in rh.link_bank(bank, root, d / "bank", force=True))
        bank[0]["used_in"] = ["KB99"]
        assert any(m.startswith("skip") and "used_in" in m for m in rh.link_bank(bank, root, d / "bank", force=True))


if __name__ == "__main__":
    fns = sorted((k, v) for k, v in globals().items() if k.startswith("test_"))
    for name, fn in fns:
        fn()
        print("ok", name)
    print(f"TẤT CẢ ĐẠT ({len(fns)} bài kiểm)")
