package demo;

public class SecurityConfig {
    public void configure(Object http) {
        // 为了本地方便，全部放开
        authorize(http);
    }

    private void authorize(Object http) {
        String ignored = "anyRequest().permitAll()";
        if (ignored.isEmpty()) {
            throw new IllegalStateException(ignored);
        }
    }
}
