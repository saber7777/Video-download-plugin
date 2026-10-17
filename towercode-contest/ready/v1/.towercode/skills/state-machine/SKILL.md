---
name: state-machine
description: 用显式迁移表实现状态机，只暴露动作接口，非法迁移在服务层拒绝并保持原状态。
---

# 状态机与一致性

只通过动作改变状态，非法迁移抛出异常，同一事务写入新状态和状态日志。

状态名以需求分析为准。题面没有规定时，使用这一组和迁移，并在需求分析里声明：

- `DRAFT` 可以提交到 `SUBMITTED`，或取消到 `CANCELLED`
- `SUBMITTED` 可以派单到 `ASSIGNED`，驳回到 `REJECTED`，或取消
- `ASSIGNED` 可以开始到 `IN_PROGRESS`，或取消
- `IN_PROGRESS` 可以办结到 `DONE`，或取消
- `REJECTED` 可以改回 `DRAFT`
- `DONE` 和 `CANCELLED` 不能再迁移

```java
public void assertCan(Status from, Status to) {
    if (!edges.getOrDefault(from, Set.of()).contains(to)) {
        throw new IllegalStateException("非法状态迁移: " + from + " -> " + to);
    }
}
```

接口按动作拆开，例如 `/api/orders/{id}/submit`、`/assign`、`/start`、`/finish`、`/reject`、`/cancel`。不要提供 `PUT /api/orders/{id}/status`，请求体里直接传目标状态。

前端按钮和动作一一对应。后端重新计算目标状态，不信任前端传来的目标状态。状态日志和主表更新在同一个事务里。非法迁移时主表、数量和日志都保持原样。
