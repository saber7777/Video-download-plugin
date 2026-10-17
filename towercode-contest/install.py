#!/usr/bin/env python3
"""Install the contest agent pack into a TowerCode / OpenCode project.

TowerCode follows the same layout as OpenCode 1.x: Markdown agents under
.opencode/agents, skills under .opencode/skills, commands under
.opencode/commands, plus AGENTS.md. A .towercode mirror is written beside
it for a renamed fork. Pass --schema v2 only if the app rejects v1 files.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "pack"

V1_BASH_TO_V2 = {"bash": "shell", "task": "subagent"}


def load_agent(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["id"] = path.stem
    return data


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def permission_rules(permission: dict) -> list[tuple[str, str, str]]:
    rules: list[tuple[str, str, str]] = []
    for action, value in permission.items():
        mapped = V1_BASH_TO_V2.get(action, action)
        if isinstance(value, str):
            rules.append((mapped, "*", value))
        elif isinstance(value, dict):
            for resource, effect in value.items():
                rules.append((mapped, str(resource), str(effect)))
        else:
            raise SystemExit(f"unsupported permission value for {action}")
    return rules


def frontmatter_v1(agent: dict) -> str:
    lines = ["---", f"description: {yaml_quote(agent['description'])}", f"mode: {agent['mode']}"]
    if "temperature" in agent:
        lines.append(f"temperature: {agent['temperature']}")
    if "color" in agent:
        lines.append(f"color: {yaml_quote(agent['color'])}")
    permission = agent.get("permission") or {}
    if permission:
        lines.append("permission:")
        for action, value in permission.items():
            if isinstance(value, str):
                lines.append(f"  {action}: {value}")
            else:
                lines.append(f"  {action}:")
                for resource, effect in value.items():
                    lines.append(f"    {yaml_quote(str(resource))}: {effect}")
    tools = agent.get("tools") or {}
    if tools:
        lines.append("tools:")
        for name, enabled in tools.items():
            lines.append(f"  {name}: {'true' if enabled else 'false'}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def frontmatter_v2(agent: dict) -> str:
    lines = ["---", f"description: {yaml_quote(agent['description'])}", f"mode: {agent['mode']}"]
    if "temperature" in agent:
        lines.append(f"temperature: {agent['temperature']}")
    rules = permission_rules(agent.get("permission") or {})
    for name, enabled in (agent.get("tools") or {}).items():
        if not enabled:
            rules.append((name, "*", "deny"))
    if rules:
        lines.append("permissions:")
        for action, resource, effect in rules:
            lines.append(f"  - action: {action}")
            lines.append(f"    resource: {yaml_quote(resource)}")
            lines.append(f"    effect: {effect}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def render_agent(agent: dict, schema: str) -> str:
    prompt = (PACK / "prompts" / f"{agent['id']}.md").read_text(encoding="utf-8").strip() + "\n"
    header = frontmatter_v1(agent) if schema == "v1" else frontmatter_v2(agent)
    return header + "\n" + prompt


def write_file(path: Path, text: str, dry_run: bool) -> None:
    if dry_run:
        print(f"write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_tree(src: Path, dest: Path, dry_run: bool) -> None:
    for item in sorted(src.rglob("*")):
        if not item.is_file():
            continue
        target = dest / item.relative_to(src)
        if dry_run:
            print(f"write {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(item, target)


def layout(schema: str) -> tuple[Path, Path]:
    # OpenCode 1.0 loads .opencode/agent and .opencode/command.
    # The plural names are a later layout, and 1.0 rejects them as typos.
    if schema == "v1":
        return Path(".opencode/agent"), Path(".opencode/command")
    return Path(".opencode/agents"), Path(".opencode/commands")


def install(target: Path, schema: str, dry_run: bool) -> list[Path]:
    config_name = "opencode.v1.json" if schema == "v1" else "opencode.v2.json"
    config = (PACK / "root" / config_name).read_text(encoding="utf-8")
    agents = [load_agent(path) for path in sorted((PACK / "agents").glob("*.json"))]
    agent_dir, command_dir = layout(schema)
    written: list[Path] = []

    def emit(rel: Path, text: str | None = None, src: Path | None = None) -> None:
        dest = target / rel
        written.append(dest)
        if text is not None:
            write_file(dest, text, dry_run)
        elif src is not None:
            if dry_run:
                print(f"write {dest}")
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest)

    emit(Path("AGENTS.md"), src=PACK / "root" / "AGENTS.md")
    emit(Path("opencode.json"), text=config)
    emit(Path("docs/contest-rules.md"), src=PACK / "root" / "docs" / "contest-rules.md")
    copy_tree(PACK / "templates", target / "docs" / "templates", dry_run)
    copy_tree(PACK / "skills", target / ".opencode" / "skills", dry_run)
    for skill in sorted((PACK / "skills").glob("*/SKILL.md")):
        emit(Path("docs/skills") / f"{skill.parent.name}.md", src=skill)
    for command in sorted((PACK / "commands").glob("*.md")):
        emit(command_dir / command.name, src=command)

    for agent in agents:
        body = render_agent(agent, schema)
        emit(agent_dir / f"{agent['id']}.md", text=body)

    if not dry_run:
        mirror = target / ".towercode"
        source = target / ".opencode"
        if mirror.exists():
            shutil.rmtree(mirror)
        shutil.copytree(source, mirror)
    else:
        print(f"mirror {target / '.opencode'} -> {target / '.towercode'}")
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install contest agents for TowerCode / OpenCode")
    parser.add_argument("--target", type=Path, required=True, help="project directory that will be opened in TowerCode")
    parser.add_argument("--schema", choices=("v1", "v2"), default="v1")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    target = args.target.resolve()
    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)
    install(target, args.schema, args.dry_run)
    if not args.dry_run:
        print(f"installed schema={args.schema} into {target}")
        print("open that directory in TowerCode, start a new session, and switch the agent to contest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
