# TowerCode 竞赛代理

信息院 AI Coding 比赛统一使用 TowerCode，技术栈是 Java Spring Boot 单体、Vue 3 和 MySQL。内置的 Build / Plan 是通用编程代理，不知道一票否决，也不知道单号、事务和状态机要怎么写。这份目录把主控换成针对评分表的 `contest` 代理，并配上只做一件事的子代理。

准备环境里没有 TowerCode 安装包，不能代替你在考场软件里点一次。代理格式按 OpenCode 1.0.180 核对过，TowerCode 若是同一套配置，把练习目录打开就能用。若它不认这套文件，改用 `PASTE.md`，规则仍然生效。

## 上场前要装上

练习目录随便选一个空文件夹，不要装进无关项目：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target D:\exam\practice
```

```bash
./install.sh /path/to/practice
```

安装后该目录会有：

- `AGENTS.md`：所有代理都会读，包括内置 Build。
- `opencode.json`：关闭网页抓取，并把规则文件放进始终生效的说明。OpenCode 1.0 没有“默认代理”这个字段，新会话可能仍显示 Build，用 Tab 切到 `contest`。
- `.opencode/agent/`、`.opencode/command/`，以及一份同内容的 `.towercode/`。1.0 把复数目录当成拼写错误，所以不要改成 `agents`。另有 8 份技能说明在 `docs/skills/`，没有技能工具时也会被读到。

用这个目录打开 TowerCode，新建会话。窗口里的代理名应是 `contest`。如果还是 Build，用 Tab 切换。v1 文件若导致软件报配置错误，执行 `install.ps1 -Target <目录> -Schema v2`。没有 Python 时，复制 `ready/v1` 里的内容到练习目录，再把其中的 `.opencode` 复制为 `.towercode`。

## 代理分别干什么

| 代理 | 作用 |
| --- | --- |
| contest | 主控。按阶段推进，每阶段停下来等你确认 |
| analyst | 只写需求分析 |
| schema | 只写 `schema.sql` 和 `data.sql` |
| backend | 登录、事务、单号、状态机 |
| frontend | 可见中文按钮，不伪造保存成功 |
| security | 只读检查四个否决项 |
| verifier | 真跑编译和接口，没跑的写成未测 |

命令：`/contest-start`、`/self-check`、`/pack-submit`。

技能里写死了比赛要用的机制，避免临场自由发挥：

- 单号是 `biz_no_seq` 上的 `LAST_INSERT_ID`，同一事务插入业务行，禁止 `select max + 1`。
- 改状态或改数量时加事务、`for update` 和 `version`，失败整单回滚。
- 只有动作接口，没有随意改状态的接口。
- 登录只放行 `POST /api/auth/login`。
- SQL 只用 `#{}`。

`fixtures/good` 是这套机制的最小样本。`reference/java` 里的状态机和库存判断可以单独编译运行。

## 考场上的第一句话

输入 `/contest-start`，换行后贴题面。它应该只写需求分析并停下。它要是开始生成工程，就发：`停。先等我确认状态机、单号和按钮。`

自定义代理没有出现时，改贴 `PASTE.md`。

三小时的节奏、赛前六条探针和 90 分钟模拟题分别在 `PLAYBOOK.md`、`TEST-PLAN.md`、`PRACTICE.md`。

## 交卷前

```bash
towercode session list
towercode export <会话ID> > ai/sessions/<会话ID>.json
python grade.py <题目目录>
```

命令若叫 `opencode`，把上面两条里的名字换掉。`grade.py` 不是官方评分器。退出码 2 表示文件里已经能看出登录绕过、SQL 拼接或缺少会话，正式比赛里这三项都会让成绩无效。退出码 0 仍然要求你亲眼看到程序启动，并且错误密码登不进去。

## 为什么不继续用内置 Build

Build 会写代码，但比赛另有 10 分看人机协同和核验，还有四条一票否决。通用代理常见的失败是：还没理解题面就开始生成、用 `select max + 1` 取号、做一个通用改状态接口、为了省事放开登录、用 `${}` 做排序。探针 D 和 B 就是用来抓住后两种的。内置代理若在这两条上不合格，就换成 `contest`。

赛场只允许 TowerCode。这份配置是赛前放进指定工具里的代理和规则，不是另一个 AI 产品。正式比赛时不要再开其他编程助手或搜索引擎。
