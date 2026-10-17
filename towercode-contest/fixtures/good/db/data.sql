-- 演示账号 admin / Tower@2026 ，password_hash 是 BCrypt，不是明文。
insert into sys_user (id, username, password_hash, display_name, role_code, enabled)
values (1, 'admin', '$2a$10$Ngqnb3OACjYRn0uj7fjbNuEJ9ScP8Hl8uugkDcbcSDrSIC5epwGwO', '管理员', 'ADMIN', 1);

insert into spare_part (id, part_name, qty)
values (1, '电源模块', 2);
