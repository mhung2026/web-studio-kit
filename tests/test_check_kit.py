import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "tools"))

import check_kit  # noqa: E402
import sync_discipline  # noqa: E402

DISCIPLINE = (KIT / "tools" / "discipline.md").read_text(encoding="utf-8").strip()


def agent_text(name="demo-agent", tools="Read, Write, Skill, mcp__plugin_playwright_playwright",
               disallowed="Agent", model="sonnet", body_extra="", discipline=DISCIPLINE, skills=None):
    skills = check_kit.required_skills(name) if skills is None else skills
    skills_yaml = "skills:\n" + "".join(f"  - {s}\n" for s in skills) if skills else ""
    on_demand = "".join(f"- `{s}`\n" for s in check_kit.ON_DEMAND_SKILLS.get(name, []))
    return (
        "---\n"
        f"name: {name}\n"
        "description: Agent mẫu để test.\n"
        f"tools: {tools}\n"
        f"disallowedTools: {disallowed}\n"
        f"model: {model}\n"
        f"{skills_yaml}"
        "---\n\n"
        "## Vai trò\nx\n\n## Vùng ghi mặc định\nx\n\n## Cách làm\nx\n\n## Đầu ra\nx\n\n"
        f"## Skill hỗ trợ\n{on_demand}\n"
        f"{body_extra}\n\n{discipline}\n"
    )

class AgentChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, name, text, newline="\n", bom=False):
        path = self.tmp / f"{name}.md"
        data = text.replace("\n", newline).encode("utf-8")
        path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)
        return path

    def test_yaml_list_parsed_with_colons_in_items(self):
        fields, body = check_kit.parse_frontmatter(
            "---\nname: a\nskills:\n  - superpowers:x\n  - superpowers:y\nmodel: opus\n---\nbody\n")
        self.assertEqual(check_kit.split_list(fields["skills"]), ["superpowers:x", "superpowers:y"])
        self.assertEqual(fields["model"], "opus")
        self.assertEqual(body, "body\n")

    def test_list_item_without_key_rejected(self):
        with self.assertRaises(ValueError):
            check_kit.parse_frontmatter("---\n  - x\nname: a\n---\n")

    def test_skill_tool_required(self):
        path = self.write("demo-agent", agent_text(tools="Read, Write"))
        self.assertTrue(any("Skill" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_missing_default_preload_rejected(self):
        path = self.write("demo-agent", agent_text(skills=[]))
        self.assertTrue(any("verification-before-completion" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_disallowed_skill_rejected(self):
        skills = ["superpowers:verification-before-completion", "superpowers:brainstorming"]
        path = self.write("demo-agent", agent_text(skills=skills))
        self.assertTrue(any("brainstorming" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_role_preload_enforced(self):
        text = agent_text(name="backend-engineer", skills=["superpowers:verification-before-completion"],
                          body_extra="`studio/ENGINEERING.md`")
        path = self.write("backend-engineer", text)
        self.assertTrue(any("test-driven-development" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_on_demand_skill_must_be_mentioned(self):
        text = agent_text(name="backend-engineer", body_extra="`studio/ENGINEERING.md`")
        text = text.replace("- `superpowers:systematic-debugging`\n", "")
        path = self.write("backend-engineer", text)
        self.assertTrue(any("systematic-debugging" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_valid_agent_passes(self):
        path = self.write("demo-agent", agent_text())
        self.assertEqual(check_kit.check_agent(path, DISCIPLINE), [])

    def test_crlf_and_bom_accepted(self):
        path = self.write("demo-agent", agent_text(), newline="\r\n", bom=True)
        self.assertEqual(check_kit.check_agent(path, DISCIPLINE), [])

    def test_name_must_match_filename(self):
        path = self.write("demo-agent", agent_text(name="other"))
        self.assertTrue(any("name" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_unknown_tool_rejected(self):
        path = self.write("demo-agent", agent_text(tools="Read, Teleport"))
        self.assertTrue(any("Teleport" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_agent_tool_must_be_disallowed(self):
        path = self.write("demo-agent", agent_text(disallowed="WebSearch"))
        self.assertTrue(any("disallowedTools" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_bad_model_rejected(self):
        path = self.write("demo-agent", agent_text(model="gpt"))
        self.assertTrue(any("model" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_missing_heading_rejected(self):
        text = agent_text().replace("## Cách làm\n", "## Cach lam\n")
        path = self.write("demo-agent", text)
        self.assertTrue(any("Cách làm" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_altered_discipline_rejected(self):
        path = self.write("demo-agent", agent_text(discipline=DISCIPLINE.replace("NOT RUN", "SKIP")))
        self.assertTrue(any("Kỷ luật chung" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_unknown_template_reference_rejected(self):
        path = self.write("demo-agent", agent_text(body_extra="Dùng `studio/templates/khong-co.md`."))
        self.assertTrue(any("khong-co.md" in e for e in check_kit.check_agent(path, DISCIPLINE)))

    def test_missing_frontmatter_rejected(self):
        path = self.write("demo-agent", "## Vai trò\nx\n")
        self.assertTrue(any("frontmatter" in e for e in check_kit.check_agent(path, DISCIPLINE)))


class KitChecks(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "agents").mkdir()
        (self.root / "tools").mkdir()
        shutil.copy(KIT / "tools" / "discipline.md", self.root / "tools" / "discipline.md")
        tpl = self.root / "skills" / "web-studio" / "templates"
        tpl.mkdir(parents=True)
        for name in check_kit.TEMPLATES:
            snippets = "\n".join(check_kit.TEMPLATE_SNIPPETS.get(name, []))
            (tpl / name).write_text(f'Kit-version: 9.9.9\nLệnh `none`: không ai được báo "pass".\n{snippets}\n',
                                    encoding="utf-8")
        for name in check_kit.EXPECTED_AGENTS:
            extra = "Đọc `studio/ENGINEERING.md`." if name in check_kit.ENGINEERING_AGENTS else ""
            (self.root / "agents" / f"{name}.md").write_text(agent_text(name=name, body_extra=extra), encoding="utf-8")
        mentions = "\n".join(f"- `{n}`" for n in check_kit.EXPECTED_AGENTS)
        (self.root / "skills" / "web-studio" / "SKILL.md").write_text(
            "---\nname: web-studio\ndescription: Producer.\n---\n\n"
            f"{mentions}\n\n" + "\n".join(f"`{s}`" for s in check_kit.PRODUCER_SKILLS) + "\n\n"
            + "\n".join(check_kit.REQUIRED_SKILL_SNIPPETS) + "\n\n## Tiếp tục sau gián đoạn\nx\n"
            "Mẫu: `templates/ticket.md`.\nKit-version: 9.9.9\n"
            "Mọi phiếu chạm code đã có hành vi đang chạy phải qua `impact-analyst` trước.\n",
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_discipline_must_restrict_skills_to_listed_ones(self):
        path = self.root / "tools" / "discipline.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(check_kit.DISCIPLINE_SNIPPETS[0], "x"), encoding="utf-8")
        self.assertTrue(any("discipline.md" in e for e in check_kit.check_kit(self.root)))

    def test_ticket_template_must_have_tdd_exception_field(self):
        path = self.root / "skills" / "web-studio" / "templates" / "ticket.md"
        path.write_text("Kit-version: 9.9.9\n", encoding="utf-8")
        self.assertTrue(any("ticket.md" in e and "Ngoại lệ TDD" in e for e in check_kit.check_kit(self.root)))

    def test_skill_must_override_superpowers_defaults(self):
        skill = self.root / "skills" / "web-studio" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("docs/superpowers", "x"), encoding="utf-8")
        self.assertTrue(any("docs/superpowers" in e for e in check_kit.check_kit(self.root)))

    def test_engineering_agents_must_reference_standards(self):
        path = self.root / "agents" / "backend-engineer.md"
        path.write_text(path.read_text(encoding="utf-8").replace("studio/ENGINEERING.md", "x"), encoding="utf-8")
        self.assertTrue(any("ENGINEERING" in e and "backend-engineer" in e for e in check_kit.check_kit(self.root)))

    def test_cli_failure_output_survives_cp1252_console(self):
        (self.root / "agents" / "web-release-manager.md").unlink()
        buffer = io.BytesIO()
        original = sys.stdout
        console = io.TextIOWrapper(buffer, encoding="cp1252")
        sys.stdout = console
        try:
            code = check_kit.main(["--root", str(self.root)])
            console.flush()
            output = buffer.getvalue()
        finally:
            sys.stdout = original
            console.detach()
        self.assertEqual(code, 1)
        self.assertIn(b"web-release-manager", output)

    def test_studio_template_none_check_needs_guidance_not_just_word(self):
        (self.root / "skills" / "web-studio" / "templates" / "STUDIO.md").write_text(
            "Kit-version: 9.9.9\n| Test | none | . |\n", encoding="utf-8")
        self.assertTrue(any("STUDIO.md" in e for e in check_kit.check_kit(self.root)))

    def test_kit_version_must_match_between_skill_and_templates(self):
        (self.root / "skills" / "web-studio" / "templates" / "ENGINEERING.md").write_text(
            "Kit-version: 1.0.0\n", encoding="utf-8")
        self.assertTrue(any("Kit-version" in e and "ENGINEERING.md" in e for e in check_kit.check_kit(self.root)))

    def test_skill_without_kit_version_rejected(self):
        skill = self.root / "skills" / "web-studio" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("Kit-version: 9.9.9", ""), encoding="utf-8")
        self.assertTrue(any("Kit-version" in e for e in check_kit.check_kit(self.root)))

    def test_skill_must_mention_producer_skills(self):
        skill = self.root / "skills" / "web-studio" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("`superpowers:writing-plans`", ""), encoding="utf-8")
        self.assertTrue(any("writing-plans" in e for e in check_kit.check_kit(self.root)))

    def test_complete_kit_passes(self):
        self.assertEqual(check_kit.check_kit(self.root), [])

    def test_missing_agent_reported(self):
        (self.root / "agents" / "web-release-manager.md").unlink()
        self.assertTrue(any("web-release-manager" in e for e in check_kit.check_kit(self.root)))

    def test_unexpected_agent_reported(self):
        (self.root / "agents" / "extra.md").write_text(agent_text(name="extra"), encoding="utf-8")
        self.assertTrue(any("extra" in e for e in check_kit.check_kit(self.root)))

    def test_underscore_files_ignored(self):
        (self.root / "agents" / "_notes.md").write_text("ghi chú", encoding="utf-8")
        self.assertEqual(check_kit.check_kit(self.root), [])

    def test_only_limits_scope(self):
        (self.root / "agents" / "web-release-manager.md").unlink()
        self.assertEqual(check_kit.check_kit(self.root, only=["web-qa-engineer"]), [])

    def test_skill_missing_template_reported(self):
        (self.root / "skills" / "web-studio" / "templates" / "adr.md").unlink()
        self.assertTrue(any("adr.md" in e for e in check_kit.check_kit(self.root)))

    def test_skill_must_mention_every_agent(self):
        skill = self.root / "skills" / "web-studio" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("`web-release-manager`", "`x`"), encoding="utf-8")
        self.assertTrue(any("web-release-manager" in e for e in check_kit.check_kit(self.root)))

    def test_skill_must_check_write_zone(self):
        skill = self.root / "skills" / "web-studio" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("--untracked-files=all", ""), encoding="utf-8")
        self.assertTrue(any("porcelain" in e for e in check_kit.check_kit(self.root)))

    def test_skill_must_have_resume_section(self):
        skill = self.root / "skills" / "web-studio" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("## Tiếp tục sau gián đoạn", "## Khác"), encoding="utf-8")
        self.assertTrue(any("Tiếp tục sau gián đoạn" in e for e in check_kit.check_kit(self.root)))

    def test_studio_template_must_explain_none(self):
        (self.root / "skills" / "web-studio" / "templates" / "STUDIO.md").write_text("x", encoding="utf-8")
        self.assertTrue(any("STUDIO.md" in e for e in check_kit.check_kit(self.root)))

    def test_skill_must_require_impact_analyst_before_touching_existing_code(self):
        skill = self.root / "skills" / "web-studio" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("`impact-analyst`", "`x`"), encoding="utf-8")
        self.assertTrue(any("impact-analyst" in e for e in check_kit.check_kit(self.root)))


class SyncDiscipline(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "agents").mkdir()
        (self.root / "tools").mkdir()
        (self.root / "tools" / "discipline.md").write_text("## Kỷ luật chung\n1. Mới.\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_replaces_old_block_and_keeps_body(self):
        path = self.root / "agents" / "a.md"
        old = "---\nname: a\n---\n\n## Vai trò\nx\n\n## Kỷ luật chung\n1. Cũ.\n"
        path.write_bytes(old.replace("\n", "\r\n").encode("utf-8"))
        changed = sync_discipline.sync(self.root)
        text = path.read_text(encoding="utf-8")
        self.assertEqual(changed, ["a.md"])
        self.assertIn("## Vai trò\nx\n", text)
        self.assertNotIn("Cũ", text)
        self.assertTrue(text.endswith("## Kỷ luật chung\n1. Mới.\n"))

    def test_appends_block_when_missing_and_is_idempotent(self):
        path = self.root / "agents" / "b.md"
        path.write_text("---\nname: b\n---\n\n## Vai trò\nx\n", encoding="utf-8")
        self.assertEqual(sync_discipline.sync(self.root), ["b.md"])
        self.assertEqual(sync_discipline.sync(self.root), [])
        self.assertEqual(path.read_text(encoding="utf-8").count("## Kỷ luật chung"), 1)


if __name__ == "__main__":
    unittest.main()
