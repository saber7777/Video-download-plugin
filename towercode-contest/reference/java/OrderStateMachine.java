import java.util.Arrays;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.Map;
import java.util.Set;

/** 只通过动作改变状态，非法迁移抛出异常，同一事务写入新状态和状态日志。 */
public final class OrderStateMachine {
    public enum Status {
        DRAFT, SUBMITTED, ASSIGNED, IN_PROGRESS, DONE, REJECTED, CANCELLED
    }

    private final Map<Status, Set<Status>> edges = new EnumMap<>(Status.class);

    public OrderStateMachine() {
        allow(Status.DRAFT, Status.SUBMITTED, Status.CANCELLED);
        allow(Status.SUBMITTED, Status.ASSIGNED, Status.REJECTED, Status.CANCELLED);
        allow(Status.ASSIGNED, Status.IN_PROGRESS, Status.CANCELLED);
        allow(Status.IN_PROGRESS, Status.DONE, Status.CANCELLED);
        allow(Status.REJECTED, Status.DRAFT);
        allow(Status.DONE);
        allow(Status.CANCELLED);
    }

    private void allow(Status from, Status... to) {
        edges.put(from, to.length == 0 ? EnumSet.noneOf(Status.class) : EnumSet.copyOf(Arrays.asList(to)));
    }

    public boolean can(Status from, Status to) {
        return from != null && to != null && edges.getOrDefault(from, Set.of()).contains(to);
    }

    public void assertCan(Status from, Status to) {
        if (!can(from, to)) {
            throw new IllegalStateException("非法状态迁移: " + from + " -> " + to);
        }
    }
}
