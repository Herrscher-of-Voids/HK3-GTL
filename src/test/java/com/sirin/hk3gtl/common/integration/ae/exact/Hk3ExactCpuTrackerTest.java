package com.sirin.hk3gtl.common.integration.ae.exact;

import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;

/** 验证提交身份不跨线程泄漏及部分产量判定，不模拟原生CPU完成。 */
public final class Hk3ExactCpuTrackerTest {
    private static int checks;

    public static void main(String[] args) throws Exception {
        UUID outer = UUID.randomUUID(), inner = UUID.randomUUID();
        check(Hk3ExactCpuTracker.currentSubmission() == null, "默认无批次身份");
        Hk3ExactCpuTracker.submit(outer, () -> {
            check(outer.equals(Hk3ExactCpuTracker.currentSubmission()), "外层批次身份");
            try {
                Hk3ExactCpuTracker.submit(inner, () -> {
                    check(inner.equals(Hk3ExactCpuTracker.currentSubmission()), "内层批次身份");
                    throw new IllegalStateException("预期异常");
                });
            } catch (IllegalStateException expected) { }
            check(outer.equals(Hk3ExactCpuTracker.currentSubmission()), "异常恢复外层身份");
            AtomicReference<UUID> other = new AtomicReference<>(outer);
            Thread thread = new Thread(() -> other.set(Hk3ExactCpuTracker.currentSubmission()));
            thread.start();
            try { thread.join(); } catch (InterruptedException interrupted) { throw new AssertionError(interrupted); }
            check(other.get() == null, "其他线程不继承提交令牌");
            return null;
        });
        check(Hk3ExactCpuTracker.currentSubmission() == null, "提交完成释放线程引用");
        check(Hk3ExactCpuTracker.produced(100, 60, false, 0) == 40, "失败批次核销真实部分成品");
        check(Hk3ExactCpuTracker.produced(100, 60, false, 1) == -1, "取消后可能迟到产物必须待核对");
        check(Hk3ExactCpuTracker.produced(100, 0, true, 0) == 100, "成功批次核销全量");
        check(Hk3ExactCpuTracker.produced(Long.MAX_VALUE, 0) == Long.MAX_VALUE, "极大批量无回绕");
        check(Hk3ExactCpuTracker.produced(100, 101) == -1 && Hk3ExactCpuTracker.produced(100, -1) == -1
                && Hk3ExactCpuTracker.produced(0, 0) == -1, "无效原生进度不当零产量");
        System.out.println("大数批次身份与部分产量判定核验通过：" + checks + "项；未运行Mixin或真实CPU。");
    }

    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); checks++; }
}
