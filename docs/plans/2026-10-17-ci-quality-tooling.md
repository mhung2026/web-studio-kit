# CI, Security-Scan & Load-Test Tooling Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nâng cấp `web-studio-kit` để mọi dự án dùng kit từ bản này có sẵn: CI tự động (không phải CD), 2 lệnh quét chất lượng/bảo mật (dependency audit + SAST), template load test (k6), và tiêu chí ĐẠT/KHÔNG ĐẠT rõ ràng cho các cổng G1–G4 — tất cả được `tools/check_kit.py` enforce cấu trúc, không chỉ ghi trong văn bản.

**Architecture:** Thêm 2 file template mới (`ci.yml`, `load-test.js`) và 3 dòng mới vào bảng "Lệnh kiểm chứng" của template `STUDIO.md`; mở rộng `check_kit.py` để bắt buộc 2 file đó tồn tại và các từ khoá liên quan xuất hiện đúng chỗ; sửa 2 agent (`web-tech-architect`, `web-qa-engineer`) và `SKILL.md` để nói rõ ai thiết lập cái gì và cổng nào kiểm cái gì. Không đổi roster 9 agent, không thêm CD, không đổi cơ chế Kit-version/vùng ghi hiện có.

**Tech Stack:** Markdown + YAML frontmatter (agent/skill), GitHub Actions YAML, k6 (JavaScript), Python 3 stdlib `unittest` cho checker.

**Spec:** `docs/specs/2026-10-17-ci-quality-tooling-design.md`

## Global Constraints

- CI **không phải** điều kiện cổng của Producer — chỉ chạy khi chủ dự án tự push/mở PR; Producer không tự push ngoài G4 (luật có sẵn, không đổi).
- Không CD, không tự deploy — không đổi so với hiện tại.
- Không đổi `EXPECTED_AGENTS` (vẫn đúng 9 agent), không thêm agent mới.
- Semgrep dùng ruleset pinned cục bộ (vd. `p/ci`), **không** dùng chế độ `auto` (gọi mạng mỗi lần chạy).
- k6 không được agent tự cài — việc cài thuộc "Điều kiện dừng" mục 5 có sẵn trong `SKILL.md`, không cần cơ chế mới.
- Mức độ bug từ tool tự động theo kiểu ví dụ-neo đã dùng trong kit (không làm bảng ánh xạ cứng): `critical`/`high` (dependency audit) hoặc `error` (Semgrep) → bug cao trở lên; thấp hơn → bug thấp, vào BACKLOG.
- Chuỗi chính xác bắt buộc xuất hiện (dùng xuyên suốt các task, không đổi cách viết giữa các file):
  - 3 dòng mới trong bảng Lệnh kiểm chứng của `templates/STUDIO.md`: `Quét lỗ hổng dependency`, `SAST (Semgrep)`, `Load test (k6, khi có backend)`.
  - 2 dòng mới trong §1 `templates/ENGINEERING.md`: `Công cụ quét bảo mật (dependency audit + SAST)`, `CI (workflow, vd. GitHub Actions)`.
  - Checker: hằng `EXTRA_TEMPLATE_FILES = ["ci.yml", "load-test.js"]`; `TEMPLATE_SNIPPETS["STUDIO.md"] = ["dependency", "SAST"]`; thêm `"SAST"` và `"load test"` (chữ thường) vào `REQUIRED_SKILL_SNIPPETS`.
  - Mọi chỗ trong `SKILL.md` nhắc tới load test phải dùng đúng cụm chữ thường `load test` (không viết hoa chữ L) để khớp chuỗi checker yêu cầu.
- Văn bản cho người: tiếng Việt; code/identifier/tên file: tiếng Anh (quy ước sẵn có).
- Kit-version: `0.1.0` → `0.2.0`, đồng bộ `SKILL.md` + toàn bộ 11 template `.md` hiện có. `ci.yml`/`load-test.js` **không** tham gia cơ chế Kit-version (không có dòng `Kit-version:` trong 2 file này — tránh phá cú pháp YAML/JS).

## Review Focus

1. **Xoá nhầm 1 trong 2 file template mới** (`ci.yml` hoặc `load-test.js`) khỏi `skills/web-studio/templates/` → checker phải báo lỗi rõ tên file, không chỉ fail chung chung. Test: Task 1.
2. **`STUDIO.md` template thiếu 1 trong 2 từ khoá bảo mật** (`dependency`, `SAST`) sau khi ai đó sửa lại bảng → checker phải bắt được, không chỉ dựa vào review mắt thường. Test: Task 1.
3. **`SKILL.md` bị sửa sau này làm mất cụm `SAST`/`load test`** (vd. ai đó viết lại gate text và quên nhắc) → checker phải bắt được. Test: Task 1.
4. **File CRLF/BOM** (thường gặp khi soạn trên Windows) cho 2 file mới — check tồn tại (`Path.exists()`) không phụ thuộc encoding nên không có rủi ro ở đây; xác nhận lại bằng cách không cần test riêng (đã an toàn theo thiết kế của `Path.exists`).
5. **Chạy `check_kit.py` đầy đủ (không `--only`) ở giữa chừng (sau Task 2 hoặc Task 3 nhưng trước Task 4) sẽ FAIL vì `SKILL.md` thật chưa có `SAST`/`load test`** — đây là trạng thái **dự kiến**, không phải lỗi hồi quy; mỗi task dùng đúng lệnh kiểm mục tiêu được ghi trong task đó, không chạy `check_kit.py` đầy đủ cho tới Task 4.

---

### Task 1: Mở rộng checker cấu trúc kit (`tools/check_kit.py`, `tests/test_check_kit.py`)

**Files:**
- Modify: `tools/check_kit.py`
- Modify: `tests/test_check_kit.py`

**Interfaces:**
- Produces (dùng ở Task 2–5): `check_kit.EXTRA_TEMPLATE_FILES = ["ci.yml", "load-test.js"]`; `check_kit.TEMPLATE_SNIPPETS` có thêm khoá `"STUDIO.md": ["dependency", "SAST"]`; `check_kit.REQUIRED_SKILL_SNIPPETS` có thêm `"SAST"` và `"load test"`.
- Không đổi chữ ký hàm nào (`check_agent`, `check_skill`, `check_kit`, `main` giữ nguyên tham số/trả về).

- [ ] **Step 1: Viết test thất bại trong `tests/test_check_kit.py`**

Trong class `KitChecks`:

1. Sửa `setUp()`: ngay sau vòng lặp tạo file cho `check_kit.TEMPLATES`, thêm vòng lặp tạo 2 file giả cho `check_kit.EXTRA_TEMPLATE_FILES` (nội dung bất kỳ, vd. `"placeholder\n"`), ghi trực tiếp vào `tpl` (biến thư mục template đã có trong `setUp`).
2. Thêm 3 test mới vào cuối class `KitChecks` (trước class `SyncDiscipline`):

```python
    def test_ci_and_load_test_templates_required(self):
        (self.root / "skills" / "web-studio" / "templates" / "ci.yml").unlink()
        self.assertTrue(any("ci.yml" in e for e in check_kit.check_kit(self.root)))

    def test_studio_template_must_mention_security_scans(self):
        path = self.root / "skills" / "web-studio" / "templates" / "STUDIO.md"
        path.write_text('Kit-version: 9.9.9\nLệnh `none`: không ai được báo "pass".\n', encoding="utf-8")
        errors = check_kit.check_kit(self.root)
        self.assertTrue(any("STUDIO.md" in e and "dependency" in e for e in errors))

    def test_skill_must_mention_security_and_load_test_gates(self):
        skill = self.root / "skills" / "web-studio" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("SAST", "x"), encoding="utf-8")
        self.assertTrue(any("SAST" in e for e in check_kit.check_kit(self.root)))
```

Lưu ý: `setUp()` hiện dựng `SKILL.md`/`STUDIO.md` giả bằng cách nối chuỗi tổng quát từ các hằng (`REQUIRED_SKILL_SNIPPETS`, `TEMPLATE_SNIPPETS`) — một khi Step 3 dưới đây thêm `"SAST"`/`"load test"` vào `REQUIRED_SKILL_SNIPPETS` và `"dependency"`/`"SAST"` vào `TEMPLATE_SNIPPETS["STUDIO.md"]`, nội dung giả trong `setUp()` tự động chứa các chuỗi này — không cần sửa `setUp()` thêm cho phần này.

- [ ] **Step 2: Chạy test, xác nhận 3 test mới FAIL**

Run: `python -m unittest discover -s tests -v`
Expected: 3 test mới FAIL (`AttributeError: module 'check_kit' has no attribute 'EXTRA_TEMPLATE_FILES'` hoặc assertion rỗng), các test cũ vẫn pass.

- [ ] **Step 3: Sửa `tools/check_kit.py`**

1. Thêm hằng ngay dưới `TEMPLATES`:
```python
EXTRA_TEMPLATE_FILES = ["ci.yml", "load-test.js"]
```
2. Sửa `TEMPLATE_SNIPPETS`:
```python
TEMPLATE_SNIPPETS = {"ticket.md": ["Ngoại lệ TDD"], "STUDIO.md": ["dependency", "SAST"]}
```
3. Sửa `REQUIRED_SKILL_SNIPPETS`:
```python
REQUIRED_SKILL_SNIPPETS = [
    "git status --porcelain --untracked-files=all",
    "docs/superpowers",
    "SAST",
    "load test",
]
```
4. Trong `check_skill()`, ngay sau vòng lặp `for name in TEMPLATES:` kiểm tồn tại, thêm:
```python
    for name in EXTRA_TEMPLATE_FILES:
        if not (templates_dir / name).exists():
            errors.append(f"templates/{name}: không tồn tại")
```

- [ ] **Step 4: Chạy test, xác nhận pass**

Run: `python -m unittest discover -s tests -v`
Expected: `Ran 42 tests ... OK`

- [ ] **Step 5: Chạy checker trên kit thật, xác nhận lỗi đúng như dự kiến**

Run: `python tools/check_kit.py`
Expected: FAIL, liệt kê đúng 3 loại lỗi: thiếu `templates/ci.yml`, thiếu `templates/load-test.js`, `templates/STUDIO.md` thiếu `dependency`/`SAST`, `SKILL.md` thiếu `SAST`/`load test` — đây là kết quả đúng (kit thật chưa có nội dung mới, các task sau sẽ bổ sung).

- [ ] **Step 6: Commit**

```bash
git add tools/check_kit.py tests/test_check_kit.py
git commit -m "$(cat <<'EOF'
feat: enforce CI/security-scan/load-test structure in kit checker

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Template CI, quét bảo mật, load test (`skills/web-studio/templates/`)

**Files:**
- Modify: `skills/web-studio/templates/STUDIO.md`
- Modify: `skills/web-studio/templates/ENGINEERING.md`
- Create: `skills/web-studio/templates/ci.yml`
- Create: `skills/web-studio/templates/load-test.js`

**Interfaces:**
- Consumes: hằng từ Task 1 (chuỗi chính xác bắt buộc — xem Global Constraints).
- Produces: nội dung mà `web-tech-architect`/`web-qa-engineer` (Task 3) và `SKILL.md` (Task 4) sẽ tham chiếu.

- [ ] **Step 1: Thêm 3 dòng vào bảng "Lệnh kiểm chứng" của `templates/STUDIO.md`**

Chèn ngay sau dòng `| Build | none | . |` và trước dòng `| Chạy local / URL xem thử | none | . |`:
```
| Quét lỗ hổng dependency | none | . |
| SAST (Semgrep) | none | . |
| Load test (k6, khi có backend) | none | . |
```

- [ ] **Step 2: Thêm 2 dòng vào bảng §1 "Stack" của `templates/ENGINEERING.md`**

Chèn ngay sau dòng `| Kiểm ranh giới lớp tự động (vd. dependency-cruiser, eslint boundaries) | |`:
```
| Công cụ quét bảo mật (dependency audit + SAST) | |
| CI (workflow, vd. GitHub Actions) | |
```

- [ ] **Step 3: Sửa dòng load test trong §4 "Sẵn sàng scale" của `templates/ENGINEERING.md`**

Đổi dòng:
```
- [ ] Load test với số người dùng mục tiêu (ghi trong ADR) trước G4; lưu kết quả vào `studio/reports/qa/`.
```
Thành:
```
- [ ] Load test với số người dùng mục tiêu (ghi trong ADR) trước G4, bắt đầu từ `studio/templates/load-test.js` (k6); lưu kết quả vào `studio/reports/qa/`.
```

- [ ] **Step 4: Tạo `skills/web-studio/templates/ci.yml`**

```yaml
name: CI
# Mẫu do web-tech-architect điền lại theo bảng "Lệnh kiểm chứng" của studio/STUDIO.md ở M0.
# CI này KHÔNG phải điều kiện cổng của Producer (xem SKILL.md mục "Giai đoạn") —
# chỉ chạy khi chủ dự án tự push hoặc mở PR lên git host của họ.

on:
  push:
    branches: [main]
  pull_request:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Cai dependency theo lockfile
        run: echo "TODO web-tech-architect: lenh cai dat theo package manager cua du an"
      - name: Lint
        run: echo "TODO web-tech-architect: lenh Lint tu bang Lenh kiem chung trong studio/STUDIO.md"
      - name: Typecheck
        run: echo "TODO web-tech-architect: lenh Typecheck tu bang Lenh kiem chung"
      - name: Test tu dong
        run: echo "TODO web-tech-architect: lenh Test tu dong tu bang Lenh kiem chung"
      - name: Build
        run: echo "TODO web-tech-architect: lenh Build tu bang Lenh kiem chung"
      - name: Quet lo hong dependency
        run: echo "TODO web-tech-architect: vd npm audit --audit-level=high"
      - name: SAST Semgrep
        run: echo "TODO web-tech-architect: vd semgrep scan --config p/ci --error (khong dung che do auto)"
```

- [ ] **Step 5: Tạo `skills/web-studio/templates/load-test.js`**

```javascript
// Mau k6 do web-tech-architect dien lai khi du an co backend va chuan bi qua cong G4.
// Nguong va base URL lay tu ADR da duyet (xem studio/ENGINEERING.md §4 "Load test").
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export const options = {
  stages: [
    { duration: '30s', target: 10 }, // TODO: ramp-up theo so nguoi dung muc tieu trong ADR
    { duration: '1m', target: 10 },  // TODO: steady state
    { duration: '30s', target: 0 },  // TODO: ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // TODO: nguong p95 theo ADR
    http_req_failed: ['rate<0.01'],   // TODO: ti le loi chap nhan duoc theo ADR
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/`); // TODO: thay bang endpoint that can kiem tai
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

- [ ] **Step 6: Kiểm nội dung (không chạy `check_kit.py` đầy đủ — xem Review Focus #5)**

Run:
```bash
python -c "
t = open('skills/web-studio/templates/STUDIO.md', encoding='utf-8').read()
assert 'Quét lỗ hổng dependency' in t and 'SAST (Semgrep)' in t and 'Load test (k6, khi có backend)' in t
e = open('skills/web-studio/templates/ENGINEERING.md', encoding='utf-8').read()
assert 'Công cụ quét bảo mật (dependency audit + SAST)' in e and 'CI (workflow, vd. GitHub Actions)' in e and 'templates/load-test.js' in e
import pathlib
assert pathlib.Path('skills/web-studio/templates/ci.yml').exists()
assert pathlib.Path('skills/web-studio/templates/load-test.js').exists()
print('OK')
"
```
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add skills/web-studio/templates/STUDIO.md skills/web-studio/templates/ENGINEERING.md skills/web-studio/templates/ci.yml skills/web-studio/templates/load-test.js
git commit -m "$(cat <<'EOF'
feat: add CI, security-scan, and load-test templates

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Nối CI/quét bảo mật/load test vào `web-tech-architect` và `web-qa-engineer`

**Files:**
- Modify: `agents/web-tech-architect.md`
- Modify: `agents/web-qa-engineer.md`

**Interfaces:**
- Consumes: tên 2 file template từ Task 2 (`studio/templates/ci.yml`, `studio/templates/load-test.js`); 3 dòng bảng Lệnh kiểm chứng từ Task 2.

- [ ] **Step 1: Sửa "Vùng ghi mặc định" của `agents/web-tech-architect.md`**

Đổi dòng:
```
- File cấu hình gốc (package manifest, lockfile, tsconfig, cấu hình build/test/lint), khung thư mục `src/`, `tests/`.
```
Thành:
```
- File cấu hình gốc (package manifest, lockfile, tsconfig, cấu hình build/test/lint, `.github/workflows/ci.yml`), khung thư mục `src/`, `tests/`.
```

- [ ] **Step 2: Sửa "Cách làm" bước 7 của `agents/web-tech-architect.md`**

Đổi:
```
7. Ở M0: điền §1 (stack, công cụ) của `studio/ENGINEERING.md` và cụ thể hóa §2–§3 theo stack; ghi lệnh lint, format, typecheck, test, build thật vào bảng Lệnh kiểm chứng của `studio/STUDIO.md`. Lint phải gồm kiểm ranh giới lớp và phụ thuộc vòng.
```
Thành:
```
7. Ở M0: điền §1 (stack, công cụ) của `studio/ENGINEERING.md` và cụ thể hóa §2–§3 theo stack; ghi lệnh lint, format, typecheck, test, build thật vào bảng Lệnh kiểm chứng của `studio/STUDIO.md`. Lint phải gồm kiểm ranh giới lớp và phụ thuộc vòng. Cùng lúc: tạo `.github/workflows/ci.yml` từ `studio/templates/ci.yml`, điền đúng các lệnh vừa ghi vào bảng Lệnh kiểm chứng; ghi lệnh quét lỗ hổng dependency (vd. `npm audit --audit-level=high`) và SAST bằng Semgrep với ruleset pinned cục bộ (vd. `semgrep scan --config p/ci`, không dùng chế độ `auto` vì chế độ đó gọi mạng mỗi lần chạy) vào 2 dòng tương ứng của bảng. CI này không phải điều kiện cổng của Producer — chỉ chạy khi chủ dự án tự push hoặc mở PR.
```

- [ ] **Step 3: Sửa "Cách làm" bước 8 của `agents/web-tech-architect.md`**

Đổi:
```
8. Thêm backend, DB, hàng đợi hay hạ tầng là cấp R: chỉ đề xuất kèm checklist §4. Trước khi có backend, giữ đường nâng cấp qua ports/adapters.
```
Thành:
```
8. Thêm backend, DB, hàng đợi hay hạ tầng là cấp R: chỉ đề xuất kèm checklist §4. Trước khi có backend, giữ đường nâng cấp qua ports/adapters. Khi ADR cấp R đã duyệt backend: trước G4, chuẩn bị `tests/load/load-test.js` từ `studio/templates/load-test.js`, điền base URL/endpoint thật và ngưỡng theo ADR. k6 là công cụ hệ thống ngoài lockfile dự án — không tự cài; việc cài thuộc "Điều kiện dừng" mục 5 của Producer (hỏi chủ dự án trước).
```

- [ ] **Step 4: Sửa "Cách làm" bước 2 của `agents/web-qa-engineer.md`**

Đổi:
```
2. Chạy lại mọi lệnh kiểm chứng trong `studio/STUDIO.md` (bỏ qua lệnh `none`, ghi NOT RUN). Ghi output tổng kết. Lint và typecheck là bắt buộc. Vi phạm §3 `studio/ENGINEERING.md` (dữ liệu không có migration, thao tác lặp không idempotent, số dư không qua ledger) là bug nghiêm trọng.
```
Thành:
```
2. Chạy lại mọi lệnh kiểm chứng trong `studio/STUDIO.md` (bỏ qua lệnh `none`, ghi NOT RUN). Ghi output tổng kết. Lint, typecheck và 2 dòng quét bảo mật (dependency audit, SAST) là bắt buộc từ M0, cùng mức với lint/typecheck. Vi phạm §3 `studio/ENGINEERING.md` (dữ liệu không có migration, thao tác lặp không idempotent, số dư không qua ledger) là bug nghiêm trọng. Phát hiện mức `critical`/`high` từ dependency audit hoặc mức `error` từ Semgrep là bug mức cao trở lên (nghiêm trọng nếu ảnh hưởng dữ liệu người dùng/thanh toán); mức thấp hơn là bug thấp, ghi vào BACKLOG, không chặn cổng.
```

- [ ] **Step 5: Kiểm cấu trúc 2 agent (độc lập với Task 2/4, dùng `--only`)**

Run: `python tools/check_kit.py --only web-tech-architect,web-qa-engineer`
Expected: `PASS: web-tech-architect, web-qa-engineer`

- [ ] **Step 6: Commit**

```bash
git add agents/web-tech-architect.md agents/web-qa-engineer.md
git commit -m "$(cat <<'EOF'
feat: wire CI/security-scan/load-test setup into tech-architect and QA agents

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Tiêu chí cổng rõ ràng trong `skills/web-studio/SKILL.md`

**Files:**
- Modify: `skills/web-studio/SKILL.md`

**Interfaces:**
- Consumes: hằng checker từ Task 1 (chuỗi bắt buộc `SAST`, `load test` — viết thường chữ "l"); nội dung Task 2/3.
- Produces: điểm đầu tiên nơi `python tools/check_kit.py` (đầy đủ, không `--only`) chạy trên repo thật phải **PASS**.

- [ ] **Step 1: Sửa mục "Kiểm sau mỗi báo cáo" bước 4**

Đổi câu:
```
Lint và typecheck trong STUDIO.md là lệnh bắt buộc từ M0; còn `none` sau M0 là lỗi cổng.
```
Thành:
```
Lint, typecheck và 2 dòng quét bảo mật (dependency audit, SAST) trong STUDIO.md là lệnh bắt buộc từ M0; còn `none` sau M0 là lỗi cổng.
```

- [ ] **Step 2: Sửa mục "Lập phiếu và giao việc" bước 1, dòng về phiếu M0**

Đổi dòng:
```
   - Phiếu M0 của `web-tech-architect` luôn có `studio/STUDIO.md` và `studio/ENGINEERING.md` trong vùng ghi.
```
Thành:
```
   - Phiếu M0 của `web-tech-architect` luôn có `studio/STUDIO.md` và `studio/ENGINEERING.md` trong vùng ghi, và yêu cầu dựng CI (`.github/workflows/ci.yml`) cùng 2 lệnh quét bảo mật ngay cùng lúc với lệnh lint/typecheck/test/build.
```

- [ ] **Step 3: Sửa gate text của G3 trong mục "Giai đoạn"**

Đổi:
```
- **G3 Hoàn thiện:** `web-qa-engineer` regression toàn bộ ⇄ `web-ux-designer` duyệt screenshot mọi màn hình chính, engineer sửa → QA chạy lại. Cổng: 0 bug nghiêm trọng, mọi màn hình/luồng chính qua được, accessibility cơ bản không chặn.
```
Thành:
```
- **G3 Hoàn thiện:** `web-qa-engineer` regression toàn bộ ⇄ `web-ux-designer` duyệt screenshot mọi màn hình chính, engineer sửa → QA chạy lại. Cổng: 0 bug nghiêm trọng, không còn phát hiện mức cao/nghiêm trọng chưa xử lý từ quét dependency/SAST, mọi màn hình/luồng chính qua được, accessibility cơ bản không chặn.
```

- [ ] **Step 4: Sửa gate text của G4 trong mục "Giai đoạn"**

Đổi:
```
- **G4 Release candidate:** `web-qa-engineer` full regression → `web-release-manager` đóng gói (version, changelog, release notes, DEPLOY_GUIDE). Dừng: chủ dự án duyệt phát hành (deploy do chủ dự án tự làm).
```
Thành:
```
- **G4 Release candidate:** `web-qa-engineer` full regression → `web-release-manager` đóng gói (version, changelog, release notes, DEPLOY_GUIDE). Có backend: load test đã chạy đạt ngưỡng ADR (`ENGINEERING.md` §4), kết quả lưu `studio/reports/qa/`. CI không phải điều kiện cổng — chỉ là tiện ích khi chủ dự án tự push/mở PR, không ảnh hưởng việc Producer chấm cổng này. Dừng: chủ dự án duyệt phát hành (deploy do chủ dự án tự làm).
```

- [ ] **Step 5: Kiểm toàn bộ kit thật (lần đầu tiên pass đầy đủ trong plan này)**

Run: `python tools/check_kit.py`
Expected: `PASS: 9 agent + skill + 11 template`

- [ ] **Step 6: Commit**

```bash
git add skills/web-studio/SKILL.md
git commit -m "$(cat <<'EOF'
feat: make quality gate criteria explicit in SKILL.md

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Tăng Kit-version, cập nhật README, kiểm tích hợp cuối

**Files:**
- Modify: `skills/web-studio/SKILL.md` (dòng `Kit-version`)
- Modify: 11 file `skills/web-studio/templates/*.md` (dòng `Kit-version`)
- Modify: `README.md`

**Interfaces:**
- Consumes: toàn bộ Task 1–4 đã commit.
- Produces: trạng thái phát hành cuối cùng của bản nâng cấp — `python tools/check_kit.py` + toàn bộ test suite pass trên repo thật.

- [ ] **Step 1: Tăng Kit-version từ `0.1.0` lên `0.2.0` ở mọi template `.md` và `SKILL.md`**

Run (bash — thay chuỗi y hệt trên mọi file, không đụng `ci.yml`/`load-test.js` vì 2 file đó không có dòng `Kit-version`):
```bash
grep -rl "Kit-version: 0.1.0" skills/web-studio | xargs sed -i 's/Kit-version: 0.1.0/Kit-version: 0.2.0/'
```

- [ ] **Step 2: Xác nhận không còn dòng version cũ, và có đúng 12 file mang version mới**

Run:
```bash
grep -rl "Kit-version: 0.1.0" skills/web-studio ; echo "exit=$?"
grep -rl "Kit-version: 0.2.0" skills/web-studio | wc -l
```
Expected: dòng đầu không in gì và `exit=1` (không còn version cũ); dòng cuối in `12` (11 template + SKILL.md).

- [ ] **Step 3: Sửa `README.md` mục "Thành phần" — thêm bullet về CI/quét bảo mật/load test**

Thêm dòng sau bullet `tools/check_kit.py`:
```markdown
- `skills/web-studio/templates/ci.yml`, `load-test.js` — mẫu CI (GitHub Actions, không phải CD — vẫn không tự deploy) và mẫu load test (k6); `web-tech-architect` điền cụ thể ở M0 (CI, quét bảo mật) và trước G4 khi có backend (load test).
```

- [ ] **Step 4: Sửa `README.md` mục "Giới hạn" — làm rõ CI không phải CD/không phải gate**

Thêm dòng:
```markdown
- CI có sẵn chỉ chạy khi chủ dự án tự push/mở PR lên git host; không phải điều kiện cổng Producer tự kiểm, và không tự deploy (CD vẫn do chủ dự án làm).
```

- [ ] **Step 5: Kiểm tích hợp cuối cùng**

Run: `python tools/check_kit.py`
Expected: `PASS: 9 agent + skill + 11 template`

Run: `python -m unittest discover -s tests -v`
Expected: `Ran 42 tests ... OK`

- [ ] **Step 6: Commit**

```bash
git add skills/web-studio/SKILL.md skills/web-studio/templates README.md
git commit -m "$(cat <<'EOF'
chore: bump kit version to 0.2.0 for quality-tooling upgrade

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

## Self-review (đã chạy)

- **Phạm vi spec → task:** §3.1–§3.4 (CI, 2 dòng bảo mật, load test, tiêu chí cổng) → Task 2–4; §3.5 (checker enforce) → Task 1; §5 toàn bộ danh sách file → khớp 1-1 với Task 1–5; quyết định "CI không phải gate" (§4) → Task 4 Step 4 + Global Constraints; không có mục nào của spec thiếu task.
- **Step scan:** mỗi step hoặc là lệnh chạy có output kỳ vọng cụ thể, hoặc là đoạn thay thế văn bản nguyên văn (không có step kiểu "thêm validation phù hợp" mơ hồ).
- **Type/string consistency:** 3 chuỗi bảng STUDIO.md, 2 chuỗi bảng ENGINEERING.md, 2 tên file, 3 hằng checker — dùng giống hệt nhau giữa Task 1 (định nghĩa), Task 2 (nội dung thật), Task 3/4 (tham chiếu bằng tên). `load test` cố ý viết thường xuyên suốt `SKILL.md` để khớp hằng checker (ghi rõ trong Global Constraints để không bị viết hoa nhầm ở Task 4).
- **Review Focus:** 5 mục đều có test hoặc giải thích rõ vì sao an toàn không cần test (CRLF/BOM) hoặc vì sao fail là dự kiến (chạy checker giữa chừng).
- **Tỉ lệ:** plan dài hơn spec vì mỗi đoạn thay thế văn bản cần trích nguyên văn "trước/sau" để không ai đoán sai dòng cần sửa — đổi lại, không có step nào chỉ nói "cập nhật cho đúng" mà không kèm nội dung chính xác.
