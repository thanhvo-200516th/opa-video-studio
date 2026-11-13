# OPA Brand & Design System Guidelines

Nguồn sự thật duy nhất cho nhận diện thương hiệu, hệ thống thiết kế và tài nguyên logo của **OverPowers Agency (OPA)**.

---

## 1. Đóng gói tài nguyên Logo & Mascot

Tất cả tài nguyên đã được chuẩn hóa trong thư mục `./assets/`:

```text
assets/
├── svg/
│   ├── opa-mascot-blue.svg        # Bản chính màu xanh (#0068FF), viewBox 2000x2000
│   ├── opa-mascot-white.svg       # Bản trắng (#FFFFFF) dùng trên nền xanh hoặc nền tối
│   ├── opa-mascot-black.svg       # Bản đen (#0A0A0A) dùng cho in ấn đơn sắc hoặc nền sáng
│   └── opa-mascot-parts.svg       # Bản tách 4 phần vector (sừng L, sừng R, mõm chữ U, khe trán)
├── png/
│   ├── OPA-V4-A-Core-blue-2000.png   # PNG trong suốt 2000x2000 (#0068FF)
│   ├── OPA-V4-A-Core-white-2000.png  # PNG trong suốt 2000x2000 (#FFFFFF)
│   └── OPA-V4-A-Core-black-2000.png  # PNG trong suốt 2000x2000 (#0A0A0A)
└── pdf/
    └── OPA — Biểu tượng 2D V4.pdf    # Master vector PDF gốc
```

### Cấu trúc hình học (Mascot Anatomy)
- **Kích thước gốc**: `viewBox="0 0 2000 2000"`, Bounding Box `[306.31, 367.33, 1693.69, 1632.8]`.
- **4 thành phần vector (`opa-mascot-parts.svg`)**:
  1. `c-muzzle`: Khối mõm bo tròn hình chữ U (tượng trưng cho cái phễu hứng mọi cơ hội, không bỏ sót khách).
  2. `a-horn-left`: Sừng trái (tâm xoay pivot: `569.16, 901.07`).
  3. `b-horn-right`: Sừng phải (tâm xoay pivot: `1430.84, 901.07`).
  4. `d-nostril-gap`: Khe trán / 2 lỗ thở giữa đỉnh mõm.

---

## 2. Quy tắc màu sắc (Color Tokens)

| Tên màu | Mã Hex | Mục đích sử dụng |
|---|---|---|
| **OPA Blue (Chủ đạo)** | `#0068FF` | Màu nhận diện chính, nút bấm chính, điểm nhấn |
| **OPA Blue Dark** | `#003C99` | Trạng thái hover, đường viền đậm, nền phụ tối |
| **OPA Blue Light** | `#E6F0FF` | Nền thẻ phụ, bong bóng tin nhắn, highlight dịu |
| **Neutral Black** | `#0A0A0A` | Nền tối (dark mode), chữ tiêu đề trên nền sáng |
| **Neutral White** | `#FFFFFF` | Nền sáng, chữ trên nền xanh hoặc nền tối |
| **Neutral Border** | `#E2E8F0` | Đường kẻ, viền card, ngăn cách nội dung |
| **Neutral Surface** | `#F8FAFC` | Nền khối xám nhẹ cho UI/Dashboard |

### Quy tắc tương phản bắt buộc:
- Mascot trắng **chỉ** xuất hiện trên nền xanh `#0068FF` hoặc nền tối `#0A0A0A`.
- Mascot xanh `#0068FF` xuất hiện trên nền trắng hoặc nền nhạt `#E6F0FF`.
- Chữ trên nền xanh luôn là màu trắng `#FFFFFF`.
- Tuyệt đối **không** dùng gradient cầu vồng, không đổ bóng blur lòe loẹt, không 3D kim loại bóng bẩy.

---

## 3. Kiểu chữ (Typography)

1. **Font chính (Primary Font)**: `"Be Vietnam Pro"` (Google Fonts).
   - Đảm bảo hiển thị chuẩn các ký tự tiếng Việt có dấu (`ầ, ổ, ữ, đ...`) không bị xén mũ.
   - Tiêu đề (Headings/Display): ExtraBold (800) hoặc Bold (700).
   - Nội dung (Body/UI): Medium (500) hoặc Regular (400).
2. **Font nhấn (Accent Font)**: `"Fraunces"` Italic 800.
   - Dùng độc quyền cho cụm từ khóa quan trọng cần nhấn mạnh (ví dụ: *không bỏ sót khách*, *vận hành AI*).

---

## 4. Chuyển động (Motion Principles)

- **Đặc trưng**: Dứt khoát, chắc nịch, có lực đẩy (charge) và độ bật nảy cơ học.
- **Easing vào cảnh**: `cubic-bezier(0.2, 0.8, 0.2, 1)`.
- **Easing ra cảnh**: `cubic-bezier(0.6, 0, 0.8, 0.2)`.
- **Bật nảy (Spring Pop)**: Damping `12`, stiffness `100`, mass `1` (nảy rõ 1 nhịp rồi đứng vững, không bồng bềnh).

---

## 5. Quy tắc cấm kỵ (Don'ts)

1. Không bóp méo tỷ lệ width/height của logo/mascot.
2. Không vẽ thêm mắt, miệng cười hay chi tiết cute hoạt hình vào Bò OPA.
3. Không tự ý đổi mã màu xanh `#0068FF` sang xanh cyan hoặc xanh tím.
