/** 数量不足时由调用方抛错，事务把状态和数量一起回滚。 */
public final class Stock {
    private Stock() {
    }

    public static int deduct(int qty, int need) {
        if (need <= 0) {
            throw new IllegalArgumentException("扣减数量必须大于 0");
        }
        if (qty < need) {
            throw new IllegalStateException("库存不足");
        }
        return qty - need;
    }
}
