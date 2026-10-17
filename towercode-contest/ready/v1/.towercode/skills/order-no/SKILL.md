---
name: order-no
description: 用序列表和 LAST_INSERT_ID 在并发下生成不重复业务单号，禁止 select max+1。
---

# 单号并发生成

用序列表行上的 LAST_INSERT_ID 取号，同一事务里插入业务行，业务单号有唯一约束。

表：

```sql
create table biz_no_seq (
  biz_code varchar(32) not null,
  biz_date char(8) not null,
  current_value int not null,
  primary key (biz_code, biz_date)
) engine=InnoDB default charset=utf8mb4;
```

同一条 JDBC 连接、同一个 Spring 事务里执行两条语句：

```sql
insert into biz_no_seq (biz_code, biz_date, current_value)
values (#{bizCode}, #{bizDate}, last_insert_id(1))
on duplicate key update current_value = last_insert_id(current_value + 1);

select last_insert_id();
```

业务单号形如 `前缀 + yyyyMMdd + 6 位数字`。前缀和位数以题面为准。业务表给单号加唯一索引。

不要这样做：

- `select max(current_value)` 或 `select max(order_no)` 再加一。两个事务会读到同一个值。
- 只在 JVM 里 `synchronized` 或使用 `AtomicLong`。评分环境可能只看数据库，进程内锁也不能防止重启重复。
- 给取号方法标 `REQUIRES_NEW`。那会换成另一条连接，`last_insert_id()` 读到的不是刚才那次更新。
- 用 UUID 代替题面要求的可读单号。

取号和插入业务行放在同一个 `@Transactional` 方法里，方法里不要调用外部接口。失败时序列和业务行一起回滚，不会发出重号。允许跳号的说法只适用于事务已提交之后业务又被人工删除的情况，代码不要主动跳号。

类注释就使用本节第一句。
