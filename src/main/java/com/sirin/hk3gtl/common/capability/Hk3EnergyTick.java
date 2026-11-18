package com.sirin.hk3gtl.common.capability;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;







public final class Hk3EnergyTick {
    private enum State { OPEN, REFUNDING, REFUNDED, COMMITTED }
    private State state = State.OPEN;
    private final ArrayDeque<Runnable> refunds = new ArrayDeque<>();
    private final List<Runnable> receipts = new ArrayList<>();
    private RuntimeException failure;
    private boolean finishing;
    private boolean checkpointPending;
    private final java.util.function.Consumer<List<Runnable>> checkpoint;

    public Hk3EnergyTick() { this(pending -> {}); }
    public Hk3EnergyTick(java.util.function.Consumer<List<Runnable>> checkpoint) {
        this.checkpoint = java.util.Objects.requireNonNull(checkpoint);
    }

    public static Hk3EnergyTick refunding(List<Runnable> pending,
                                         java.util.function.Consumer<List<Runnable>> checkpoint) {
        var tick = new Hk3EnergyTick(checkpoint);
        tick.refunds.addAll(pending);
        tick.state = State.REFUNDING;
        return tick;
    }

    public void requireOpen() {
        if (state != State.OPEN) throw new IllegalStateException("能源工作票据已封账");
    }

    public void undoWith(Runnable refund) { requireOpen(); refunds.push(java.util.Objects.requireNonNull(refund)); }
    public void onCommit(Runnable receipt) { requireOpen(); receipts.add(java.util.Objects.requireNonNull(receipt)); }
    public boolean settled() { return terminal() && !checkpointPending; }
    private boolean terminal() { return state == State.REFUNDED || state == State.COMMITTED; }
    public RuntimeException failure() { return failure; }

    public void runWork(Runnable work, java.util.function.BooleanSupplier advanced) {
        requireOpen();
        try { work.run(); }
        finally { finish(advanced.getAsBoolean()); }
    }

    /** 只允许真实推进确认付款；没有推进时按逆序退款，失败保持原顺序等待重试。 */
    public boolean finish(boolean advanced) {
        if (settled()) return true;
        if (finishing) return false;
        finishing = true;
        try {
            failure = null;
            if (!terminal() && advanced) {
                requireOpen();
                state = State.COMMITTED;
                refunds.clear();
                for (Runnable receipt : receipts) {
                    try { receipt.run(); }
                    catch (RuntimeException problem) { if (failure == null) failure = problem; }
                }
                receipts.clear();
            } else if (!terminal()) {
                state = State.REFUNDING;
                receipts.clear();
                while (!refunds.isEmpty()) {
                    try { refunds.peek().run(); }
                    catch (RuntimeException problem) { failure = problem; break; }
                    refunds.pop();
                }
                if (refunds.isEmpty()) state = State.REFUNDED;
            }
            checkpointPending = true;
            try { checkpoint.accept(List.copyOf(refunds)); checkpointPending = false; }
            catch (RuntimeException problem) { failure = problem; }
            return settled();
        } finally {
            // 日志失败只补存剩余状态，不重新执行已经完成的退款。
            finishing = false;
        }
    }
}
