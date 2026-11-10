package com.sirin.hk3gtl.common.recipe.power;

import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import java.math.BigInteger;
import java.util.List;

/**
 * 【文件职责】多个现有能源缓冲仓的精确分摊和可重试退款，不覆盖仓室余额快照。
 * 【变更记录 #1】2026-10-17 16:43:35（第1次备注 · 修订165）
 * 删除：无；新增：纯支付端口、余额预检、实际改量核对及部分退款余量。
 * 修改：金额使用BigInteger，每个端口仅处理自身可支付量；用途：任一仓拒付或工作失败均不留下净扣款。
 */
/**
 * 【变更记录 #2】2026-10-17 16:55:08（第2次备注 · 修订165）
 * 删除：余额已改后回调抛错可能漏登记退款的缺口。
 * 新增：携带真实改量的失败回执，部分退款余量保存在撤销项内；修改：失败不封账、不重复退已还金额。
 * 用途：多仓中途拒付、实际IO失败和退款重试均以真实净改量结算。
 */
/**
 * 【变更记录 #3】2026-11-04 22:10:32（第3次备注 · 内测5修订201）
 * 删除：非法实际改量在登记撤销前抛错而遗失余额变更的顺序。
 * 新增：超额扣款和意外加款的带符号撤销；修改：先登记非零真实差量，再拒绝异常支付。
 * 用途：监听器造成回执异常时仍精确抵消已知变更，部分撤销保留余量；不改变批准费用。
 */
/**
 * 【变更记录 #4】2026-11-04 22:14:54（第4次备注 · 内测5修订201）
 * 删除：异常退款改量校验前遗漏余量更新的路径。
 * 新增：每次退款先按真实改量递减待退差额，再校验符号和范围；修改：异常票据暂停并重试带符号余量。
 * 用途：反向部分退款只撤销真实净变化，不重复抵消已发生的余额改量。
 */
public final class Hk3PortPayment {
    private Hk3PortPayment() {}
    public interface Port {
        BigInteger available();
        BigInteger power();
        BigInteger change(BigInteger delta);
    }
    public static final class ChangeFailure extends RuntimeException {
        private final BigInteger actual;
        public ChangeFailure(BigInteger actual, RuntimeException cause) { super(cause); this.actual = actual; }
    }
    public static BigInteger available(List<Port> ports) {
        return ports.stream().map(Port::available).reduce(BigInteger.ZERO, BigInteger::add);
    }
    public static BigInteger power(List<Port> ports) {
        return ports.stream().map(Port::power).reduce(BigInteger.ZERO, BigInteger::add);
    }
    public static boolean pay(List<Port> ports, BigInteger cost, Hk3EnergyTick tick) {
        tick.requireOpen();
        if (cost.signum() <= 0 || available(ports).compareTo(cost) < 0 || power(ports).compareTo(cost) < 0) return false;
        BigInteger left = cost;
        for (Port port : ports) {
            BigInteger take = left.min(port.available().max(BigInteger.ZERO));
            if (take.signum() == 0) continue;
            BigInteger changed;
            boolean failed = false;
            try { changed = port.change(take.negate()); }
            catch (ChangeFailure problem) { changed = problem.actual; failed = true; }
            if (changed.signum() != 0) tick.undoWith(new Refund(port, changed.negate()));
            if (changed.signum() > 0 || changed.negate().compareTo(take) > 0)
                throw new IllegalStateException("能源仓返回非法实际改量");
            BigInteger paid = changed.negate();
            if (failed || !paid.equals(take)) return false;
            left = left.subtract(paid);
            if (left.signum() == 0) return true;
        }
        return false;
    }
    private static final class Refund implements Runnable {
        private final Port port;
        private BigInteger left;
        private Refund(Port port, BigInteger paid) { this.port = port; this.left = paid; }
        @Override public void run() {
            if (left.signum() == 0) return;
            BigInteger requested = left;
            BigInteger restored;
            boolean failed = false;
            try { restored = port.change(requested); }
            catch (ChangeFailure problem) { restored = problem.actual; failed = true; }
            left = left.subtract(restored);
            if (failed || (restored.signum() != 0 && restored.signum() != requested.signum())
                    || restored.abs().compareTo(requested.abs()) > 0)
                throw new IllegalStateException("能源仓返回非法退款改量");
            if (left.signum() != 0) throw new IllegalStateException("能源仓退款容量不足，保持暂停等待重试");
        }
    }
}
