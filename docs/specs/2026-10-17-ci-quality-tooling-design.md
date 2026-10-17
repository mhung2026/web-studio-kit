# Nâng cấp Web Studio Kit — CI, quét bảo mật, load test, chuẩn chất lượng rõ ràng

**Ngày:** 2026-10-17 • **Trạng thái:** chờ chủ dự án duyệt spec
**Phạm vi:** nâng cấp chính bộ kit (`E:\Working\web-studio-kit`) — áp dụng cho mọi dự án dùng `web-studio-kit` kể từ bản nâng cấp này, không phải một dự án cụ thể nào.

## 1. Bối cảnh

Thiết kế ban đầu của kit (`docs/specs/2026-10-16-web-studio-team-design.md` §8 "Ngoài phạm vi") chủ động loại "dựng CI/CD" khỏi phạm vi. Sau khi dùng thử, chủ dự án muốn bổ sung lại một phần việc đó cùng 3 việc khác: thêm tool quét chất lượng/bảo mật, thêm script mô phỏng tải, và làm rõ "chuẩn" để biết khi nào một dự án thật sự đạt chất lượng — hiện các chuẩn này nằm rải rác ở `ENGINEERING.md` §2–§4, bảng "Lệnh kiểm chứng" của `STUDIO.md`, và mô tả cổng G1–G4 trong `SKILL.md`.

**Quyết định này sửa đổi §8 của spec gốc** (cho phần CI), giữ nguyên phần còn lại của §8 (không CD, không pentest sâu, không agent nghiên cứu thị trường...).

## 2. Mục tiêu và tiêu chí thành công

1. Dự án mới dùng kit từ M0 có sẵn: workflow CI tự động, 2 lệnh quét chất lượng/bảo mật trong bảng Lệnh kiểm chứng, template script load test.
2. Tiêu chí ĐẠT/KHÔNG ĐẠT của mỗi cổng G1–G4 nêu rõ ràng trong `SKILL.md`, không phải suy luận từ nhiều file.
3. Không phá vỡ nguyên tắc nền của kit: một nguồn sự thật (`STUDIO.md` bảng Lệnh kiểm chứng), lệnh `none` = không được báo "pass", agent không tự deploy/không cài công cụ hệ thống/không tốn tiền.
4. `tools/check_kit.py` + test phải enforce được cấu trúc mới (file template tồn tại, nội dung bắt buộc có) — không chỉ ghi trong văn bản rồi không ai kiểm.

## 3. Phạm vi

### Trong phạm vi
1. **CI (không phải CD).** Workflow tự động chạy đúng các lệnh đã khai trong bảng "Lệnh kiểm chứng" của `STUDIO.md` mỗi lần push/PR. GitHub Actions làm mặc định (repo của chủ dự án lưu trên GitHub).
2. **2 dòng lệnh kiểm chứng mới** trong `STUDIO.md`: quét lỗ hổng dependency (`npm audit`/tương đương theo stack) và SAST bằng Semgrep (ruleset có sẵn cục bộ, không cần tài khoản).
3. **Template script load test bằng k6** — hiện thực hoá checklist "Load test trước G4" đã có sẵn ở `ENGINEERING.md` §4 nhưng trước nay chưa có công cụ cụ thể.
4. **Viết lại rõ tiêu chí cổng G1–G4** trong `SKILL.md`, gắn thẳng vào bảng Lệnh kiểm chứng (gồm cả 2 dòng mới + load test khi có backend).
5. **`check_kit.py`:** thêm kiểm tra 2 file template mới tồn tại và bảng Lệnh kiểm chứng mẫu có nhắc 2 mục mới — biến "chuẩn" thành cái được enforce, không chỉ là văn bản.

### Ngoài phạm vi (giữ nguyên hoặc không đổi)
- Deploy tự động (CD) — chủ dự án vẫn tự deploy theo `DEPLOY_GUIDE.md`, không đổi.
- Pentest/DAST chuyên sâu, dịch vụ bảo mật trả phí/cần tài khoản.
- Thêm agent mới hay đổi roster 9 agent / `EXPECTED_AGENTS`.
- Agent tự cài k6 (hay bất kỳ công cụ hệ thống nào) thay chủ dự án — vẫn áp dụng "Điều kiện dừng" mục 5 đã có sẵn trong `SKILL.md` (không cần cơ chế mới).
- Áp ngược 2 dòng lệnh mới cho dự án đã khởi tạo `studio/` từ trước — cơ chế "Kit-version lệch → mở phiếu nâng cấp" đã có sẵn ở `SKILL.md` Bước 0 mục 4 tự lo việc này.

## 4. Quyết định thiết kế chính

| Quyết định | Lý do | Đánh đổi chấp nhận |
|---|---|---|
| CI only, không CD | Giữ nguyên luật cứng "agent không tự deploy, không dùng khóa thật" của kit; CI (chạy lint/test/build) không đụng hạ tầng thật, không cần secret | Dự án vẫn phải deploy tay; không có "xanh là lên prod" |
| GitHub Actions làm mặc định | Repo mẫu và hướng dẫn cài đặt của kit đều giả định GitHub; phổ biến nhất | Dự án dùng GitLab/Bitbucket phải tự đổi — ghi chú rõ trong template |
| Dependency audit + Semgrep, không phải tool trả phí (Snyk, SonarQube...) | Khớp ràng buộc "không tốn tiền, không tài khoản thật" của kit; cả hai chạy local/CI không cần đăng nhập | Độ phủ lỗ hổng thấp hơn tool thương mại — chấp nhận được ở mức "cơ bản" như audit đặc tả đã làm |
| Semgrep dùng ruleset pinned cục bộ (`p/ci`/`p/owasp-top-ten` tải một lần), không dùng chế độ "auto" gọi registry mỗi lần chạy | Chế độ auto âm thầm gọi mạng mỗi lần — vi phạm tinh thần "không hành động ra ngoài máy" ngoài ý muốn | web-tech-architect phải ghi rõ lệnh cụ thể, không được để "auto" mặc định |
| k6 cho load test (không phải autocannon/artillery) | Không phụ thuộc ngôn ngữ backend — chỉ bắn HTTP, dùng chung được cho mọi dự án kit quản lý | k6 là binary ngoài (không qua npm) → luôn rơi vào "Điều kiện dừng" mục 5, phải hỏi chủ dự án trước khi cài lần đầu — **đây là hành vi đúng, không phải thiếu sót** |
| Không tạo file "chuẩn chất lượng" mới | Kit đã có nguyên tắc một nguồn sự thật; thêm file song song sẽ tạo nguy cơ lệch nhau | Phải sửa `SKILL.md` (nhiều chỗ) thay vì chỉ thêm 1 file mới — chấp nhận vì nhất quán quan trọng hơn tiện sửa |
| Không đổi `web-release-manager.md` | Gate G4 của agent này ("QA đã ĐẠT full regression") đã tự động phủ mọi dòng mới trong bảng Lệnh kiểm chứng nhờ cơ chế QA chạy lại toàn bộ — không cần nhắc lại | Không có |
| **CI không phải tiêu chí cổng — chỉ là hạ tầng cho chủ dự án** | Producer hiện chỉ push lên remote ở G4 và luôn hỏi chủ dự án trước (luật có sẵn, không đổi). Nếu coi "CI phải xanh" là điều kiện cổng, Producer sẽ phải tự push định kỳ trong G1–G3 để có lần chạy CI thật — vi phạm luật "hành động ra ngoài máy/mạng cần hỏi chủ dự án". Gate chất lượng tiếp tục dựa 100% vào việc chạy lệnh **local** (QA đã làm việc này từ trước, không đổi) | Workflow `ci.yml` có thể không chạy lần nào cho tới khi chủ dự án tự push/mở PR — chấp nhận được; ghi rõ trong template là "tiện ích cho chủ dự án khi họ tự đẩy code, không phải điều kiện cổng của Producer" |
| 2 dòng bảo mật mới bắt buộc **từ M0, cùng tier với lint/typecheck** (không phải chỉ ở G3/G4) | `web-qa-engineer.md` đã có sẵn câu "Lint và typecheck là bắt buộc" áp dụng từ M0 qua mọi cổng — thêm 2 dòng mới vào đúng câu đó là nhất quán nhất, không cần một cơ chế "chỉ bắt buộc ở cổng cuối" riêng | Milestone đầu (ngay sau M0) đã phải sạch bảo mật cơ bản, không đợi tới G3 mới siết — đúng tinh thần "catch sớm" |
| Load test giữ nguyên vị trí đã quy định — "trước G4" | `ENGINEERING.md` §4 vốn đã ghi rõ "Load test... trước G4"; không có mâu thuẫn cần giải quyết thêm, chỉ cần `SKILL.md` trỏ rõ tới điều khoản đã có | Không có |
| Mức độ bug từ tool tự động theo đúng kiểu hướng dẫn-bằng-ví-dụ đã dùng trong kit, không làm bảng ánh xạ cứng | Kit hiện không định nghĩa ranh giới chính xác giữa nghiêm trọng/cao/thấp ở đâu cả — luôn dùng 1 câu ví dụ neo rồi để QA phán đoán phần còn lại (vd. "Vi phạm §3 ENGINEERING.md... là bug nghiêm trọng"). Làm khác đi (bảng ánh xạ cứng severity→mức) sẽ lệch phong cách và dễ cứng nhắc sai trong trường hợp biên | Ranh giới mềm hơn, dựa vào phán đoán QA — chấp nhận được vì "không chắc cấp → chọn cấp cao hơn" đã là luật chung sẵn có |
| `check_kit.py` chỉ kiểm **sự hiện diện chuỗi** (tên file, vài từ khoá), không kiểm ngữ nghĩa "đúng tiêu chí gắn đúng cổng" | Checker hiện tại vốn chỉ làm được mức này cho mọi nội dung khác (vd. cặp `IMPACT_SNIPPET`/`IMPACT_PHRASE_HINT` cũng chỉ kiểm có nhắc cụm từ, không kiểm logic). Làm sâu hơn đòi hỏi parser ngữ nghĩa — ngoài phạm vi một checker markdown | Có thể SKILL.md viết đúng từ khoá nhưng sai ý — rủi ro đã tồn tại từ trước với mọi nội dung khác do checker này kiểm, không phải rủi ro mới |

## 5. Thay đổi cụ thể theo file

1. **`skills/web-studio/templates/STUDIO.md`** — thêm 3 dòng vào bảng "Lệnh kiểm chứng": `Quét lỗ hổng dependency`, `SAST (Semgrep)`, `Load test (k6, khi có backend)`, giá trị mặc định `none`. Tăng `Kit-version`.
2. **`skills/web-studio/templates/ENGINEERING.md`**
   - §1 Stack: thêm 2 dòng `Công cụ quét bảo mật (dependency audit + SAST)` và `CI (workflow, vd. GitHub Actions)`.
   - §4 checklist: sửa dòng "Load test..." để trỏ tới `studio/templates/load-test.js` làm điểm bắt đầu.
   - Tăng `Kit-version`.
3. **2 file template mới** (không phải `.md`, không cần đăng ký trong `check_kit.TEMPLATES` vì checker chỉ ràng buộc tham chiếu dạng `templates/*.md`):
   - `skills/web-studio/templates/ci.yml` — khung GitHub Actions: checkout, cài dependency theo lockfile, chạy đúng các lệnh không phải `none` trong bảng Lệnh kiểm chứng của dự án (placeholder, `web-tech-architect` điền cụ thể ở M0).
   - `skills/web-studio/templates/load-test.js` — khung k6: biến môi trường cho base URL, 1 kịch bản mẫu (ramp-up/steady/ramp-down), ngưỡng mẫu (`http_req_duration`, `http_req_failed`) để dự án điền số thật từ ADR.
4. **`agents/web-tech-architect.md`**
   - "Vùng ghi mặc định": thêm `.github/workflows/ci.yml` vào nhóm "File cấu hình gốc".
   - "Cách làm" bước 7: thêm việc tạo `.github/workflows/ci.yml` từ template, điền lệnh quét dependency + Semgrep (ruleset pinned, không dùng `auto`) vào bảng Lệnh kiểm chứng.
   - "Cách làm" bước 8 (cấp R thêm backend): thêm việc chuẩn bị `tests/load/load-test.js` từ template trước G4 khi ADR cấp R cho phép backend — cài k6 thuộc "Điều kiện dừng" mục 5 của Producer, agent không tự cài.
5. **`agents/web-qa-engineer.md`** — "Cách làm" bước 2: nối thêm vào câu "Lint và typecheck là bắt buộc" sẵn có để 2 dòng bảo mật mới cùng tier (bắt buộc từ M0, không phải chỉ ở cổng cuối); thêm 1 câu neo mức độ — phát hiện `critical`/`high` từ dependency audit hoặc `ERROR` từ Semgrep → bug mức cao trở lên (nghiêm trọng nếu ảnh hưởng dữ liệu người dùng/thanh toán), mức thấp hơn → bug thấp vào BACKLOG không chặn cổng — đúng kiểu ví dụ-neo đã dùng cho §3 ENGINEERING.md, không làm bảng ánh xạ cứng. Không cần cơ chế review riêng mới vì "chạy lại mọi lệnh kiểm chứng" đã tự động bao phủ 2 dòng mới.
6. **`skills/web-studio/SKILL.md`**
   - Viết lại rõ tiêu chí ĐẠT/KHÔNG ĐẠT trong mục "Giai đoạn": 2 dòng bảo mật mới bắt buộc từ M0 (cùng tier lint/typecheck, áp dụng mọi cổng G2 trở đi); load test giữ nguyên "trước G4" đã có sẵn ở `ENGINEERING.md` §4, chỉ trỏ rõ hơn. **CI không đưa vào làm tiêu chí cổng** (xem bảng quyết định §4) — ghi một câu ngắn giải thích để không ai hiểu nhầm "CI xanh" là điều kiện Producer tự kiểm.
   - "Khởi tạo"/M0: ghi chú CI + 2 dòng bảo mật là việc của `web-tech-architect` ở M0, cùng lúc với lệnh lint/typecheck/test/build.
   - Tăng `Kit-version` cuối file (khớp mọi template).
7. **`README.md`** — mục "Thành phần": nhắc kit nay có sẵn CI (không phải CD), quét bảo mật cơ bản, template load test; nói rõ "vẫn không tự deploy" để tránh hiểu nhầm CI = CD.
8. **`tools/check_kit.py` + `tests/test_check_kit.py`**
   - Thêm hằng liệt kê 2 file template không phải `.md` bắt buộc tồn tại (`ci.yml`, `load-test.js`), kiểm trong `check_skill()`.
   - Thêm kiểm bảng Lệnh kiểm chứng mẫu (`templates/STUDIO.md`) có nhắc cả 2 cụm liên quan bảo mật (ví dụ "dependency" và "SAST").
   - Thêm kiểm `SKILL.md` có nhắc "SAST" và "Load test" ở đâu đó (kiểm sự hiện diện chuỗi, theo đúng mức checker hiện tại đang làm cho nội dung khác như `IMPACT_SNIPPET` — **không** kiểm ngữ nghĩa "đúng tiêu chí gắn đúng cổng", việc đó ngoài khả năng một checker markdown).
   - Test mới tương ứng theo đúng style file hiện có (constructor dựng kit giả trong `tempfile`, xoá 1 file/chuỗi rồi assert lỗi xuất hiện).

## 6. Rủi ro / điểm cần cẩn thận

- Semgrep "auto" âm thầm gọi mạng mỗi lần chạy — nếu agent dùng mặc định sẽ vi phạm tinh thần "không hành động ra ngoài máy" dù không cố ý. Giải pháp đã chọn ở §4: luôn ghi lệnh cụ thể với ruleset pinned.
- k6 không cài qua lockfile dự án (không phải package npm) — sẽ luôn kích hoạt "Điều kiện dừng" mục 5 của Producer ở lần đầu cần chạy load test. Đây là hành vi mong muốn (nhất quán với luật hiện có), không phải lỗi cần sửa thêm.
- GitHub Actions giả định git host là GitHub; ghi rõ trong `ci.yml` là mẫu tham khảo, đổi nền tảng CI khác nếu dự án dùng git host khác.
- `web-release-manager.md` cố ý không đổi — nếu sau này phát hiện G4 cần kiểm tra gì thêm ngoài "QA ĐẠT full regression", đó là một quyết định riêng, không phải phần của nâng cấp này.

## 7. Không thuộc phạm vi nâng cấp này

- Không hồi tố 2 dòng lệnh kiểm chứng mới cho dự án đã có `studio/` từ trước — để nguyên cơ chế "Kit-version lệch → phiếu nâng cấp" đã có xử lý việc này.
- Không chọn thay stack CI khác ngoài GitHub Actions trong lần nâng cấp này.
- Không định nghĩa ngưỡng load test cụ thể (số người dùng, p95...) — đây luôn là số của từng dự án, ghi trong ADR như checklist §4 đã quy định từ trước.

Kit-version mục tiêu sau nâng cấp: tăng từ `0.1.0` lên `0.2.0` (thay đổi template có ý nghĩa, không chỉ sửa lỗi).
