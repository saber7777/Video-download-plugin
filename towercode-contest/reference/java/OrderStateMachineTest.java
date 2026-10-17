public final class OrderStateMachineTest {
    public static void main(String[] args) {
        OrderStateMachine machine = new OrderStateMachine();
        expect(machine.can(OrderStateMachine.Status.DRAFT, OrderStateMachine.Status.SUBMITTED), "草稿可以提交");
        expect(!machine.can(OrderStateMachine.Status.DRAFT, OrderStateMachine.Status.DONE), "草稿不能直接办结");
        expect(!machine.can(OrderStateMachine.Status.DONE, OrderStateMachine.Status.CANCELLED), "已办结不能再取消");
        try {
            machine.assertCan(OrderStateMachine.Status.IN_PROGRESS, OrderStateMachine.Status.ASSIGNED);
            throw new AssertionError("非法迁移没有被拒绝");
        } catch (IllegalStateException expected) {
            if (!expected.getMessage().contains("非法状态迁移")) {
                throw new AssertionError(expected.getMessage());
            }
        }
        System.out.println("state machine ok");
    }

    private static void expect(boolean value, String message) {
        if (!value) {
            throw new AssertionError(message);
        }
    }
}
