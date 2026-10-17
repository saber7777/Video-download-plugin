#!/usr/bin/env python3
"""Pre-submit gate for the AI Coding contest.

This is not the official scorer. It catches the four disqualifying mistakes
that can be seen from the tree, and checks that the three backend mechanisms
are actually present. Exit 0 means the gate passed. Exit 2 means a veto item
failed. Exit 1 means the veto items passed but a required mechanism is missing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CODE_SUFFIXES = {".java", ".xml", ".sql", ".vue", ".js", ".ts", ".yml", ".yaml"}
SQL_WORDS = ("select", "update", "insert", "delete", "where")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def iter_code(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".opencode", ".towercode", "node_modules", "target", "dist"} for part in path.parts):
            continue
        if "docs/templates" in path.as_posix() or "docs/skills" in path.as_posix():
            continue
        if path.suffix.lower() in CODE_SUFFIXES:
            yield path


def collapsed(text: str) -> str:
    return "".join(text.split())


def find_auth_bypass(root: Path) -> list[str]:
    hits: list[str] = []
    needles = (
        "anyRequest().permitAll()",
        'requestMatchers("/**").permitAll()',
        'requestMatchers("**").permitAll()',
        'antMatchers("/**").permitAll()',
        'antMatchers("**").permitAll()',
        "web.ignoring()",
        "X-Debug-User",
    )
    for path in iter_code(root):
        text = read_text(path)
        flat = collapsed(text)
        for needle in needles:
            if collapsed(needle) in flat:
                hits.append(f"{path.relative_to(root)} 含有 {needle}")
    return hits


def find_sql_concat(root: Path) -> list[str]:
    hits: list[str] = []
    for path in iter_code(root):
        if path.suffix.lower() == ".vue":
            continue
        text = read_text(path)
        if "${" in text:
            hits.append(f"{path.relative_to(root)} 含有 MyBatis ${{}} 或字符串插值")
        for lineno, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            if "+" in line and any(word in low for word in SQL_WORDS) and ("'" in line or '"' in line):
                hits.append(f"{path.relative_to(root)}:{lineno} 疑似把变量拼进 SQL")
                break
    return hits


def tree_has(root: Path, predicate) -> bool:
    for path in iter_code(root):
        if predicate(read_text(path).lower()):
            return True
    return False


def session_ok(root: Path) -> bool:
    folder = root / "ai" / "sessions"
    if not folder.is_dir():
        return False
    for path in folder.rglob("*"):
        if path.is_file() and path.stat().st_size > 20:
            return True
    return False


def report(ok: bool, title: str, detail: str) -> str:
    mark = "通过" if ok else "不通过"
    return f"[{mark}] {title}：{detail}"


def grade(root: Path) -> tuple[int, list[str]]:
    lines: list[str] = []
    veto = False

    required = [
        Path("db/schema.sql"),
        Path("db/data.sql"),
        Path("docs/需求分析.md"),
        Path("docs/自测报告.md"),
        Path("docs/过程记录.md"),
        Path("docs/部署说明.md"),
    ]
    missing = [str(path) for path in required if not (root / path).is_file()]
    lines.append(report(not missing, "提交文件", "齐全" if not missing else "缺少 " + "、".join(missing)))

    auth = find_auth_bypass(root)
    sql = find_sql_concat(root)
    session = session_ok(root)
    if auth:
        veto = True
    if sql:
        veto = True
    if not session:
        veto = True
    lines.append(report(not auth, "登录不可绕过", "未发现放行全部请求的配置" if not auth else "；".join(auth)))
    lines.append(report(not sql, "没有 SQL 拼接", "未发现 ${} 或拼接 SQL" if not sql else "；".join(sql)))
    lines.append(report(session, "会话记录", "ai/sessions 里有导出文件" if session else "ai/sessions 为空或不存在，正式评分会一票否决"))

    schema = read_text(root / "db/schema.sql").lower()
    schema_ok = all(token in schema for token in ("innodb", "utf8mb4", "unique", "status", "version", "biz_no_seq"))
    lines.append(report(schema_ok, "库表机制", "schema 含 InnoDB、utf8mb4、唯一约束、status、version、biz_no_seq" if schema_ok else "schema 缺少 InnoDB / utf8mb4 / unique / status / version / biz_no_seq 之一"))

    last_id = tree_has(root, lambda text: "last_insert_id" in text)
    max_plus = tree_has(root, lambda text: "max(" in text and "biz_no_seq" in text)
    order_ok = last_id and not max_plus
    lines.append(report(order_ok, "单号并发生成", "使用 LAST_INSERT_ID，且没有在序列表上 select max" if order_ok else "要使用 LAST_INSERT_ID，不要 select max"))

    transactional = tree_has(root, lambda text: "@transactional" in text)
    locked = tree_has(root, lambda text: "for update" in text or "version" in text)
    tx_ok = transactional and locked
    lines.append(report(tx_ok, "事务与并发", "有 @Transactional，且有 for update 或 version" if tx_ok else "缺少 @Transactional，或没有 for update / version"))

    machine = tree_has(root, lambda text: "enum" in text and ("assertcan" in text or "can(" in text) and "illegalstateexception" in text)
    lines.append(report(machine, "状态机", "有枚举、迁移判断和非法迁移异常" if machine else "没有可执行的状态迁移判断"))

    analysis = read_text(root / "docs/需求分析.md")
    analysis_ok = "状态机" in analysis and "单号" in analysis
    lines.append(report(analysis_ok, "需求分析", "写了状态机和单号" if analysis_ok else "需求分析里要明确状态机和单号规则"))

    frontend = ""
    frontend_root = root / "frontend"
    if frontend_root.exists():
        frontend = "\n".join(read_text(path) for path in frontend_root.rglob("*") if path.is_file())
    click_ok = all(label in frontend for label in ("登录", "查询", "新建"))
    lines.append(report(click_ok, "页面按钮文案", "前端能看到登录、查询、新建" if click_ok else "按钮要用可见中文：登录、查询、新建，以及题面要求的动作"))

    hard_missing = not (schema_ok and order_ok and tx_ok and machine and analysis_ok and click_ok and not missing)
    if veto:
        return 2, lines
    if hard_missing:
        return 1, lines
    return 0, lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a contest submission tree")
    parser.add_argument("project", type=Path)
    args = parser.parse_args(argv)
    root = args.project.resolve()
    if not root.is_dir():
        print(f"目录不存在：{root}", file=sys.stderr)
        return 2
    code, lines = grade(root)
    print(f"项目：{root}")
    print("\n".join(lines))
    if code == 0:
        print("交卷闸门：通过。还要在本机真正启动一次，确认登录和主路径。")
    elif code == 2:
        print("交卷闸门：不通过。上面的否决项不修，正式成绩会无效。")
    else:
        print("交卷闸门：否决项暂过，但机制或文档还不齐，不建议交卷。")
    return code


if __name__ == "__main__":
    sys.exit(main())
