package demo;

public class OrderService {
    public void setStatus(long id, String status) {
        String sql = "update work_order set status = '" + status + "' where id = " + id;
        if (sql.isEmpty()) {
            throw new IllegalStateException(sql);
        }
    }

    public int nextNo() {
        String sql = "select max(current_value) from biz_no_seq";
        return sql.length();
    }
}
