---
name: submission
description: 按固定目录打包 JAR、前端产物、SQL、文档、会话记录和截图。
---

# 提交目录

```text
backend/
frontend/
dist/app.jar
dist/frontend/
db/schema.sql
db/data.sql
docs/需求分析.md
docs/自测报告.md
docs/部署说明.md
docs/过程记录.md
ai/sessions/
screenshots/
```

后端打包：

```bash
mvn -o -DskipTests package
```

复制 Spring Boot 重新打包出来的可执行 JAR，文件名通常不带 `.original`。放到 `dist/app.jar`。

前端构建后，把构建目录的内容放到 `dist/frontend/`。不要只提交 `node_modules`。

导出会话：

```bash
towercode session list
towercode export <会话ID> > ai/sessions/<会话ID>.json
```

命令如果叫 `opencode`，换成 `opencode session list` 和 `opencode export`。桌面版如果有导出按钮，导出的文件也放进 `ai/sessions/`。

截图至少包括：登录页、登录后的列表、新建成功、一次状态动作成功、一次被拒绝的非法操作。文件放进 `screenshots/`，自测报告用同样的文件名引用。

不要把 `.opencode/node_modules`、`.towercode/node_modules` 打进提交包。那是工具第一次打开目录时自己装的运行库，不是答卷。

交卷前在项目根目录执行：

```bash
python grade.py .
```

环境没有这份脚本时，按 `docs/templates/自测报告.md` 的否决清单逐项肉眼核对。闸门失败就不要把目录交上去。
