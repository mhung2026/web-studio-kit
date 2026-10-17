# Web Studio Kit

Team agent Claude Code làm web/app, từ yêu cầu đến code chạy được, test qua. Chủ dự án tự deploy.

Kit này là bản nhân từ `game-studio-kit` (cùng chủ dự án, cùng cơ chế), đổi vai trò và quy trình cho web/app. 5/9 tên agent có tiền tố `web-` (`web-design-auditor`, `web-tech-architect`, `web-ux-designer`, `web-qa-engineer`, `web-release-manager`) để **không trùng tên** với agent cùng vai của `game-studio-kit` khi cả hai cùng cài vào `~/.claude/agents/` — xem `docs/specs/2026-10-16-web-studio-team-design.md` §1 để biết lý do.

## Thành phần
- `agents/` — 9 subagent: product-owner, web-design-auditor, web-tech-architect, impact-analyst, backend-engineer, frontend-engineer, web-ux-designer, web-qa-engineer, web-release-manager.
- `skills/web-studio/` — skill Producer (phiên chính điều phối) và template.
- `skills/web-studio/templates/ENGINEERING.md` — chuẩn code, dữ liệu/migration và checklist sẵn sàng scale; mỗi dự án có bản `studio/ENGINEERING.md`, review kiến trúc mỗi mốc.
- `tools/check_kit.py` — kiểm cấu trúc kit; `tools/discipline.md` — bản gốc khối "Kỷ luật chung" của mọi agent.
- `skills/web-studio/templates/ci.yml`, `load-test.js` — mẫu CI (GitHub Actions, không phải CD — vẫn không tự deploy) và mẫu load test (k6); `web-tech-architect` điền cụ thể ở M0 (CI, quét bảo mật) và trước G4 khi có backend (load test).
- `docs/specs/`, `docs/plans/` — thiết kế và kế hoạch.

## Cài đặt

**Cách 1 — plugin marketplace (khuyên dùng để chia sẻ):** repo này tự là marketplace của chính nó (`.claude-plugin/marketplace.json`).
```
/plugin marketplace add E:\Working\web-studio-kit
/plugin install web-studio-kit@web-studio-kit
```
Khi đã đưa repo lên git host (GitHub...), thay bằng:
```
/plugin install web-studio-kit --marketplace <owner>/<repo>
```
Agent/skill cài qua đường này được namespace theo plugin (`web-studio-kit:product-owner`...), không trùng với bất kỳ kit nào khác dù tên gốc giống nhau.

**Cách 2 — script cài trực tiếp vào `~/.claude` (không namespace, dùng tên trần `product-owner`...):**
```powershell
python -m unittest discover -s tests
powershell -ExecutionPolicy Bypass -File .\install.ps1
```
Sau đó mở phiên Claude Code mới hoặc Reload Window. Cài song song với `game-studio-kit` an toàn theo cách này — hai kit không chia sẻ tên agent nào (xem phần trên).

## Dùng
Trong thư mục dự án web/app:
- `/web-studio` hoặc "làm tiếp" — Producer tự chọn bước tiếp.
- "làm M2", "rà lại docs 03", "đánh giá tác động trước khi sửa X" — giao việc cụ thể.
- Thêm dòng `PAUSE` vào `studio/STATUS.md` để dừng ở cổng gần nhất.
- Câu hỏi cần bạn quyết nằm ở `studio/DECISIONS_PENDING.md`.
- Dự án đã có code từ trước: lần khởi tạo đầu tiên là **onboarding** — `web-tech-architect`/`impact-analyst` quét codebase hiện tại trước khi mở phiếu đầu, không giả định code trống.

## Sửa kit
1. Sửa trong repo này. Khối kỷ luật chung: sửa `tools/discipline.md` rồi chạy `python tools/sync_discipline.py`. Đổi template: tăng `Kit-version` ở mọi template và cuối `SKILL.md` (checker bắt buộc khớp); dự án cũ sẽ được Producer mở phiếu nâng cấp.
2. `python tools/check_kit.py` và test phải pass.
3. Commit, chạy lại `install.ps1`. Agent bị bỏ khỏi kit sẽ được gỡ khỏi `~/.claude/agents` (có sao lưu).

## Giới hạn
- Agent dùng skill của plugin superpowers (nạp sẵn qua `skills:`, dự phòng bằng tool `Skill`). Chưa cài plugin thì installer cảnh báo.
- Agent không deploy, không dùng khóa/tài khoản thật.
- `web-ux-designer`/`web-qa-engineer`/`frontend-engineer` cần plugin Playwright MCP (`mcp__plugin_playwright_playwright`).
- Kiểm vùng ghi của Producer dựa trên `git status`; file agent ghi ra ngoài repo không bị phát hiện. Muốn chặn cứng, thêm hook PreToolUse hoặc deny rules.
- Không có vai nghiên cứu thị trường (khác `game-studio-kit`) — kit này là công cụ hỗ trợ code nội bộ.
- CI có sẵn chỉ chạy khi chủ dự án tự push/mở PR lên git host; không phải điều kiện cổng Producer tự kiểm, và không tự deploy (CD vẫn do chủ dự án làm).
