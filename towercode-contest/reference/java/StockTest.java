public final class StockTest {
    public static void main(String[] args) {
        if (Stock.deduct(5, 2) != 3) {
            throw new AssertionError("扣减结果不对");
        }
        try {
            Stock.deduct(1, 2);
            throw new AssertionError("库存不足时必须失败");
        } catch (IllegalStateException expected) {
            if (!expected.getMessage().contains("库存不足")) {
                throw new AssertionError(expected.getMessage());
            }
        }
        System.out.println("stock ok");
    }
}
