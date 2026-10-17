你只编写 `db/schema.sql` 和 `db/data.sql`。不要写 Java、XML 或 Vue。

先读已经确认的 `docs/需求分析.md`。表和字段跟那份文档走，不跟示例名称走。机制不能换：

- MySQL 8，InnoDB，utf8mb4。
- 业务单号列有唯一约束。
- 业务主表有 `status` 和 `version`。
- 有 `biz_no_seq(biz_code, biz_date, current_value)`，主键是 `biz_code + biz_date`。
- 状态变化有日志表，至少记录来源状态、目标状态、动作、操作者、时间。
- 会扣减的数量列有非负约束；真正的并发保护仍在更新语句里做。
- 外键把主从关系标清楚。需要查询的状态、单号、所属人加索引。
- 演示用户的密码是 BCrypt，不要明文。说明里写清用户名和初始口令。
- `data.sql` 只放跑通主路径需要的少量数据。

写完后用一段话解释每张表的职责，然后停止，等参赛者确认。不要生成后端。
