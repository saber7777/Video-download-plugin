---
description: 主路径跑通后打包 JAR、前端产物和会话记录
agent: verifier
---

在主路径已经跑通的前提下收口，不要重写业务。

1. 后端打可执行 JAR，复制到 `dist/app.jar`。不要复制 `.jar.original`。
2. 前端构建产物放到 `dist/frontend/`。
3. 核对 `db/schema.sql`、`db/data.sql`、四份文档、`ai/sessions/`、`screenshots/`。
4. 导出会话：先 `towercode session list` 或 `opencode session list`，再 `export <会话ID>` 到 `ai/sessions/`。
5. 缺什么就列出。可以补部署说明里的命令，不能编造没有实际运行的测试结果。
