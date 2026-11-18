package com.sirin.hk3gtl.common.recipe.power;

import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import net.minecraft.nbt.CompoundTag;
import java.math.BigInteger;
import java.util.List;

 





 





 





 





public final class Hk3PortPayment {
    private Hk3PortPayment() {}
    public interface Port {
        BigInteger available();
        BigInteger power();
        BigInteger change(BigInteger delta);
        default CompoundTag refundTarget() { return null; }
        default Hk3RefundJournal.Action refund(BigInteger applied) { return new Refund(this, applied.negate()); }
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
            if (changed.signum() != 0) tick.undoWith(port.refund(changed));
            if (changed.signum() > 0 || changed.negate().compareTo(take) > 0)
                throw new IllegalStateException("能源仓返回非法实际改量");
            BigInteger paid = changed.negate();
            if (failed || !paid.equals(take)) return false;
            left = left.subtract(paid);
            if (left.signum() == 0) return true;
        }
        return false;
    }
    public static Runnable refund(Port port, BigInteger left) { return new Refund(port, left); }

    private static final class Refund implements Hk3RefundJournal.Action {
        private final Port port;
        private BigInteger left;
        private Refund(Port port, BigInteger paid) { this.port = port; this.left = paid; }
        @Override public CompoundTag snapshot() {
            var tag = new CompoundTag();
            var target = port.refundTarget();
            if (target == null) {
                tag.putString("Kind", "unsupported");
                tag.putString("Class", port.getClass().getName());
            } else {
                tag.putString("Kind", "port");
                tag.put("Target", target.copy());
                tag.putString("Left", left.toString());
            }
            return tag;
        }
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
