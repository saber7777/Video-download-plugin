create table sys_user (
  id bigint primary key,
  username varchar(64) not null,
  password_hash varchar(100) not null,
  display_name varchar(64) not null,
  role_code varchar(32) not null,
  enabled tinyint not null default 1,
  unique key uk_user_username (username)
) engine=InnoDB default charset=utf8mb4;

create table biz_no_seq (
  biz_code varchar(32) not null,
  biz_date char(8) not null,
  current_value int not null,
  primary key (biz_code, biz_date)
) engine=InnoDB default charset=utf8mb4;

create table work_order (
  id bigint not null auto_increment primary key,
  order_no varchar(32) not null,
  title varchar(200) not null,
  status varchar(32) not null,
  version int not null default 0,
  assignee_id bigint null,
  created_by bigint not null,
  created_at datetime not null,
  updated_at datetime not null,
  unique key uk_work_order_no (order_no),
  key idx_work_order_status (status),
  constraint fk_work_order_assignee foreign key (assignee_id) references sys_user (id)
) engine=InnoDB default charset=utf8mb4;

create table work_order_log (
  id bigint not null auto_increment primary key,
  order_id bigint not null,
  from_status varchar(32) not null,
  to_status varchar(32) not null,
  action_code varchar(32) not null,
  operator_id bigint not null,
  created_at datetime not null,
  constraint fk_log_order foreign key (order_id) references work_order (id)
) engine=InnoDB default charset=utf8mb4;

create table spare_part (
  id bigint primary key,
  part_name varchar(100) not null,
  qty int not null,
  constraint chk_spare_qty check (qty >= 0)
) engine=InnoDB default charset=utf8mb4;
