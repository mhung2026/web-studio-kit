# STUDIO — <tên làm việc của dự án>
> Cấu hình dự án cho team web-studio. Producer tạo lúc khởi tạo; mọi agent đọc file này trước khi làm.

## Dự án
- Tên làm việc:
- Loại dự án (web app / API / cả hai):
- Người dùng mục tiêu:
- Nền tảng/hạ tầng mục tiêu (đã chốt / đề xuất):
- Dự án đã có code trước khi có kit? có | không
- Giai đoạn khởi đầu: G0 | G1

## Nguồn sự thật (đọc theo thứ tự)
| Chủ đề | File | Ghi chú |
|---|---|---|

## Bất biến
Luật không được vi phạm khi chưa có ADR cấp R được chủ dự án duyệt.
-

## Lệnh kiểm chứng
Ghi `none` nếu dự án chưa có lệnh đó. Lệnh `none` nghĩa là chưa có bằng chứng: không ai được báo "pass" cho mục đó.

Bảng này là **nguồn duy nhất** của lệnh kiểm chứng; `studio/ENGINEERING.md` chỉ trỏ về đây.

| Mục đích | Lệnh | Thư mục chạy |
|---|---|---|
| Validator đặc tả | none | . |
| Test tự động | none | . |
| Lint | none | . |
| Typecheck | none | . |
| Build | none | . |
| Quét lỗ hổng dependency | none | . |
| SAST (Semgrep) | none | . |
| Load test (k6, khi có backend) | none | . |
| Chạy local / URL xem thử | none | . |

## Chuẩn kỹ thuật
Xem `studio/ENGINEERING.md` (chuẩn code, dữ liệu/migration, checklist sẵn sàng scale). Lint và typecheck phải có lệnh thật từ M0.

## Vùng ghi theo vai
Ghi đè vùng mặc định trong file agent. Để trống dòng = dùng mặc định.

| Agent | Được ghi |
|---|---|
| product-owner | |
| web-design-auditor | studio/adr/, studio/reports/audit/ |
| web-tech-architect | |
| impact-analyst | studio/reports/impact/, tests/characterization/ |
| backend-engineer | |
| frontend-engineer | |
| web-ux-designer | |
| web-qa-engineer | |
| web-release-manager | release/, CHANGELOG.md |

## Kế hoạch mốc
- File kế hoạch:
- DoD riêng của dự án:

## Quy ước thay đổi đặc tả
- Mẫu ADR riêng (nếu có; trống = `studio/templates/adr.md`):
- File ghi quyết định:
- Content version nằm ở:
- Checksum cần cập nhật (nếu có):

## Viewport kiểm UI
| Tên | Kích thước |
|---|---|
| desktop | 1440x900 |
| mobile | 390x844 |

Kit-version: 0.2.0
