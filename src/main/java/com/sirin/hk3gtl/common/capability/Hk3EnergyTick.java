package com.sirin.hk3gtl.common.capability;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;

/**
 * 【变更记录 #1】2026-10-01 17:47:00（修订139）
 * 删除：无；新增：单次工作调用的能源撤销栈及推进后的事实回执。
 * 修改：失败逆序退还，只移除已完成的退款；失败票据保留重试，回执异常不退款已完成工作。
 * 用途：隔离每台机器的实际能源改量，不覆盖整账户快照，不宣称物品/流体事务。
 */
public final class Hk3EnergyTick {
    private enum State { OPEN, REFUNDING, REFUNDED, COMMITTED }
    private State state = State.OPEN;
    private final ArrayDeque<Runnable> refunds = new ArrayDeque<>();
    private final List<Runnable> receipts = new ArrayList<>();
    private RuntimeException failure;

    public void requireOpen() {
        if (state != State.OPEN) throw new IllegalStateException("能源工作票据已封账");
    }

    public void undoWith(Runnable refund) { requireOpen(); refunds.push(java.util.Objects.requireNonNull(refund)); }
    public void onCommit(Runnable receipt) { requireOpen(); receipts.add(java.util.Objects.requireNonNull(receipt)); }
    public boolean settled() { return state == State.REFUNDED || state == State.COMMITTED; }
    public RuntimeException failure() { return failure; }

    public void runWork(Runnable work, java.util.function.BooleanSupplier advanced) {
        requireOpen();
        try { work.run(); }
        finally { finish(advanced.getAsBoolean()); }
    }

    /** 只允许真实推进确认付款；没有推进时按逆序退款，失败保持原顺序等待重试。 */
    public boolean finish(boolean advanced) {
        if (settled()) return true;
        failure = null;
        if (advanced) {
            requireOpen();
            state = State.COMMITTED;
            refunds.clear();
            for (Runnable receipt : receipts) {
                try { receipt.run(); }
                catch (RuntimeException problem) { if (failure == null) failure = problem; }
            }
            receipts.clear();
            return true;
        }
        state = State.REFUNDING;
        receipts.clear();
        while (!refunds.isEmpty()) {
            try { refunds.peek().run(); }
            catch (RuntimeException problem) { failure = problem; return false; }
            refunds.pop();
        }
        state = State.REFUNDED;
        return true;
    }
}
