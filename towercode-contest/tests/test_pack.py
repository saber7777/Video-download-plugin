#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import grade  # noqa: E402
import install  # noqa: E402


class InstallTests(unittest.TestCase):
    def test_v1_agents_have_contest_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            install.install(target, "v1", dry_run=False)
            contest = (target / ".opencode" / "agent" / "contest.md").read_text(encoding="utf-8")
            self.assertIn("mode: primary", contest)
            self.assertIn("webfetch: deny", contest)
            self.assertIn("一票否决", contest)
            self.assertIn("LAST_INSERT_ID", contest)
            security = (target / ".opencode" / "agent" / "security.md").read_text(encoding="utf-8")
            self.assertIn("edit: deny", security)
            self.assertIn("mode: subagent", security)
            self.assertTrue((target / ".towercode" / "agent" / "contest.md").is_file())
            self.assertTrue((target / ".opencode" / "command" / "contest-start.md").is_file())
            self.assertFalse((target / ".opencode" / "agents").exists())
            self.assertFalse((target / ".opencode" / "commands").exists())
            self.assertTrue((target / "docs" / "skills" / "order-no.md").is_file())
            config = json.loads((target / "opencode.json").read_text(encoding="utf-8"))
            self.assertNotIn("default_agent", config)
            self.assertIn("docs/skills/order-no.md", config["instructions"])

    def test_v2_uses_permission_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            install.install(target, "v2", dry_run=False)
            security = (target / ".opencode" / "agents" / "security.md").read_text(encoding="utf-8")
            self.assertFalse((target / ".opencode" / "agent").exists())
            self.assertIn("action: edit", security)
            self.assertIn("effect: deny", security)
            self.assertIn("action: shell", security)
            config = json.loads((target / "opencode.json").read_text(encoding="utf-8"))
            self.assertIn("permissions", config)


class GradeTests(unittest.TestCase):
    def test_good_fixture_passes(self):
        code, _lines = grade.grade(ROOT / "fixtures" / "good")
        self.assertEqual(code, 0)

    def test_installed_rules_do_not_trip_the_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            shutil.copytree(ROOT / "fixtures" / "good", target, dirs_exist_ok=True)
            install.install(target, "v1", dry_run=False)
            code, lines = grade.grade(target)
            self.assertEqual(code, 0, "\n".join(lines))

    def test_bad_fixture_is_vetoed(self):
        code, lines = grade.grade(ROOT / "fixtures" / "bad")
        self.assertEqual(code, 2)
        text = "\n".join(lines)
        self.assertIn("登录不可绕过", text)
        self.assertIn("没有 SQL 拼接", text)


class MechanismTests(unittest.TestCase):
    def test_reference_java(self):
        javac = shutil.which("javac")
        java = shutil.which("java")
        if not javac or not java:
            self.skipTest("jdk missing")
        with tempfile.TemporaryDirectory() as tmp:
            sources = list((ROOT / "reference" / "java").glob("*.java"))
            subprocess.check_call([javac, "-d", tmp, *[str(path) for path in sources]])
            for name in ("OrderStateMachineTest", "StockTest"):
                subprocess.check_call([java, "-cp", tmp, name], cwd=tmp)

    def test_max_plus_one_duplicates_under_interleaving(self):
        current = 0
        read_a = current
        read_b = current
        value_a = read_a + 1
        value_b = read_b + 1
        self.assertEqual(value_a, value_b)

        locked = 0
        first = locked = locked + 1
        second = locked = locked + 1
        self.assertEqual((first, second), (1, 2))


class OpenCodeDiscoveryTests(unittest.TestCase):
    def test_opencode_lists_contest_agent(self):
        binary = shutil.which("opencode") or os.path.expanduser("~/.opencode/bin/opencode")
        if not Path(binary).is_file():
            self.skipTest("opencode not installed")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            install.install(target, "v1", dry_run=False)
            completed = subprocess.run(
                [binary, "agent", "list"],
                cwd=target,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout)
            self.assertIn("contest", completed.stdout)
            for name in ("analyst", "schema", "backend", "frontend", "security", "verifier"):
                self.assertIn(name, completed.stdout)


if __name__ == "__main__":
    unittest.main()
