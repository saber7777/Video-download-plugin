---
name: environment
description: 在写代码前检查 JDK、Maven、Node、MySQL 和本地依赖，避免考场离线时下载新库。
---

# 环境

考场网络只放行指定模型接口。把 `npm install` 或 Maven 下载当成默认步骤，会卡到比赛结束。

先做这些只读检查：

- `java -version`
- `mvn -v`，没有 mvn 就在环境包目录里找
- `node -v` 和 `npm -v`
- `mysql --version`，或看题目给出的主机、端口、库名
- 项目里是否已有 `pom.xml`、`package.json`、现成的 `src`

依赖规则：

- 已有骨架时，沿用它的 Spring Boot、持久化框架和 UI 库。
- 没有骨架时，只用本地 Maven 仓库里已经存在的 Spring Boot、MyBatis、Spring Security、MySQL 驱动。
- 编译优先加离线参数：`mvn -o -DskipTests package`。离线失败再看缺的是哪一个构件，不要换一套框架。
- 前端同理。环境里有 Element Plus 就用它；没有就用题目模板，不要临时换组件库。

把检查结果写进 `docs/过程记录.md` 的第一段：实际命令、版本、哪些依赖是本地已有的。
