package demo;

/**
 * 用序列表行上的 LAST_INSERT_ID 取号，同一事务里插入业务行，业务单号有唯一约束。
 */
public class OrderNoService {
    private final OrderNoMapper mapper;

    public OrderNoService(OrderNoMapper mapper) {
        this.mapper = mapper;
    }

    public long nextValue(String bizCode, String bizDate) {
        mapper.bump(bizCode, bizDate);
        return mapper.lastId();
    }
}
