# ENGINEERING — chuẩn kỹ thuật và khả năng mở rộng
> Sở hữu: `web-tech-architect`. Bắt buộc đọc: `web-tech-architect`, `backend-engineer`, `frontend-engineer`, `web-qa-engineer`, `impact-analyst`.
> Mục **[Ngay]** áp dụng từ dòng code đầu tiên. Mục **[Khi có backend]** áp dụng khi ADR cấp R cho phép thêm backend/DB; trước đó chỉ cần giữ đường nâng cấp.
> Lệnh kiểm chứng (lint, format, typecheck, test, build) chỉ ghi ở bảng "Lệnh kiểm chứng" của `studio/STUDIO.md`. Lệnh `none`: không ai được báo "pass".

## 1. Stack (web-tech-architect điền ở M0)
| Mục | Giá trị |
|---|---|
| Ngôn ngữ / version | |
| Runtime / version | |
| Package manager + lockfile | |
| Công cụ lint / format / typecheck / test | |
| Kiểm ranh giới lớp tự động (vd. dependency-cruiser, eslint boundaries) | |
| Công cụ quét bảo mật (dependency audit + SAST) | |
| CI (workflow, vd. GitHub Actions) | |

## 2. Chuẩn code [Ngay]
- Strict typing bật đầy đủ (TypeScript: `strict: true`, `noUncheckedIndexedAccess: true`); không `any` ngầm; `any` tường minh phải có comment lý do.
- Lint + format chạy trong lệnh kiểm chứng; 0 lỗi lint mới được merge. Không tắt rule hàng loạt.
- Phân lớp: domain (thuần, không I/O) → application (use case, port) → adapters (DB, HTTP, queue — fake trước) → UI/API. Phụ thuộc chỉ hướng vào trong: domain không phụ thuộc gì; application chỉ phụ thuộc domain và ports; adapters/UI phụ thuộc vào trong, không ngược lại. Domain không phụ thuộc framework UI cụ thể (React/Vue/...), ORM cụ thể, hay thời gian thực/random không seed. Không phụ thuộc vòng giữa module, kiểm bằng công cụ trong lệnh lint, không chỉ bằng review.
- Module có public interface nhỏ (`index` xuất có chủ đích); không import sâu vào file nội bộ của module khác.
- Hằng số nghiệp vụ chỉ đến từ config/data đã validate; không số cứng rải rác.
- Lỗi: lỗi nghiệp vụ trả về kiểu kết quả có mã lỗi; exception chỉ cho lỗi lập trình/hạ tầng. Không nuốt lỗi im lặng.
- Hàm/file nhỏ, một trách nhiệm; file > 300 dòng phải có lý do trong review.
- Dependency: chỉ thêm khi cần, ghi version cố định qua lockfile, kiểm giấy phép; không thêm thư viện cho việc vài dòng làm được.
- Test: unit cho domain, integration cho application + adapter, acceptance cho tiêu chí mốc; test tất định (seed, đồng hồ giả). Code đã có hành vi trước khi có kit: thêm characterization test (việc của `impact-analyst`) trước khi sửa, không viết lại test theo ý engineer đoán.

## 3. Dữ liệu và trạng thái bền vững [Ngay]
- Dữ liệu bền vững có `schemaVersion`, ID giao dịch/`revision` tăng đơn điệu và `updatedAt` (UTC) — đủ để sau này đồng bộ/giải xung đột.
- Mỗi lần đổi schema có hàm migration `vN → vN+1` và test với dữ liệu mẫu của từng version cũ. Không bao giờ làm hỏng dữ liệu cũ âm thầm.
- ID ổn định dạng chuỗi (không dùng index mảng làm ID); ID không đổi nghĩa khi dữ liệu nguồn đổi.
- Số dư/số lượng là số nguyên ở đơn vị nhỏ nhất; mọi thay đổi đi qua ledger có ID giao dịch.
- Mọi thao tác có thể bị gọi lặp (thanh toán, gửi lại request, resume) phải idempotent theo ID.
- Thời gian lưu dạng UTC/epoch; không lưu chuỗi giờ địa phương.
- Lưu trữ đi qua port (`StoragePort`/repository), không gọi DB/file trực tiếp từ domain/application — để đổi hạ tầng không phải sửa logic.
- Gọi dịch vụ ngoài (API bên thứ ba, email, thanh toán) đi qua port, có adapter giả lập, timeout và đường fallback.

## 4. Sẵn sàng scale [Khi có backend]
Checklist bắt buộc trước khi merge mã backend và trước G4:
- [ ] Server stateless: không giữ session/state trong bộ nhớ process; state ở DB/cache dùng chung → chạy được nhiều instance.
- [ ] Logic nghiệp vụ quan trọng (thanh toán, số dư, phần thưởng) được server xác thực; không tin số do client gửi.
- [ ] "Backend" gồm cả BaaS, DB hosted, SDK bên thứ ba — tất cả cần ADR cấp R.
- [ ] DB quan hệ (ví dụ PostgreSQL) cho dữ liệu nhiều người dùng; không dùng SQLite/file cho server nhiều instance.
- [ ] Backup DB tự động và **đã thử restore** (point-in-time nếu nền tảng hỗ trợ) trước G4.
- [ ] Schema DB do công cụ migration có version quản lý; migration chạy được tiến và có kế hoạch lùi; không sửa schema tay.
- [ ] Mỗi truy vấn thường dùng có index phù hợp; xem query plan với dữ liệu giả lớn.
- [ ] Không N+1 query; không `SELECT *` trong code sản phẩm.
- [ ] Mọi danh sách có phân trang (cursor) và giới hạn kích thước.
- [ ] Ghi nhiều bảng trong transaction; cập nhật tranh chấp dùng optimistic concurrency (cột version) hoặc khóa có chủ đích.
- [ ] API ghi nhận `Idempotency-Key`; callback bên thứ ba (thanh toán, webhook) chống xử lý hai lần ở tầng DB (unique constraint).
- [ ] Connection pool có giới hạn; timeout cho DB và mọi lời gọi ngoài; retry có backoff chỉ cho thao tác idempotent.
- [ ] Rate limit theo người dùng/IP; kích thước request có giới hạn.
- [ ] Secret chỉ ở server/biến môi trường; không trong client, repo hay log.
- [ ] Có đường xóa tài khoản và xuất dữ liệu người dùng (quyền riêng tư).
- [ ] Log có cấu trúc + request ID; không log dữ liệu cá nhân thừa; có metric độ trễ/lỗi.
- [ ] Việc nặng/chậm chạy ở hàng đợi nền, không chặn request.
- [ ] Asset tĩnh phục vụ qua CDN/hosting tĩnh, không qua server ứng dụng.
- [ ] Backend lỗi thì ứng dụng vẫn ở mức dùng được tối thiểu, có thông báo rõ (không bắt buộc offline-first nếu dự án không cần).
- [ ] Load test với số người dùng mục tiêu (ghi trong ADR) trước G4, bắt đầu từ `studio/templates/load-test.js` (k6); lưu kết quả vào `studio/reports/qa/`.

## 5. Review kiến trúc mỗi mốc
`web-tech-architect` chấm từng mục §2–§3 (và §4 nếu có backend): **đạt / vi phạm chặn / nợ kỹ thuật chấp nhận được**. Vi phạm chặn → mốc không đạt. Nợ kỹ thuật → ghi vào `studio/BACKLOG.md` kèm mốc trả nợ. Dự án onboarding từ code có sẵn: chênh lệch với §2–§4 phát hiện ở M0 ghi thành nợ kỹ thuật ngay, không chặn mốc đầu (xem `SKILL.md` mục Khởi tạo).

## 6. Ngoại lệ đã duyệt
| Mục | Lý do | ADR | Hạn trả |
|---|---|---|---|

Kit-version: 0.2.0
