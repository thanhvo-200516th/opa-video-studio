# V3 "Khám sức khỏe AI" (AI Audit): storyboard 16:9, ĐÃ DUYỆT 11/10

Ngày 11/10/2026.

- **Khung và thời lượng:** 1920×1080, 60 fps, 20 s.
- **Nguồn lời:** brief V3 trong `Prompt-motion-graphic-mascot-OPA.md`.
- **Hệ chuyển động:** dùng lại `src/v2w` của V2 16:9: camera ảo theo chặng 80–160 px, parallax, Bò, thẻ UI, chữ trồi trong mask, khối nhấn Fraunces. Ngôn ngữ chuyển động giữ đúng V2, nên không làm 3 đoạn test.
- **Ý chính:** trước khi đầu tư AI, để OPA soi xem đội bán hàng đang mất khách ở đâu.

## Luật áp

- 5 màu thương hiệu. Riêng đỏ cảnh báo `ALERT` #E5484D chỉ dùng cho dấu "rò khách", không làm nền lớn, không tô chữ, không tô Bò.
- Viết hoa đầu mọi dòng. Cụm nhấn dùng Fraunces Italic 800 kèm khối đánh dấu.
- ≤ 9 chữ mỗi khung (tính cả nhãn UI). Chữ ≥ 28 px. Mỗi nhóm chữ đứng đọc ≥ 1,5 s.
- Không cắt cứng; chuyển cảnh liền mạch. Blur chỉ khi thật nhanh.

## Storyboard (nhạc 120 BPM, phách 0,5 s)

### Cảnh 1 (0–4 s): Câu hỏi

- **Hình:**
  - Nền xanh #0068FF. Mở cận, camera kéo ra.
  - Bò trắng idle, nghiêng đầu 6° như đang hỏi (xoay cứng, đúng hình). Lớp nền xa trôi.
- **Lời:**
  - "Đầu tư AI…" (thường)
  - "Bắt đầu từ đâu?" (**cụm nhấn**: khối trắng quét, chữ xanh)
- **Âm:** nhạc vào nhẹ. Tick ở lúc khối nhấn quét. Chuông hỏi nhỏ ở lúc Bò nghiêng đầu.

### Cảnh 2 (4–10 s): Soi quy trình

- **Chuyển cảnh (khoảng 4,0 s):** Bò lấy đà (charge). Từ khe trán Bò, 5 khối quy trình bay cung ra thành hàng ngang, như khối nhả từ lòng U ở V2. Camera dolly theo hàng khối.
- **Hình:** sơ đồ 5 khối nối mũi tên: Quảng cáo → Tin nhắn → Tư vấn → Chốt → Chăm sóc. Mỗi khối là thẻ UI có icon.
  - **Kính lúp lướt qua** từ trái sang (camera bám). Khối nào nằm dưới kính thì hiện nhãn chữ, ra khỏi kính thì nhãn thu về icon. Cách này giữ ≤ 9 chữ mỗi khung mà vẫn đọc đủ 5 bước.
  - Kính dừng ở 2 khối **Tin nhắn** và **Chăm sóc**. Hai khối nhấp nháy viền đỏ `ALERT`, và các chấm đỏ nhỏ rơi khỏi khối như khách rò ra ngoài.
  - Sau đó Bò snort. Hai khối đổi sang xanh #0068FF, chấm đỏ ngừng rơi.
- **Lời:**
  - 4,5–7,0 s: "Soi từng bước bán hàng"
  - 7,0–9,8 s: "Chỉ ra chỗ đang rò khách" ("rò khách" là **cụm nhấn**)
- **Âm:** âm quét nhẹ khi kính lướt. 2 tiếng "blip" cảnh báo mềm, không còi báo động. Snort cùng tiếng "khóa" lúc 2 khối đổi xanh.

### Cảnh 3 (10–15 s): Kế hoạch

- **Chuyển cảnh (khoảng 10,0 s):** 5 khối gom lại, biến hình thành một tài liệu (match/morph). Tài liệu trượt ra giữa khung.
- **Hình:**
  - 10,2–11,9 s: đọc được tiêu đề tài liệu "Kế hoạch AI cho đội của anh chị".
  - Sau đó camera đẩy vào thân tài liệu, tiêu đề ra khỏi khung trên. 3 dòng mờ lần lượt được đánh số 1 · 2 · 3, mỗi số đúng một phách.
- **Lời:**
  - 12,0–15,0 s: "Ra kế hoạch" / "Làm gì trước, làm gì sau." ("Làm gì trước, làm gì sau." là **cụm nhấn**)
- **Âm:** tiếng giấy trượt (synth). 3 tick theo số 1 · 2 · 3.

### Cảnh 4 (15–20 s): Outro

- **Chuyển cảnh (khoảng 15,0 s):** camera lặn vào số 3, sau đó flood xanh mở ra khung outro. Cùng ngôn ngữ lặn/flood của V2.
- **Hình:** Bò trắng một bên, khối chữ một bên (như outro V2). Cú logo đập ở 15,5 s, có sonic logo của OPA.
- **Lời:** xem câu hỏi 2 bên dưới.
- **Âm:** sonic logo (a) E5–A4–C♯5 như V2. Tick ở nút CTA.

## Âm thanh

- Tự tổng hợp 100 % bằng code như V2 (`tools/audio`). Nhạc hybrid 120 BPM, master −16 LUFS, true peak ≤ −2 dBTP.
- Mốc âm đặt theo giây ở bảng trên. Hình khớp ±1 f60.

## Đầu ra

- `out/v3-16x9/v3-ai-audit_16x9.mp4` cùng ảnh bìa 16:9 và README.
- Bản không giá trước (SHOW_PRICE = false, hạn 16/10). Giá chốt 15/10 thì render lại.

## Minh chốt (11/10)

1. Nhãn 5 bước hiện dần theo kính lúp (chỉ khối dưới kính hiện chữ).
2. Outro: giữ CTA webinar, bỏ dòng báo giá. Outro gồm "AI Audit" / "Cho doanh nghiệp", rồi nút "Đăng ký webinar để được tư vấn trước". Vì vậy V3 không phụ thuộc giá, nên không cần render lại sau ngày 15/10.
3. Cụm nhấn duyệt như đề xuất: "Bắt đầu từ đâu?" · "Rò khách" · "Làm gì trước, làm gì sau.".

## Bảng mốc chốt (giây; hình và âm cùng theo bảng này)

| Giây | Hình | Âm (cue) |
|---|---|---|
| 0,00 | Mở cận nền xanh, camera kéo ra | nhạc vào (pad + nhịp nhẹ) |
| 0,25 | "Đầu tư AI…" trồi | — |
| 0,75 | "Bắt đầu từ đâu?" trồi | — |
| 1,00 | Bò nghiêng đầu 6° | `chime-hoi` (chuông hỏi nhỏ) |
| 1,50 | khối nhấn "Bắt đầu từ đâu?" quét | `tick-accent-1` |
| 3,50 | Bò lấy đà (charge), nhóm chữ 1 rút | `whoosh-windup` (kết thúc 3,95) |
| 4,00 | Khối 1 bật khỏi khe trán; khối 2–5 cách 0,1 s (4,1 · 4,2 · 4,3 · 4,4) | `thump` 4,00 + `tick-eject` ×5 |
| 4,50 | "Soi từng bước bán hàng" trồi | — |
| 5,00–7,00 | Kính lúp lướt trái → phải; nhãn hiện dưới kính | `scan` (quét nhẹ, kéo dài) |
| 7,00 | Khối "Tin nhắn" nháy viền đỏ, chấm đỏ rơi; "Chỉ ra chỗ đang" / "Rò khách" trồi | `blip-alert-1` |
| 7,50 | Khối "Chăm sóc" nháy đỏ, chấm đỏ rơi | `blip-alert-2` |
| 8,00 | Khối nhấn "Rò khách" quét | `tick-accent-2` |
| 8,75 | Bò snort | `snort` |
| 9,00 | Hai khối đổi xanh, chấm đỏ ngừng | `tick-fix` (khóa) |
| 9,75 | Lấy đà gom khối | `whoosh-gather` (đỉnh 10,00) |
| 10,00 | 5 khối gom và biến hình thành tài liệu, tài liệu trượt ra | `paper` (giấy trượt) |
| 10,20–11,90 | Đọc tiêu đề "Kế hoạch AI cho đội của anh chị" | — |
| 12,00 | Camera đẩy vào thân tài liệu; "Ra kế hoạch" / "Làm gì trước, làm gì sau." trồi | — |
| 12,50 · 13,00 · 13,50 | Đánh số 1 · 2 · 3 | `tick-num` ×3 |
| 14,00 | Khối nhấn "Làm gì trước, làm gì sau." quét | `tick-accent-3` |
| 14,75 | Camera lấy đà lặn | `riser` (kết thúc 15,00) |
| 15,00 | Lặn vào số 3, flood xanh mở khung outro | `whoosh-dive` (đỉnh 15,00) |
| 15,50 | "AI Audit" khóa (đập 1,5 %), Bò thở phì | `hit-logo` + `subdrop-logo` + `sonic-logo` (a) |
| 15,70 | "Cho doanh nghiệp" trồi | — |
| 17,20 | Bước 1 rút | nhạc dừng, chỉ còn đuôi sonic logo |
| 17,40 | Nút "Đăng ký webinar để được tư vấn trước" spring | — |
| 17,80 | Nút khóa | `tick-cta` |
| 18,00–20,00 | Khung CTA (Bò thở, camera trôi rất nhẹ; miễn chỉ số đứng yên từ 18,3) | im dần |

## Câu hỏi đã trả lời (giữ để tra)

1. **Nhãn 5 bước:** chọn hiện bằng kính lúp (chỉ khối dưới kính hiện chữ) để giữ ≤ 9 chữ, hay hiện cả 5 nhãn cùng lúc?
2. **Outro (5 s) có 3 dòng chữ trong brief:** "AI Audit cho doanh nghiệp", "Nhắn OPA để nhận báo giá", CTA "Đăng ký webinar để được tư vấn trước". Cộng lại 19 chữ, nên phải tách thành nhiều nhịp, và 5 s không đủ để mỗi nhịp đứng ≥ 1,5 s. Chọn một:
   - (a) Giữ CTA webinar, bỏ dòng báo giá (đề xuất: V3 dẫn sang webinar).
   - (b) Giữ dòng báo giá, bỏ CTA webinar.
   - (c) Giữ cả hai, kéo video lên 22 s.
3. **Cụm nhấn:** "Bắt đầu từ đâu?", "rò khách", "Làm gì trước, làm gì sau." Duyệt hay đổi chỗ nhấn?
