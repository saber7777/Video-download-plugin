# 赛前怎么测 TowerCode

这台准备环境里没有 TowerCode 程序，测不到你们考场那一份安装包。下面这组探针是在你自己的 Windows 上对真实 TowerCode 做的。每条探针单独开一个新会话，避免上一轮把答案喂给它。

先对内置 Build 测一遍，再安装本目录的代理，对 `contest` 测一遍。同一条探针，内置代理错了、竞赛代理做对了，就用竞赛代理上场。

## 安装

在题目练习目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target D:\exam\practice
```

没有 Python 时，把 `ready\v1` 里的 `AGENTS.md`、`opencode.json`、`docs`、`.opencode` 复制到练习目录，再把 `.opencode` 复制一份为 `.towercode`。不要把 `agent` 或 `command` 改成复数。

用该目录打开 TowerCode。OpenCode 1.0 的新会话默认仍是 Build，用 Tab 切到 `contest`。切过去之后，系统提示里应出现“一票否决”。只停留在 Build 也可以，因为 `AGENTS.md` 和 `docs/skills` 对它同样生效，但 `contest` 会强制按阶段停下来。

## 六条探针

探针原文在 `probes/`。

| 探针 | 合格 | 不合格 |
| --- | --- | --- |
| A 分析 | 只写状态机、单号、按钮，然后停止 | 直接生成半个项目 |
| B 单号 | `biz_no_seq` 加 `LAST_INSERT_ID`，并拒绝 `select max + 1` | UUID、Redis，或先查最大值再加一 |
| C 状态 | 按动作拆接口；非法迁移不改数据库 | 一个可以随便改状态的接口 |
| D 登录 | 拒绝放开登录，说明这会一票否决 | 答应 `permitAll` 或先不做登录 |
| E SQL | 排序字段走白名单，SQL 里只有 `#{}` | `${}` 或把列名拼进 `order by` |
| F 收口 | 列出 JAR、前端产物、两份 SQL、文档和 `export` 命令 | 只说把源码打个 zip |

内置 Build 在 D 上答应放开登录，或者在 B 上使用 `select max + 1`，就不要带着它进考场。这两条分别对应整场无效和后端失分。

## 工具本身还要确认的事

这些和代理好坏无关，但会决定你能不能交卷。

- TowerCode 的模型请求在考场白名单里能通。赛前用练习目录走完一条最短会话。
- 命令行如果叫 `towercode`，确认有 `session list` 和 `export`。如果只有桌面导出按钮，练习一次并把文件放进 `ai/sessions/`。
- `mvn -o -DskipTests package` 和前端构建在环境包里能离线完成。不能的话，赛前把缺的构件装进本地仓库，不要等比赛当天才下载。
- 自定义代理没出现时，先看 `opencode.json` 有没有报错。报不认识的字段，就只保留能打开软件的那一版；规则仍在 `AGENTS.md` 里。v1 不被接受时，用 `install.ps1 -Schema v2` 再装一次。

## 一次压缩演练

用 `PRACTICE.md` 的模拟题限时 90 分钟。演练结束跑：

```powershell
python grade.py D:\exam\practice
```

退出码 0 只说明否决项和三条机制在文件里能看见，不能代替你亲眼看到的启动和登录。演练里没启动成功，就先解决环境，不要再调提示词。
