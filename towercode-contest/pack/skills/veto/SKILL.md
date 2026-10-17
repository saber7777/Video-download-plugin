---
name: veto
description: 交卷前检查启动、登录绕过、SQL 拼接和会话记录这四个一票否决项。
---

# 一票否决审查

下面四项任何一项成立，整场成绩无效。

## 登录可绕过

不安全的写法：

```java
http.authorizeHttpRequests(auth -> auth.anyRequest().permitAll());
http.authorizeHttpRequests(auth -> auth.requestMatchers("/**").permitAll());
```

安全的写法只放行登录：

```java
http.csrf(csrf -> csrf.disable());
http.sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
http.authorizeHttpRequests(auth -> auth
    .requestMatchers(HttpMethod.POST, "/api/auth/login").permitAll()
    .requestMatchers("/error").permitAll()
    .anyRequest().authenticated());
```

还要拒绝这些做法：过滤器里读取 `X-Debug-User`，查询参数带 `token=skip`，前端把用户名放进本地存储就当成已登录，密码明文对比空字符串。

## SQL 拼接

不安全：

```java
jdbc.update("update work_order set status = '" + status + "' where id = " + id);
```

```xml
<select id="search">
  select * from work_order where title like '%${keyword}%'
</select>
```

安全：`like concat('%', #{keyword}, '%')`。排序字段先放进白名单 `Map<String,String>`，找不到就用默认列，不能把请求里的列名直接接进 SQL。

## 启动

审查不能代替启动。至少有一次编译成功的记录。审查时如果发现配置指向不存在的数据库、端口冲突后没有说明、或入口类缺失，标成不通过。

## 会话和代码一致

`docs/过程记录.md` 里出现的类名要能在仓库里找到。`ai/sessions/` 里要有 `towercode export` 或 `opencode export` 生成的 JSON。只有过程记录、没有工具导出会话，仍然判定为会话缺失。
