# Web Studio Kit — Thiết kế team agent làm web/app

**Ngày:** 2026-10-16 • **Trạng thái:** chờ chủ dự án duyệt spec
**Dự án áp dụng đầu tiên:** chưa chọn. **Không phải tscappy** — nhánh `feat/web-prototype` của tscappy đã là một engagement `game-studio-kit` đang chạy thật (M0+M1 ĐẠT, chờ M2; xem `studio/STATUS.md` trên nhánh đó), nên tiếp tục dùng game-studio-kit cho tscappy. Web-studio-kit dành cho các dự án web/app khác của chủ dự án.

Kit này là bản nhân từ `game-studio-kit` (cùng chủ dự án, cùng cơ chế), đổi vai trò và quy trình cho phù hợp web/app thay vì game. Phần nào không đổi so với game-studio sẽ ghi "giữ nguyên game-studio" thay vì chép lại.

## 1. Mục tiêu và tiêu chí thành công

Một bộ agent Claude Code **dùng chung cho nhiều dự án web/app** (không riêng tscappy), đi từ ý tưởng/yêu cầu đến code chạy được, test qua, sẵn sàng để chủ dự án tự deploy. Hai loại việc đều phải chạy tốt:
1. **Làm mới:** dự án hoặc tính năng chưa có code.
2. **Bảo trì/nâng cấp:** sửa hoặc thêm tính năng trên code đã chạy thật — rủi ro chính là làm hỏng chức năng đã có, nên review tác động là bắt buộc trước khi sửa, không phải tùy chọn.

Thành công khi:
1. Chủ dự án gõ `/web-studio` (hoặc "làm tiếp") trong một dự án web/app bất kỳ, team tự xác định đây là dự án mới hay dự án có sẵn code, lập kế hoạch, giao việc, code, test, báo cáo có bằng chứng chạy thật.
2. Với việc bảo trì: không có phiếu sửa/thêm tính năng nào chạm code đã có hành vi đang chạy mà bỏ qua bước đánh giá tác động.
3. Team chỉ dừng hỏi ở quyết định cấp R hoặc điều kiện dừng ở §5.3.
4. Cùng một kit dùng được cho dự án mới chỉ bằng cách tạo `studio/` trong repo đó — không phải sửa kit.
5. Team không tự deploy; chủ dự án tự làm phần đó.

### Đã thống nhất với chủ dự án (trong phiên brainstorming)
- Dùng chung cho mọi dự án web/app, không riêng tscappy.
- Chủ dự án là software engineer, muốn một "team khép kín" cùng code, không phải chỉ hỏi-đáp rời rạc.
- Hai loại việc: làm mới + bảo trì/nâng cấp; bảo trì cần review kỹ để không vỡ chức năng cũ.
- Deploy do chủ dự án tự làm.
- Roster 9 vai (bỏ market-analyst, narrative-designer, art-director, systems-economist, playtester so với game-studio; đổi game-designer → product-owner, gameplay-engineer → backend-engineer, client-engineer → frontend-engineer; thêm mới `impact-analyst`): `product-owner`, `web-design-auditor`, `web-tech-architect`, `impact-analyst`, `backend-engineer`, `frontend-engineer`, `web-ux-designer`, `web-qa-engineer`, `web-release-manager`.
- Giữ `web-release-manager` ở dạng nhẹ: version, changelog, release notes, DEPLOY_GUIDE nháp — không tự deploy (đúng như bản game-studio vốn đã không deploy).
- **Tiền tố `web-`** trên 5 vai (`web-design-auditor`, `web-tech-architect`, `web-ux-designer`, `web-qa-engineer`, `web-release-manager`) là quyết định đã chốt, không phải giả định: builder-check phát hiện 5 tên này trùng hệt agent đã cài của game-studio-kit trong `~/.claude/agents/` (nội dung khác hẳn — web vs. game). Cài kiểu global như game-studio sẽ làm hai kit ghi đè lẫn nhau mỗi lần cài, phá vỡ engagement game-studio đang chạy thật (tscappy và worktree v0.4). Chủ dự án chọn phương án đổi tên (thay vì chuyển sang cài project-local) để giữ mô hình "cài một lần, dùng mọi nơi" của game-studio. 4 vai không trùng (`product-owner`, `impact-analyst`, `backend-engineer`, `frontend-engineer`) giữ tên gốc.
- Dự án áp dụng đầu tiên: chưa chọn, không phải tscappy (xem đầu tài liệu). Để trống đến khi chủ dự án có dự án cụ thể; §7.3 mô tả điều kiện cần có ở dự án đó thay vì chốt tên dự án.

### Giả định (chưa được chủ dự án nói rõ, cần xác nhận)
- Tổ chức kit: lặp lại phương án A của game-studio — repo riêng `E:\Working\web-studio-kit`, cài vào `~/.claude` qua `install.ps1`; mỗi dự án có `studio/` riêng.
- Tên skill/lệnh gọi: `web-studio`, gõ `/web-studio`.
- Không có vai nghiên cứu thị trường (bỏ market-analyst) vì mục tiêu là công cụ nội bộ hỗ trợ code, không phải định hướng sản phẩm từ đầu. Dự án nào cần vẫn gọi `market-analyst` "mượn" từ game-studio-kit nếu đã cài, nhưng đây là ngoài phạm vi kit này.
- Stack không cố định trong kit: `web-tech-architect` chọn theo từng dự án như game-studio, xác minh version/API bằng tài liệu chính thức.

## 2. Ràng buộc nền tảng

Giữ nguyên game-studio:
- **Producer là phiên Claude chính**, chạy theo skill `web-studio`; các vai còn lại là subagent, mọi agent khai báo `disallowedTools: Agent`.
- Subagent không thấy lịch sử chat của phiên chính: mọi ngữ cảnh truyền qua **phiếu việc** và file trên đĩa.
- Phiên chính có thể bị nén ngữ cảnh khi chạy dài: mọi trạng thái nằm trên đĩa (`studio/STATUS.md`…) và git.

## 3. Vai trò

**Producer** (skill `web-studio`, phiên chính): giữ backlog/STATUS, chia mốc thành phiếu, chọn agent, chạy song song phiếu không chung file, kiểm cổng, áp quyền, commit, báo cáo, gom câu hỏi cấp R. Khác với game-studio: Producer còn phải tự phân loại mỗi phiếu là "code mới" hay "chạm code đã có hành vi" để quyết có chèn bước `impact-analyst` trước engineer hay không (xem §4.2).

| Nhóm | Agent | Trách nhiệm | Vùng ghi mặc định | Tools đặc biệt | Model |
|---|---|---|---|---|---|
| Spec | `product-owner` | Brief, spec tính năng, tiêu chí chấp nhận, review đề xuất đổi phạm vi | docs thiết kế (theo `STUDIO.md`) | — | opus |
| | `web-design-auditor` | Rà đặc tả bằng con mắt mới: mâu thuẫn, case biên thiếu, lỗ hổng bảo mật cơ bản ở mức spec (không phải pentest), chỗ chưa tối ưu; đề xuất ADR. Không tự sửa đặc tả | `studio/adr/` (trạng thái *đề xuất*), `studio/reports/audit/` | Bash (validator) | opus |
| Kỹ thuật | `web-tech-architect` | Chọn stack (xác minh docs chính thức), kiến trúc, ranh giới module, ADR kỹ thuật, review cấu trúc mỗi mốc | khung dự án, config build/lint/test, ADR kỹ thuật, `studio/ENGINEERING.md` | WebFetch, Bash | opus |
| | `impact-analyst` **(mới)** | Trước khi sửa code đã có hành vi đang chạy: map hành vi/API/contract hiện tại ở vùng sắp đổi, liệt kê nơi gọi đến, viết test đặc trưng hóa (characterization test) nếu vùng đó chưa có test che phủ, chỉ rõ rủi ro vỡ và phạm vi sửa an toàn. Không tự sửa code sản phẩm | `studio/reports/impact/`, `tests/characterization/` | Bash, Grep | opus |
| | `backend-engineer` | API, domain/application logic, truy cập dữ liệu, theo TDD | `src/domain`, `src/application`, `src/api` (tên cụ thể do `web-tech-architect` chốt ở M0), test tương ứng | Bash | sonnet |
| | `frontend-engineer` | UI, component, state, tích hợp API client, build | `src/ui`/`src/components`, `src/pages` (tên cụ thể do `web-tech-architect` chốt ở M0), test tương ứng | Bash | sonnet |
| Trải nghiệm | `web-ux-designer` | Luồng màn hình, wireframe, thứ bậc thông tin, readability, onboarding, accessibility; duyệt screenshot thật | docs UX, spec màn hình | Playwright (chỉ xem) | sonnet |
| Chất lượng | `web-qa-engineer` | Test nghiệm thu, regression, bug report, kiểm bằng chứng DoD, review riêng dữ liệu/migration/idempotency, bảo mật cơ bản (input validation, auth, OWASP phổ biến) | `tests/acceptance/`, `studio/bugs/`, `studio/reports/qa/` | Bash, Playwright | sonnet |
| Phát hành | `web-release-manager` | Version bump, changelog, release notes, `DEPLOY_GUIDE.md` nháp, checklist tuân thủ cơ bản. **Không tự deploy** | `release/`, `CHANGELOG.md` | Bash | sonnet |

Vùng ghi cụ thể của từng dự án do `studio/STUDIO.md` ghi đè, giống game-studio.

### `impact-analyst` — vì sao cần vai mới
Game-studio không có vai này vì mỗi game trong kit luôn bắt đầu từ `studio/` do chính kit khởi tạo — code "cũ" vẫn luôn là code do chính team này viết và đã có test theo chuẩn của kit. Web-studio thì khác: phần lớn việc là bảo trì/nâng cấp **dự án đã tồn tại trước khi có kit**, có thể không có test đầy đủ, không theo chuẩn ENGINEERING.md. `impact-analyst` là bước đệm bắt buộc để engineer không "đoán" hành vi cũ rồi sửa sai. Chi tiết tích hợp vào vòng mốc ở §4.2.

### Kỷ luật chung (nhúng vào mọi agent)
Giữ nguyên nội dung 13 điều của game-studio (đọc STUDIO.md trước khi làm; chỉ ghi trong vùng; không tự nhận "xong" khi chưa chạy lệnh; không tự nghiệm thu việc mình; không bịa số liệu/API; chia cấp sửa lỗi/B·D/R; không tạo secret giả; không gọi agent khác; không commit; viết tiếng Việt; ưu tiên Kỷ luật chung > phiếu > skill) — đồng bộ qua `tools/discipline.md` + `tools/sync_discipline.py` như game-studio.

### Chuẩn kỹ thuật và khả năng mở rộng
Tái dùng gần như nguyên vẹn `templates/ENGINEERING.md` của game-studio — checklist §4 "Sẵn sàng scale" (server stateless, migration DB có version, index, phân trang, transaction, idempotency key, rate limit, secret chỉ ở server...) **vốn đã viết cho web/backend nói chung**, không phải thứ game-specific phải dịch lại. Điều chỉnh khi chuyển sang web-studio:
- §3 "Dữ liệu, save và trạng thái": đổi khung "save file người chơi" thành khung chung "dữ liệu bền vững của ứng dụng" (schema version, migration có test, ID ổn định, mọi thao tác gọi lặp phải idempotent qua ledger/transaction ID) — nguyên tắc giữ nguyên, chỉ đổi ví dụ từ "tiền trong game" sang "đơn hàng/thanh toán/điểm" tùy dự án.
- Bỏ phần neo vào renderer/SDK game trong §2 (domain không phụ thuộc "renderer/SDK") — thay bằng domain không phụ thuộc framework UI cụ thể (React/Vue/...) hay ORM cụ thể khi có thể, qua ports/adapters.
- `web-tech-architect`, `backend-engineer`, `frontend-engineer`, `web-qa-engineer`, `impact-analyst` bắt buộc đọc file này.

### Tích hợp skill superpowers
Giữ cơ chế game-studio: skill cốt lõi nạp sẵn qua `skills:` trong frontmatter, skill phụ agent tự gọi bằng tool `Skill`.

| Agent | Nạp sẵn (`skills:`) | Tự gọi khi cần |
|---|---|---|
| `backend-engineer`, `frontend-engineer` | `superpowers:test-driven-development`, `superpowers:verification-before-completion` | `superpowers:systematic-debugging`, `superpowers:receiving-code-review` |
| `web-qa-engineer` | `superpowers:verification-before-completion`, `superpowers:systematic-debugging` | `superpowers:test-driven-development` |
| `web-tech-architect` | `superpowers:verification-before-completion` | `superpowers:test-driven-development`, `superpowers:receiving-code-review` |
| `impact-analyst` | `superpowers:verification-before-completion` | `superpowers:systematic-debugging` (khi hành vi hiện tại trông như bug chứ không phải chủ ý) |
| 4 agent còn lại (`product-owner`, `web-design-auditor`, `web-ux-designer`, `web-release-manager`) | `superpowers:verification-before-completion` | — |

Producer gọi bằng tool `Skill`: `superpowers:brainstorming` (G0), `superpowers:writing-plans` (chia mốc), `superpowers:dispatching-parallel-agents` (giao song song), `superpowers:systematic-debugging` (cổng thất bại lần 2), `superpowers:receiving-code-review`, `superpowers:verification-before-completion` (trước khi ghi cổng ĐẠT), `superpowers:finishing-a-development-branch` (G4). Không dùng `subagent-driven-development`/`executing-plans` (trùng Vòng mốc) — giữ nguyên lý do của game-studio.

Giữ nguyên `disallowedTools: Agent` trên mọi agent — lý do như game-studio (vùng ghi, câu hỏi cấp R về tay Producer, truy vết qua phiếu).

## 4. Quy trình

### 4.1 Giai đoạn

| Giai đoạn | Agent chính | Đầu ra | Cổng |
|---|---|---|---|
| G0 Ý tưởng | Producer (`brainstorming` cùng chủ dự án) → `product-owner` | Brief 1 trang, mục tiêu, phạm vi | **Chủ dự án duyệt brief** |
| G1 Tiền sản xuất / Onboarding | `web-design-auditor`, `product-owner`, `web-tech-architect`, `web-ux-designer` (mốc đầu có UI); dự án **đã có code** → thêm `impact-analyst` quét toàn bộ để viết `STUDIO.md`/`ENGINEERING.md` từ thực tế thay vì từ ý tưởng | Đặc tả đã rà, ADR, kiến trúc+stack, kế hoạch mốc, (nếu có code cũ) bản đồ hành vi hiện tại | Validator pass; không câu R nào chặn mốc đầu |
| G2 Sản xuất (lặp M0…Mn) | `backend-engineer`/`frontend-engineer`, `impact-analyst` (khi chạm code cũ), `web-ux-designer`, `web-qa-engineer` | Code+test từng mốc | DoD mốc (§4.3) |
| G3 Hoàn thiện | `web-qa-engineer` (regression toàn bộ) ⇄ `web-ux-designer` (duyệt screenshot mọi màn hình chính) | Báo cáo regression, screenshot, sửa lỗi phát hiện | 0 bug nghiêm trọng; mọi màn hình/luồng chính qua được; accessibility cơ bản không chặn |
| G4 Release candidate | `web-release-manager`, `web-qa-engineer` | Version, changelog, release notes, `DEPLOY_GUIDE.md` nháp | Full regression trên RC; **chủ dự án duyệt phát hành** (deploy do chủ dự án tự làm) |
| G5 Sau phát hành | `web-qa-engineer`, Producer | Feedback → backlog | Lặp G2–G4 thu nhỏ |

Không còn G3 kiểu "playtester đa persona" của game-studio — thay bằng regression + duyệt UX thật, vì web/app không cần persona kiểu "người tối ưu khai thác luật" như game.

Producer xác định giai đoạn từ `studio/STATUS.md`. Repo chưa có `studio/`:
- Chưa có code đáng kể → khởi tạo như G0 (giống game-studio).
- **Đã có code chạy được** (trường hợp phổ biến hơn với web-studio) → bỏ qua G0, vào thẳng G1 kiểu onboarding: `web-tech-architect` + `impact-analyst` đọc toàn bộ codebase, test, config hiện có để viết `STUDIO.md`/`ENGINEERING.md` phản ánh **thực tế đang chạy**, không phải chuẩn lý tưởng; chênh lệch giữa thực tế và chuẩn ENGINEERING.md ghi vào `BACKLOG.md` như nợ kỹ thuật, không chặn mốc đầu.

### 4.2 Vòng lặp một mốc (G2) — khác biệt chính so với game-studio

1. **Lập kế hoạch:** đọc STATUS + kế hoạch mốc; chia phiếu nhỏ (vùng file, tiêu chí, lệnh kiểm chứng, tài liệu cần đọc) — dùng `superpowers:writing-plans`.
2. **Phân loại phiếu (Producer tự làm, không phải skill):**
   - Code hoàn toàn mới (file/module chưa tồn tại, chưa ai dùng) → bỏ qua bước 3, vào thẳng bước 4.
   - Sửa lỗi hoặc thêm tính năng **chạm vào code đã có hành vi đang chạy thật** (có người dùng/có caller) → bắt buộc bước 3 trước khi giao engineer.
3. **Đánh giá tác động:** phiếu `impact-analyst` — đọc vùng sắp sửa, liệt kê hành vi/API hiện tại và nơi gọi đến, viết characterization test nếu vùng đó chưa có test che phủ hành vi hiện tại, báo cáo rủi ro + phạm vi sửa an toàn vào `studio/reports/impact/<phiếu>.md`. Phiếu engineer kế tiếp phải đọc báo cáo này trước khi sửa.
4. **Thiết kế sẵn sàng?** Đặc tả của mốc còn mở → phiếu cho `product-owner`/`web-design-auditor` trước; engineer không tự đoán yêu cầu.
5. **Thực hiện:** TDD; phiếu không giao nhau về file chạy song song (`superpowers:dispatching-parallel-agents`).
6. **QA:** chạy test thật, đối chiếu tiêu chí, review dữ liệu/migration/idempotency/bảo mật cơ bản; bug → quay lại bước 5.
7. **UX:** khi mốc có UI, `web-ux-designer` duyệt screenshot thật.
8. **Kiến trúc:** `web-tech-architect` review theo §5 `ENGINEERING.md`; vi phạm chặn → phiếu sửa.
9. **Chốt cổng:** Producer tự chạy lại lệnh kiểm chứng, kiểm DoD, cập nhật STATUS, ghi `studio/reports/milestone/`, commit, đi tiếp mốc kế.

### 4.3 DoD chung
Giữ nguyên 6 mục của game-studio: lệnh chạy cụ thể; test chạy thật có log; screenshot nếu có màn mới; docs/data/test đồng bộ, validator pass; không bug nghiêm trọng về dữ liệu/thanh toán/trạng thái; tóm tắt done/not done/risk/next. Dự án bảo trì bổ sung điều kiện 7: **mọi phiếu chạm code cũ có báo cáo `impact-analyst` đi kèm**, nếu không có phải ghi lý do rõ ràng (vd. vùng hoàn toàn mới, không có caller).

## 5. Quyền, thay đổi đặc tả, an toàn khi chạy liên tục

Giữ nguyên cơ chế 3 cấp của game-studio, đổi ví dụ cho web:

| Cấp | Ví dụ | Quyết |
|---|---|---|
| Sửa lỗi | Bug rõ ràng không đổi hành vi dự kiến, lỗi chính tả, config sai, dependency lỗi version | Agent tự sửa (nếu trong vùng ghi) + ADR ngắn |
| B/D | Đổi cách hiện thực mà hợp đồng/API không đổi (B); đổi hành vi/tính năng người dùng thấy (D); đổi thư viện | Đề xuất → agent khác review → Producer duyệt → sửa |
| R | Đổi/thêm API công khai đã có người dùng dùng; thêm backend/DB/hạ tầng mới; đổi nhà cung cấp/bên thứ ba; việc tốn tiền hoặc cần tài khoản thật | **Hỏi chủ dự án**, kèm phương án + khuyến nghị |

Không chắc cấp nào → xếp cấp cao hơn. Quy trình sửa ADR, điều kiện dừng khi chạy liên tục (câu hỏi R chặn, tới cổng G0/G4, một mốc thất bại cổng 3 lần, lỗi nghiêm trọng dữ liệu không sửa được trong mốc, cần cài công cụ/API key/tốn tiền, `PAUSE` trong STATUS) — **giữ nguyên game-studio**, chỉ thay "lỗi nghiêm trọng tiền/kho/save" thành "lỗi nghiêm trọng dữ liệu người dùng/thanh toán/trạng thái ứng dụng".

## 6. Cấu trúc file

### 6.1 Kit (`E:\Working\web-studio-kit`, git riêng)
```
agents/                      9 file <name>.md
skills/web-studio/
  SKILL.md                   playbook Producer (bản dịch quy trình game-studio sang web)
  templates/                 STUDIO.md, STATUS.md, BACKLOG.md, DECISIONS_PENDING.md,
                             ticket.md, report.md, adr.md, milestone-report.md,
                             impact-report.md (mới, thay market-report.md/playtest-report.md),
                             DEPLOY_GUIDE.md, ENGINEERING.md
tools/check_kit.py           kiểm frontmatter, tham chiếu template (EXPECTED_AGENTS đổi theo roster mới)
tools/discipline.md          bản gốc khối Kỷ luật chung
install.ps1                  copy agents/ → ~/.claude/agents/, skills/ → ~/.claude/skills/
README.md                    tiếng Việt
docs/specs/                  spec này
```

### 6.2 Trong dự án áp dụng
```
studio/
  STUDIO.md            nguồn sự thật, bất biến, lệnh test/validate, vùng ghi, viewport kiểm UI, DoD riêng
  STATUS.md
  BACKLOG.md
  DECISIONS_PENDING.md
  adr/  tickets/  bugs/
  reports/{audit,impact,qa,milestone,arch}/
release/
```
Khác game-studio: không có `reports/market/`, `reports/playtest/`; có `reports/impact/` mới.

### 6.3 Phiếu việc và báo cáo
Giữ nguyên định dạng `ticket.md`/`report.md` của game-studio (vai, mục tiêu, vùng ghi, tiêu chí nghiệm thu, lệnh kiểm chứng, ngoại lệ TDD / đã làm, file sửa, lệnh đã chạy, NOT RUN, vấn đề phát hiện, đề xuất ADR, việc ngoài vùng).

## 7. Kiểm thử chính team

1. **Cấu trúc:** `python tools/check_kit.py` — 9 agent, frontmatter hợp lệ, tool hợp lệ, template được tham chiếu tồn tại (phỏng theo checker của game-studio, đổi `EXPECTED_AGENTS`/`TEMPLATES`).
2. **Smoke từng agent:** việc chỉ đọc tí hon trên một dự án thật; xác nhận gọi được và nêu đúng vùng ghi.
3. **Chạy thật đầu tiên:** chưa chọn dự án (không phải tscappy — xem đầu tài liệu). Khi chủ dự án chỉ định một dự án web/app cụ thể: nếu dự án đã có code → khởi tạo `studio/` kiểu onboarding, `web-tech-architect` + `impact-analyst` quét codebase hiện tại, xác định G1, xử lý ADR phát sinh, **dừng** để chủ dự án đánh giá trước khi chạy tiếp; nếu dự án chỉ có ý tưởng → khởi tạo G0 như game-studio.

## 8. Ngoài phạm vi
Tự deploy; dựng CI/CD; workflow script đa agent ngoài cơ chế Producer; đồng bộ PM ngoài; tạo ảnh bitmap; tài khoản/secret thật; nghiên cứu thị trường (không có `market-analyst` trong kit này).
