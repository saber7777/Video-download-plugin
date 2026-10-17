package demo;

/**
 * 改状态或改数量时锁住业务行，用版本条件更新，影响行数不是 1 就回滚。
 * 只通过动作改变状态，非法迁移抛出异常，同一事务写入新状态和状态日志。
 */
public class OrderService {
    private final OrderMapper mapper;
    private final OrderStateMachine machine;

    public OrderService(OrderMapper mapper, OrderStateMachine machine) {
        this.mapper = mapper;
        this.machine = machine;
    }

    @Transactional
    public void assign(long id, long assigneeId, int version) {
        WorkOrder current = mapper.selectForUpdate(id);
        machine.assertCan(current.status, OrderStateMachine.Status.ASSIGNED);
        int updated = mapper.casStatus(id, current.status, OrderStateMachine.Status.ASSIGNED, assigneeId, version);
        if (updated != 1) {
            throw new ConflictException("工单已被其他人更新");
        }
        mapper.insertLog(id, current.status, OrderStateMachine.Status.ASSIGNED, "assign");
    }
}
