import os
import csv
import json
import subprocess

SFX_ROOT = r"/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/sfx"
CSV_PATH = r"/media/vmiz/Over Powers/SaoLuu_D_20261028_132523/Vibe Coding/Motion Claude/OPA-Motion-graphic-mascot/ae/opa-agent/audio/kho_sfx_do.csv"
OUT_WAV_DIR = r"/media/vmiz/Over Powers/video AE/template intro/video edit teamplate/OPA_T5_Assets/SFX_Pro"
OUT_JSON_PATH = os.path.join(OUT_WAV_DIR, "resolved_sfx_cues.json")

os.makedirs(OUT_WAV_DIR, exist_ok=True)

csv_metrics = {}
with open(CSV_PATH, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        csv_metrics[r["file"].replace("\\", "/")] = {
            "dur": float(r["dur"]),
            "peak_s": float(r["peak_s"]),
            "tp_dbtp": float(r["tp_dbtp"]),
            "m_max": float(r["m_max"]),
            "centroid": float(r["centroid"]),
        }

SCENE_STARTS = {
    "01_Scene": 0.000,
    "02_Scene": 3.0333,
    "03_Scene": 6.4333,
    "04_Scene": 9.1333,
    "05_Scene": 12.1333,
    "06_Scene": 15.200,
    "07_Scene": 26.900,
    "08_Scene": 31.3667,
    "09_Scene": 34.1333,
    "10_Scene": 38.4667,
    "11_Scene": 42.700,
    "12_Scene": 47.4667,
    "13_Scene": 50.700,
}

# 78 High-Tech Professional SaaS Cues (Apple / Linear / Stripe style)
# Using uisfx-themes: studio, minimal, glass, scifi, soft, cinematic, zen
# AE Audio Levels (gain_db) strictly calibrated between -6.0 dB and -9.5 dB (-5 to -10 dB target)
CUES = [
    # --- 01_Scene (0.00s - 3.07s): Opening Hook ---
    ("01_Scene", 0.04, "impact", "S01 Cinematic Wake Pulse", "packs/uisfx-themes/cinematic/wake.ogg", -6.5, "Xung trầm ấm mở màn đồng bộ Color Flash (f1)"),
    ("01_Scene", 0.22, "whoosh", "S01 Studio Expand Reveal", "packs/uisfx-themes/studio/expand.ogg", -7.5, "Chữ 'Hàng trăm khách nhắn tin mỗi ngày' mở ra mượt mà"),
    ("01_Scene", 0.56, "ui", "S01 Glass Focus 'Mỏ vàng doanh thu'", "packs/uisfx-themes/glass/focus.ogg", -8.5, "Điểm nhấn tinh tế vào cụm 'là mỏ vàng doanh thu' (f17)"),
    ("01_Scene", 2.95, "riser", "S01 Soft Swipe Transition", "packs/uisfx-themes/soft/swipe.ogg", -8.0, "Lướt nhẹ chuẩn bị mở mạng lưới đa kênh Scene 02"),

    # --- 02_Scene (3.03s - 6.97s): Multi-Channel Customer Hub ---
    ("02_Scene", 3.08, "whoosh", "S02 Cinematic Hub Expand", "packs/uisfx-themes/cinematic/expand.ogg", -6.5, "Camera zoom-out bước 1 mở tâm OPA Hub (f92)"),
    ("02_Scene", 3.22, "scifi", "S02 SciFi Network Connecting", "packs/uisfx-themes/scifi/connecting.ogg", -9.0, "Đường mạch kết nối đa kênh tỏa ra từ tâm (02_Scene_Lines)"),
    ("02_Scene", 3.36, "pop", "S02 Studio Focus Inner Avatar 1", "packs/uisfx-themes/studio/focus.ogg", -9.0, "Chân dung khách vòng trong xuất hiện nhịp 1 (f101)"),
    ("02_Scene", 3.50, "pop", "S02 Studio Select Inner Avatar 2", "packs/uisfx-themes/studio/select.ogg", -9.0, "Chân dung khách vòng trong xuất hiện nhịp 2 (f105)"),
    ("02_Scene", 3.65, "ui", "S02 Minimal Progress Inner Icon 02", "packs/uisfx-themes/minimal/progress-step.ogg", -9.5, "Icon_02 nảy nhẹ tại đỉnh overshoot (f109)"),
    ("02_Scene", 4.00, "ui", "S02 Soft Select Inner Icon 04", "packs/uisfx-themes/soft/select.ogg", -9.0, "Icon_04 nảy nhẹ tại đỉnh overshoot (f120)"),
    ("02_Scene", 4.25, "ui", "S02 Zen Focus Inner Icons 03-01", "packs/uisfx-themes/zen/focus.ogg", -9.5, "Cặp Icon_03 & Icon_01 hoàn tất vòng trong (f128)"),
    ("02_Scene", 4.65, "whoosh", "S02 Glass Expand Outer Ring", "packs/uisfx-themes/glass/expand.ogg", -7.0, "Camera zoom-out bước 2 mở rộng toàn mạng lưới (f140)"),
    ("02_Scene", 5.00, "pop", "S02 Soft Focus Outer Avatars 1", "packs/uisfx-themes/soft/focus.ogg", -9.5, "Nhóm chân dung vòng ngoài xuất hiện nhịp 1 (f150)"),
    ("02_Scene", 5.36, "ui", "S02 Studio Connect Outer Icon 05", "packs/uisfx-themes/studio/connect.ogg", -8.5, "Icon_05 kết nối vào mạng lưới vòng ngoài (f161)"),
    ("02_Scene", 5.58, "ui", "S02 Minimal Select Outer Icon 06", "packs/uisfx-themes/minimal/select.ogg", -9.0, "Icon_06 & 07_Person khép hoàn chỉnh sơ đồ (f167)"),

    # --- 03_Scene (6.43s - 9.17s): Pain Point 1 (5-Minute Delay) ---
    ("03_Scene", 6.45, "whoosh", "S03 Cinematic Swipe Cut", "packs/uisfx-themes/cinematic/swipe.ogg", -7.0, "Chuyển cảnh mượt sang vấn đề trả lời chậm (f193)"),
    ("03_Scene", 6.68, "ui", "S03 Studio Focus Text Line 1", "packs/uisfx-themes/studio/focus.ogg", -8.5, "Chữ 'Nhưng trả lời chậm chỉ 5 phút' hiện ra (f200)"),
    ("03_Scene", 7.08, "ui", "S03 Soft Warning 'Mất đơn'", "packs/uisfx-themes/soft/warning.ogg", -8.0, "Âm báo trầm tinh tế nhấn câu 'là mất đơn vào tay đối thủ' (f212)"),

    # --- 04_Scene (9.13s - 12.53s): Pain Point 2 (Inbox Overload Counter) ---
    ("04_Scene", 9.20, "whoosh", "S04 Studio Expand Zoom-In", "packs/uisfx-themes/studio/expand.ogg", -7.0, "Camera đẩy vào màn hình Inbox quá tải (f276)"),
    ("04_Scene", 9.35, "pop", "S04 Minimal Open Counter Cards", "packs/uisfx-themes/minimal/open.ogg", -8.0, "Hai thẻ đếm thông báo 04_Scene_Counter01 & 02 mở ra (f280)"),
    ("04_Scene", 9.48, "ui", "S04 Studio Badge Pop", "packs/uisfx-themes/studio/badge.ogg", -8.0, "Badge đỏ báo tin nhắn tồn đọng xuất hiện (f284)"),
    ("04_Scene", 9.85, "ui", "S04 Minimal Progress Step 1", "packs/uisfx-themes/minimal/progress-step.ogg", -9.5, "Bộ đếm tin nhắn nhảy số đợt 1 + rung nhẹ (f295)"),
    ("04_Scene", 10.58, "ui", "S04 Studio Progress Step 2", "packs/uisfx-themes/studio/progress-step.ogg", -9.5, "Bộ đếm tin nhắn nhảy số đợt 2 (f317)"),
    ("04_Scene", 10.74, "ui", "S04 Studio Warning Shake", "packs/uisfx-themes/studio/warning.ogg", -8.5, "Badge rung cảnh báo quá tải đợt 2 (f322)"),
    ("04_Scene", 11.48, "ui", "S04 Cinematic Warning Peak", "packs/uisfx-themes/cinematic/warning.ogg", -8.0, "Badge rung cảnh báo đỉnh điểm trước khi sang giải pháp (f344)"),

    # --- 05_Scene (12.13s - 15.90s): Hero Reveal (OPA AGENT) ---
    ("05_Scene", 12.15, "impact", "S05 Cinematic Wake Hero Reveal", "packs/uisfx-themes/cinematic/wake.ogg", -6.0, "Âm mở màn công nghệ cao khi xuất hiện giải pháp OPA AGENT (f364)"),
    ("05_Scene", 12.24, "riser", "S05 Glass Connect Brand Shimmer", "packs/uisfx-themes/glass/connect.ogg", -7.5, "Hiệu ứng âm thanh kính trong trẻo tôn vinh thương hiệu OPA Agent"),
    ("05_Scene", 13.25, "whoosh", "S05 Soft Expand Pill Button", "packs/uisfx-themes/soft/expand.ogg", -8.0, "Nút pill 'AI Bán Hàng Cho Shop Dùng Pancake' trượt ra (f397)"),
    ("05_Scene", 13.50, "ui", "S05 Glass Select Pill Glow", "packs/uisfx-themes/glass/select.ogg", -8.0, "Viền sáng neon kích hoạt mượt mà quanh nút pill (f405)"),

    # --- 06_Scene (15.20s - 27.17s): Live AI Chat Demo (Stock & Bill POS) ---
    ("06_Scene", 15.30, "whoosh", "S06 Cinematic Expand Chat UI", "packs/uisfx-themes/cinematic/expand.ogg", -7.0, "Giao diện Chat 3D nghiêng trượt vào trung tâm (f459)"),
    ("06_Scene", 16.70, "pop", "S06 Soft Focus Customer 1 Avatar", "packs/uisfx-themes/soft/focus.ogg", -9.5, "Avatar khách hàng Minh Anh xuất hiện (f501)"),
    ("06_Scene", 16.95, "ui", "S06 Studio Typing Customer 1", "packs/uisfx-themes/studio/typing.ogg", -9.5, "Nhịp gõ phím nhẹ khi khách hỏi tồn kho (f508)"),
    ("06_Scene", 17.17, "ui", "S06 Soft Receive Customer 1 Question", "packs/uisfx-themes/soft/receive.ogg", -7.5, "Bong bóng câu hỏi 'Váy Lụa Đỏ size S còn hàng không ạ?' hiện ra (f515)"),
    ("06_Scene", 17.35, "pop", "S06 SciFi Focus OPA Avatar 1", "packs/uisfx-themes/scifi/focus.ogg", -9.0, "Avatar OPA Agent kích hoạt phản hồi tức thì (f520)"),
    ("06_Scene", 17.60, "scifi", "S06 Studio Scanning Pancake Stock", "packs/uisfx-themes/studio/scanning.ogg", -9.5, "OPA Agent quét dữ liệu tồn kho Pancake POS (f528)"),
    ("06_Scene", 18.54, "ui", "S06 Glass Send AI Stock Reply", "packs/uisfx-themes/glass/send.ogg", -7.0, "OPA Agent gửi câu trả lời 'vẫn còn 3 chiếc ạ!' tại f556"),
    ("06_Scene", 21.68, "whoosh", "S06 Glass Swipe Scroll to Title 2", "packs/uisfx-themes/glass/swipe.ogg", -7.5, "Cuộn đoạn chat & chuyển sang 'Chốt đơn & Xác minh bill tự động' (f650)"),
    ("06_Scene", 22.40, "pop", "S06 Soft Focus Customer 2 Avatar", "packs/uisfx-themes/soft/focus.ogg", -9.5, "Avatar khách hàng thứ 2 xuất hiện (f672)"),
    ("06_Scene", 22.65, "ui", "S06 Studio Typing Customer 2", "packs/uisfx-themes/studio/typing.ogg", -9.5, "Khách gõ xác nhận chuyển khoản (f679)"),
    ("06_Scene", 22.90, "ui", "S06 Soft Receive Customer 2 Bill", "packs/uisfx-themes/soft/receive.ogg", -7.5, "Bong bóng báo 'Mình vừa chuyển khoản 450k rồi nhé' hiện ra (f687)"),
    ("06_Scene", 23.25, "scifi", "S06 Studio Processing Bill Verification", "packs/uisfx-themes/studio/processing.ogg", -9.0, "AI tự động kiểm tra bill chuyển khoản 450.000đ (f697)"),
    ("06_Scene", 24.30, "ui", "S06 Glass Checkout Order #PK8921", "packs/uisfx-themes/glass/checkout.ogg", -6.5, "Xác minh bill hợp lệ [OK] & tự động tạo đơn #PK8921 trên Pancake POS (f729)"),

    # --- 07_Scene (26.90s - 31.90s): 24/7 Multi-Chat Wall ---
    ("07_Scene", 26.95, "whoosh", "S07 Cinematic Expand Chat Wall", "packs/uisfx-themes/cinematic/expand.ogg", -7.0, "Camera lùi mở bức tường 9 cột chat song song (f808)"),
    ("07_Scene", 27.25, "ui", "S07 Zen Receive Cascade 1", "packs/uisfx-themes/zen/receive.ogg", -9.5, "Tin nhắn đồng loạt nảy nhẹ trên tường chat nhịp 1 (f817)"),
    ("07_Scene", 27.55, "ui", "S07 Zen Send Cascade 2", "packs/uisfx-themes/zen/send.ogg", -9.5, "AI phản hồi đồng loạt trên tường chat nhịp 2 (f826)"),
    ("07_Scene", 27.85, "ui", "S07 Soft Receive Cascade 3", "packs/uisfx-themes/soft/receive.ogg", -9.5, "Tin nhắn đa kênh nảy nhẹ nhịp 3 (f835)"),
    ("07_Scene", 28.65, "whoosh", "S07 Glass Expand 'Chăm sóc 24/7' Pill", "packs/uisfx-themes/glass/expand.ogg", -7.0, "Nền chat mờ đi & bảng 'Chăm sóc hàng ngàn khách 24/7' lướt vào tâm (f860)"),
    ("07_Scene", 28.95, "ui", "S07 Studio Complete 24/7 Lock", "packs/uisfx-themes/studio/complete.ogg", -8.0, "Bảng tiêu đề 24/7 khớp vị trí trung tâm (f868)"),
    ("07_Scene", 31.35, "whoosh", "S07 Studio Swipe Out", "packs/uisfx-themes/studio/swipe.ogg", -7.5, "Tường chat lướt gọn sang trái nhường chỗ Scene 08 (f940)"),

    # --- 08_Scene (31.37s - 34.57s): 5-Minute Pancake Setup ---
    ("08_Scene", 31.58, "whoosh", "S08 Glass Swipe 'Thiết lập chỉ trong 5 phút'", "packs/uisfx-themes/glass/swipe.ogg", -7.5, "Tiêu đề tốc độ thiết lập trượt ra mượt mà (f947)"),
    ("08_Scene", 32.02, "ui", "S08 Studio Connect 'Kết nối thẳng qua Pancake'", "packs/uisfx-themes/studio/connect.ogg", -8.0, "Âm kết nối công nghệ nhấn mạnh tích hợp Pancake (f961)"),

    # --- 09_Scene (34.13s - 39.13s): Smart Response Mode Selector ---
    ("09_Scene", 34.18, "whoosh", "S09 Soft Expand Scene 09", "packs/uisfx-themes/soft/expand.ogg", -7.5, "Mở màn hình 'Chế độ phản hồi thông minh' (f1025)"),
    ("09_Scene", 35.65, "pop", "S09 Studio Focus Mode Button 01", "packs/uisfx-themes/studio/focus.ogg", -8.5, "Nút 'AI tự tư vấn & lên đơn POS' hiện ra (f1070)"),
    ("09_Scene", 35.80, "pop", "S09 Minimal Focus Mode Button 02", "packs/uisfx-themes/minimal/focus.ogg", -9.0, "Nút 'AI nháp câu trả lời cho nhân viên' hiện ra lệch nhịp (f1074)"),
    ("09_Scene", 36.23, "ui", "S09 Studio Press Mode Button 01", "packs/uisfx-themes/studio/press.ogg", -7.5, "Nhấn chọn nút 'AI tự tư vấn & lên đơn POS' (Scale 94% tại f1087)"),
    ("09_Scene", 36.32, "ui", "S09 Glass Toggle-On Cyan Glow", "packs/uisfx-themes/glass/toggle-on.ogg", -7.5, "Viền sáng xanh cyan kích hoạt mượt mà quanh nút 01 (f1090)"),

    # --- 10_Scene (38.47s - 42.93s): Shop Brand Tone Selector ---
    ("10_Scene", 38.52, "whoosh", "S10 Soft Swipe Scene 10", "packs/uisfx-themes/soft/swipe.ogg", -7.5, "Chuyển sang màn 'Tùy chỉnh giọng điệu của shop' (f1156)"),
    ("10_Scene", 40.00, "pop", "S10 Zen Focus Tone 01 'Chuyên nghiệp'", "packs/uisfx-themes/zen/focus.ogg", -9.0, "Nút 'Chuyên nghiệp' hiện ra nhẹ nhàng (f1200)"),
    ("10_Scene", 40.10, "pop", "S10 Soft Focus Tone 02 'Thân thiện'", "packs/uisfx-themes/soft/focus.ogg", -9.0, "Nút 'Thân thiện' hiện ra nhịp 2 (f1203)"),
    ("10_Scene", 40.24, "pop", "S10 Studio Focus Tone 03 'Ngắn gọn'", "packs/uisfx-themes/studio/focus.ogg", -9.0, "Nút 'Ngắn gọn' hoàn tất bộ 3 lựa chọn (f1207)"),
    ("10_Scene", 40.67, "ui", "S10 Studio Press Tone 02 'Thân thiện'", "packs/uisfx-themes/studio/press.ogg", -7.5, "Nhấn chọn nút 'Thân thiện' (Scale 94% tại f1220)"),
    ("10_Scene", 40.76, "ui", "S10 Glass Toggle-On Tone 02 Glow", "packs/uisfx-themes/glass/toggle-on.ogg", -7.5, "Viền sáng xanh cyan bật sáng cho nút 'Thân thiện' (f1223)"),

    # --- 11_Scene (42.70s - 47.50s): 3x Pancake POS Slot-Machine Sync ---
    ("11_Scene", 42.78, "whoosh", "S11 Cinematic Expand 'Đồng bộ trực tiếp với'", "packs/uisfx-themes/cinematic/expand.ogg", -7.0, "Camera đẩy vào cụm tiêu đề đồng bộ (f1283)"),
    ("11_Scene", 43.55, "whoosh", "S11 Studio Swipe Slot 1 ('tồn kho Pancake POS')", "packs/uisfx-themes/studio/swipe.ogg", -8.0, "Cụm 1 'tồn kho Pancake POS' trượt lên (f1306)"),
    ("11_Scene", 44.08, "ui", "S11 Minimal Select Slot 1 Lock", "packs/uisfx-themes/minimal/select.ogg", -8.5, "Cụm 1 khớp vị trí hiển thị (f1322)"),
    ("11_Scene", 44.80, "whoosh", "S11 Studio Swipe Slot 2 ('bảng giá & chính sách')", "packs/uisfx-themes/studio/swipe.ogg", -8.0, "Cụm 2 'bảng giá & chính sách shop' trượt lên thế chỗ (f1344)"),
    ("11_Scene", 45.32, "ui", "S11 Minimal Select Slot 2 Lock", "packs/uisfx-themes/minimal/select.ogg", -8.5, "Cụm 2 khớp vị trí hiển thị (f1360)"),
    ("11_Scene", 46.05, "whoosh", "S11 Glass Swipe Slot 3 ('xác minh bill chuyển khoản')", "packs/uisfx-themes/glass/swipe.ogg", -7.5, "Cụm 3 'xác minh bill chuyển khoản' trượt vào chốt hạ (f1381)"),
    ("11_Scene", 46.55, "ui", "S11 Studio Complete 3x POS Sync", "packs/uisfx-themes/studio/complete.ogg", -7.5, "Xác nhận hoàn tất đồng bộ 3 tính năng trụ cột Pancake POS (f1396)"),

    # --- 12_Scene (47.47s - 50.93s): AI Powered Network & Sparkle Stars ---
    ("12_Scene", 47.52, "whoosh", "S12 Cinematic Expand AI Hub", "packs/uisfx-themes/cinematic/expand.ogg", -6.5, "Camera lùi nhanh từ tâm OPA Hub mở mạng lưới AI (f1426)"),
    ("12_Scene", 47.90, "pop", "S12 Soft Select Inner Ring Nodes", "packs/uisfx-themes/soft/select.ogg", -9.0, "Các nút chân dung & icon vòng trong bung mở đồng bộ (f1437)"),
    ("12_Scene", 48.25, "ui", "S12 Studio Connect Network Links", "packs/uisfx-themes/studio/connect.ogg", -8.5, "Các nhánh mạng lưới kết nối hoàn chỉnh (f1447)"),
    ("12_Scene", 48.87, "riser", "S12 Glass Complete AI Sparkle Stars", "packs/uisfx-themes/glass/complete.ogg", -7.0, "4 ngôi sao AI 4 cánh (12_Scene_Star_Animation) tỏa sáng (f1466-f1476)"),
    ("12_Scene", 49.15, "whoosh", "S12 Soft Expand Full Ecosystem", "packs/uisfx-themes/soft/expand.ogg", -8.0, "Camera lùi bước 2 mở toàn cảnh hệ sinh thái OPA (f1474)"),

    # --- 13_Scene (50.70s - 55.50s): Grand Finale & CTA ---
    ("13_Scene", 50.72, "impact", "S13 Cinematic Wake Finale Reveal", "packs/uisfx-themes/cinematic/wake.ogg", -6.0, "Xung trầm công nghệ mở màn kết 'Bứt phá doanh số tự động cùng OPA AGENT' (f1521)"),
    ("13_Scene", 50.90, "sonic", "S13 Cinematic Complete Brand Resolution", "packs/uisfx-themes/cinematic/complete.ogg", -6.5, "Hợp âm kết thúc sang trọng, hiện đại khẳng định thương hiệu OPA Agent (f1527)"),
    ("13_Scene", 51.32, "whoosh", "S13 Glass Expand URL CTA ('chat.overpowers.agency')", "packs/uisfx-themes/glass/expand.ogg", -7.5, "Dòng địa chỉ web chat.overpowers.agency hiện ra mượt mà (f1540)"),
    ("13_Scene", 51.56, "ui", "S13 Studio Select CTA Final Lock", "packs/uisfx-themes/studio/select.ogg", -8.0, "Điểm nhấn khép lại video tinh tế tại URL CTA (f1547)"),
]

unique_files = sorted(set(c[4] for c in CUES))
converted_map = {}

for rel_path in unique_files:
    src_path = os.path.join(SFX_ROOT, rel_path.replace("/", os.sep))
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Missing SFX file: {src_path}")
    parts = rel_path.split("/")
    theme = parts[-2]
    stem = os.path.splitext(parts[-1])[0]
    safe_wav_name = f"pro_{theme}_{stem}.wav"
    dst_path = os.path.join(OUT_WAV_DIR, safe_wav_name)

    m = csv_metrics.get(rel_path)
    if not m:
        raise KeyError(f"Missing CSV metrics for {rel_path}")

    pre_trim_db = -4.5
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", src_path,
        "-af", f"volume={pre_trim_db}dB,lowpass=f=11000",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le",
        dst_path,
    ]
    subprocess.run(cmd, check=True)

    converted_map[rel_path] = {
        "wav_name": safe_wav_name,
        "wav_path": dst_path.replace("\\", "/"),
        "dur": m["dur"],
        "peak_s": m["peak_s"],
        "tp_dbtp": round(m["tp_dbtp"] + pre_trim_db, 1),
        "m_max": round(m["m_max"] + pre_trim_db, 1),
        "centroid": m["centroid"],
    }

LABEL_COLORS = {
    "whoosh": 9,   # Green
    "impact": 10,  # Purple
    "pop": 11,     # Orange
    "ui": 8,       # Blue
    "riser": 14,   # Cyan
    "scifi": 13,   # Magenta
    "sonic": 13,   # Magenta
}

resolved_cues = []
for idx, (scene, cue_sec, cat, name, rel_path, ae_gain_db, rationale) in enumerate(CUES, 1):
    info = converted_map[rel_path]
    peak_s = info["peak_s"]
    start_sec = round(cue_sec - peak_s, 4)
    scene_start = SCENE_STARTS[scene]
    local_cue_sec = round(cue_sec - scene_start, 4)
    local_start_sec = round(local_cue_sec - peak_s, 4)

    resolved_cues.append({
        "idx": idx,
        "scene": scene,
        "cue_sec": cue_sec,
        "frame": round(cue_sec * 30),
        "start_sec": start_sec,
        "local_cue_sec": local_cue_sec,
        "local_start_sec": local_start_sec,
        "cat": cat,
        "label_color": LABEL_COLORS.get(cat, 8),
        "name": name,
        "rel_path": rel_path,
        "wav_name": info["wav_name"],
        "wav_path": info["wav_path"],
        "dur": info["dur"],
        "peak_s": peak_s,
        "gain_db": ae_gain_db,
        "eff_dbtp": round(info["tp_dbtp"] + ae_gain_db, 1),
        "rationale": rationale,
    })

with open(OUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump({"files": converted_map, "cues": resolved_cues}, f, ensure_ascii=False, indent=2)

print(f"Mastered {len(converted_map)} WAV files and saved {len(resolved_cues)} cues to {OUT_JSON_PATH}")
