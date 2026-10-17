---
name: transaction
description: 用短事务、行锁和版本条件实现并发更新，数量不足时整单回滚。
---

# 事务与并发控制

改状态或改数量时锁住业务行，用版本条件更新，影响行数不是 1 就回滚。

```java
@Transactional
public void assign(long id, long assigneeId, int version) {
    WorkOrder current = mapper.selectForUpdate(id);
    machine.assertCan(current.getStatus(), Status.ASSIGNED);
    int updated = mapper.casStatus(id, current.getStatus(), Status.ASSIGNED, assigneeId, version);
    if (updated != 1) {
        throw new ConflictException("工单已被其他人更新");
    }
    mapper.insertLog(id, current.getStatus(), Status.ASSIGNED, "assign");
}
```

对应 SQL 只使用预编译参数：

```xml
<select id="selectForUpdate" resultType="WorkOrder">
  select id, status, version, assignee_id
  from work_order
  where id = #{id}
  for update
</select>

<update id="casStatus">
  update work_order
  set status = #{toStatus},
      assignee_id = #{assigneeId},
      version = version + 1,
      updated_at = now()
  where id = #{id}
    and status = #{fromStatus}
    and version = #{version}
</update>
```

扣减数量用受影响行数表达“够不够”，不要先查再在 Java 里减：

```xml
<update id="deduct">
  update spare_part
  set qty = qty - #{need}
  where id = #{id}
    and qty >= #{need}
</update>
```

返回 0 就抛异常。因为它和状态更新在同一个 `@Transactional` 里，异常会让整单回滚。

不要把事务标在 private 方法上再在同一个类里自调用，Spring 不会代理这次调用。事务放在对外的服务方法上。不要在事务里发 HTTP 请求或等待用户输入。
