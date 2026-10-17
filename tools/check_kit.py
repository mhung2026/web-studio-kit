#!/usr/bin/env python3
"""Kiểm cấu trúc web-studio-kit: agent, skill Producer và template."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_AGENTS = [
    "product-owner", "web-design-auditor", "web-tech-architect", "impact-analyst",
    "backend-engineer", "frontend-engineer", "web-ux-designer", "web-qa-engineer",
    "web-release-manager",
]
TEMPLATES = [
    "STUDIO.md", "STATUS.md", "BACKLOG.md", "DECISIONS_PENDING.md", "ticket.md",
    "report.md", "adr.md", "milestone-report.md", "impact-report.md",
    "DEPLOY_GUIDE.md", "ENGINEERING.md",
]
EXTRA_TEMPLATE_FILES = ["ci.yml", "load-test.js"]
KNOWN_TOOLS = {
    "Read", "Write", "Edit", "Grep", "Glob", "Bash", "PowerShell", "WebFetch",
    "WebSearch", "NotebookEdit", "TodoWrite", "Skill",
}
ALLOWED_MODELS = {"opus", "sonnet", "haiku", "fable", "inherit"}
REQUIRED_HEADINGS = ["## Vai trò", "## Vùng ghi mặc định", "## Cách làm", "## Đầu ra", "## Skill hỗ trợ", "## Kỷ luật chung"]
REQUIRED_SKILL_SNIPPETS = [
    "git status --porcelain --untracked-files=all",
    "docs/superpowers",  # Producer phải ghi đè nơi lưu mặc định của brainstorming/writing-plans
    "SAST",
    "load test",
]
DISCIPLINE_SNIPPETS = ["Chỉ gọi skill có trong mục \"Skill hỗ trợ\" của mình"]
TEMPLATE_SNIPPETS = {"ticket.md": ["Ngoại lệ TDD"], "STUDIO.md": ["dependency", "SAST"]}
NONE_GUIDANCE = "không ai được báo \"pass\""
KIT_VERSION_RE = re.compile(r"^Kit-version:\s*(\S+)\s*$", re.M)
REQUIRED_SKILL_HEADINGS = ["## Tiếp tục sau gián đoạn"]
DESCRIPTION_MAX = 400
ENGINEERING_AGENTS = {"web-tech-architect", "backend-engineer", "frontend-engineer", "web-qa-engineer", "impact-analyst"}
ENGINEERING_REF = "studio/ENGINEERING.md"
IMPACT_SNIPPET = "impact-analyst"
IMPACT_PHRASE_HINT = "hành vi đang chạy"
TDD = "superpowers:test-driven-development"
VERIFY = "superpowers:verification-before-completion"
DEBUG = "superpowers:systematic-debugging"
RECEIVE_REVIEW = "superpowers:receiving-code-review"
AGENT_SKILLS = {TDD, VERIFY, DEBUG, RECEIVE_REVIEW}
DEFAULT_PRELOAD = [VERIFY]
PRELOAD_SKILLS = {
    "backend-engineer": [TDD, VERIFY],
    "frontend-engineer": [TDD, VERIFY],
    "web-qa-engineer": [VERIFY, DEBUG],
}
ON_DEMAND_SKILLS = {
    "backend-engineer": [DEBUG, RECEIVE_REVIEW],
    "frontend-engineer": [DEBUG, RECEIVE_REVIEW],
    "web-qa-engineer": [TDD],
    "web-tech-architect": [TDD, RECEIVE_REVIEW],
    "impact-analyst": [DEBUG],
}
PRODUCER_SKILLS = [
    "superpowers:brainstorming", "superpowers:writing-plans", "superpowers:dispatching-parallel-agents",
    DEBUG, RECEIVE_REVIEW, VERIFY, "superpowers:finishing-a-development-branch",
]


def required_skills(name):
    return PRELOAD_SKILLS.get(name, DEFAULT_PRELOAD)


def read_text(path):
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        raise ValueError("thiếu frontmatter (file phải bắt đầu bằng ---)")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter không có dòng --- đóng")
    fields = {}
    list_key = None
    for line in text[4:end].split("\n"):
        if not line.strip():
            continue
        item = re.match(r"^\s+-\s+(.+?)\s*$", line)
        if item:
            if list_key is None:
                raise ValueError(f"mục danh sách không thuộc khóa nào: {line!r}")
            fields[list_key] = ", ".join(v for v in (fields[list_key], item.group(1)) if v)
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"dòng frontmatter không hợp lệ: {line!r}")
        fields[key.strip()] = value.strip()
        list_key = key.strip() if not value.strip() else None
    return fields, text[end + 5:]


def split_list(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def has_heading(body, heading):
    return re.search(rf"^{re.escape(heading)}\s*$", body, re.M) is not None


def template_refs(body, prefix):
    return re.findall(rf"{re.escape(prefix)}([\w.-]+\.md)", body)


def check_agent(path, discipline):
    try:
        fields, body = parse_frontmatter(read_text(path))
    except ValueError as exc:
        return [f"{path.name}: {exc}"]
    errors = []
    if fields.get("name") != path.stem:
        errors.append(f"{path.name}: name '{fields.get('name')}' phải trùng tên file '{path.stem}'")
    description = fields.get("description", "")
    if not description:
        errors.append(f"{path.name}: thiếu description")
    elif len(description) > DESCRIPTION_MAX:
        errors.append(f"{path.name}: description dài {len(description)} > {DESCRIPTION_MAX} ký tự")
    if fields.get("model") not in ALLOWED_MODELS:
        errors.append(f"{path.name}: model '{fields.get('model')}' không thuộc {sorted(ALLOWED_MODELS)}")
    tools = split_list(fields.get("tools", ""))
    if not tools:
        errors.append(f"{path.name}: phải khai báo tools tường minh")
    for tool in tools:
        if tool == "Agent":
            errors.append(f"{path.name}: không được cấp tool Agent")
        elif tool not in KNOWN_TOOLS and not tool.startswith("mcp__"):
            errors.append(f"{path.name}: tool không hợp lệ '{tool}'")
    if "Agent" not in split_list(fields.get("disallowedTools", "")):
        errors.append(f"{path.name}: disallowedTools phải chứa Agent")
    if "Skill" not in tools:
        errors.append(f"{path.name}: tools phải có Skill (dự phòng khi skill chưa được nạp sẵn)")
    skills = split_list(fields.get("skills", ""))
    for skill in skills:
        if skill not in AGENT_SKILLS:
            errors.append(f"{path.name}: skill không dùng cho agent '{skill}'")
    for skill in required_skills(path.stem):
        if skill not in skills:
            errors.append(f"{path.name}: thiếu skill nạp sẵn bắt buộc '{skill}'")
    for skill in ON_DEMAND_SKILLS.get(path.stem, []):
        if f"`{skill}`" not in body:
            errors.append(f"{path.name}: mục Skill hỗ trợ phải nhắc skill tự gọi `{skill}`")
    for heading in REQUIRED_HEADINGS:
        if not has_heading(body, heading):
            errors.append(f"{path.name}: thiếu mục '{heading}'")
    if discipline not in body:
        errors.append(f"{path.name}: khối '## Kỷ luật chung' không khớp nguyên văn tools/discipline.md")
    if path.stem in ENGINEERING_AGENTS and ENGINEERING_REF not in body:
        errors.append(f"{path.name}: agent kỹ thuật phải tham chiếu {ENGINEERING_REF}")
    for ref in template_refs(body, "studio/templates/"):
        if ref not in TEMPLATES:
            errors.append(f"{path.name}: tham chiếu template không tồn tại '{ref}'")
    return errors


def check_skill(root):
    skill_dir = root / "skills" / "web-studio"
    skill_path = skill_dir / "SKILL.md"
    if not skill_path.exists():
        return ["skills/web-studio/SKILL.md: không tồn tại"]
    errors = []
    try:
        fields, body = parse_frontmatter(read_text(skill_path))
    except ValueError as exc:
        return [f"SKILL.md: {exc}"]
    if fields.get("name") != "web-studio":
        errors.append("SKILL.md: name phải là web-studio")
    if not fields.get("description"):
        errors.append("SKILL.md: thiếu description")
    for agent in EXPECTED_AGENTS:
        if f"`{agent}`" not in body:
            errors.append(f"SKILL.md: không nhắc tới agent `{agent}`")
    for skill in PRODUCER_SKILLS:
        if f"`{skill}`" not in body:
            errors.append(f"SKILL.md: thiếu skill hỗ trợ của Producer `{skill}`")
    for snippet in REQUIRED_SKILL_SNIPPETS:
        if snippet not in body:
            errors.append(f"SKILL.md: thiếu nội dung bắt buộc `{snippet}`")
    if IMPACT_SNIPPET not in body or IMPACT_PHRASE_HINT not in body:
        errors.append(f"SKILL.md: phải nhắc `{IMPACT_SNIPPET}` cùng cụm '{IMPACT_PHRASE_HINT}' (bắt buộc trước khi sửa code đã có hành vi đang chạy)")
    for heading in REQUIRED_SKILL_HEADINGS:
        if not has_heading(body, heading):
            errors.append(f"SKILL.md: thiếu mục '{heading}'")
    templates_dir = skill_dir / "templates"
    for name in TEMPLATES:
        if not (templates_dir / name).exists():
            errors.append(f"templates/{name}: không tồn tại")
    for name in EXTRA_TEMPLATE_FILES:
        if not (templates_dir / name).exists():
            errors.append(f"templates/{name}: không tồn tại")
    for ref in set(template_refs(body, "templates/")):
        if ref not in TEMPLATES:
            errors.append(f"SKILL.md: tham chiếu template lạ '{ref}'")
    for name, snippets in TEMPLATE_SNIPPETS.items():
        path = templates_dir / name
        for snippet in snippets:
            if path.exists() and snippet not in read_text(path):
                errors.append(f"templates/{name}: thiếu mục '{snippet}'")
    studio_tpl = templates_dir / "STUDIO.md"
    if studio_tpl.exists() and NONE_GUIDANCE not in read_text(studio_tpl):
        errors.append("templates/STUDIO.md: phải có câu hướng dẫn `none` (không ai được báo \"pass\")")
    errors.extend(check_kit_versions(body, templates_dir))
    return errors


def kit_version(text):
    match = KIT_VERSION_RE.search(text)
    return match.group(1) if match else None


def check_kit_versions(skill_body, templates_dir):
    version = kit_version(skill_body)
    if not version:
        return ["SKILL.md: thiếu dòng `Kit-version: X.Y.Z`"]
    errors = []
    for name in TEMPLATES:
        path = templates_dir / name
        if path.exists() and kit_version(read_text(path)) != version:
            errors.append(f"templates/{name}: Kit-version phải là {version}")
    return errors


def check_kit(root, only=None):
    discipline = read_text(root / "tools" / "discipline.md").strip()
    errors = [f"tools/discipline.md: thiếu câu '{s}'" for s in DISCIPLINE_SNIPPETS if s not in discipline]
    agents_dir = root / "agents"
    present = {p.stem: p for p in agents_dir.glob("*.md") if not p.name.startswith("_")}
    names = only if only else EXPECTED_AGENTS
    for name in names:
        if name in present:
            errors.extend(check_agent(present[name], discipline))
        elif not only:
            errors.append(f"agents/{name}.md: thiếu agent")
        else:
            errors.append(f"agents/{name}.md: không tồn tại")
    if not only:
        for extra in sorted(set(present) - set(EXPECTED_AGENTS)):
            errors.append(f"agents/{extra}.md: agent ngoài danh sách EXPECTED_AGENTS")
        errors.extend(check_skill(root))
    return errors


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--only", help="danh sách agent cách nhau bởi dấu phẩy")
    args = parser.parse_args(argv)
    only = split_list(args.only) if args.only else None
    errors = check_kit(args.root.resolve(), only)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"{len(errors)} lỗi.")
        return 1
    scope = ", ".join(only) if only else f"{len(EXPECTED_AGENTS)} agent + skill + {len(TEMPLATES)} template"
    print(f"PASS: {scope}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
