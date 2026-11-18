package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.Objects;
import java.util.UUID;

/** 只记录大数父订单与真实子任务回执，不猜测CPU完成状态。 */
public final class Hk3ExactOrder {
    public static final int MAX_DECIMAL_DIGITS = 512;
    private static final BigInteger MAX_TOTAL = BigInteger.TEN.pow(MAX_DECIMAL_DIGITS).subtract(BigInteger.ONE);

    public enum State { READY, RUNNING, PAUSED, CANCELLED, COMPLETE }

    public record Snapshot(UUID orderId, UUID owner, BigInteger total, BigInteger completed,
                           BigInteger activeAmount, UUID activeToken, State state) {}

    private final UUID orderId;
    private final UUID owner;
    private final BigInteger total;
    private BigInteger completed;
    private BigInteger activeAmount;
    private UUID activeToken;
    private State state;

    public Hk3ExactOrder(UUID orderId, UUID owner, BigInteger total) {
        this(new Snapshot(orderId, owner, total, BigInteger.ZERO, BigInteger.ZERO, null, State.READY), false);
    }

    private Hk3ExactOrder(Snapshot snapshot, boolean restoring) {
        validate(snapshot);
        orderId = snapshot.orderId();
        owner = snapshot.owner();
        total = snapshot.total();
        completed = snapshot.completed();
        activeAmount = snapshot.activeAmount();
        activeToken = snapshot.activeToken();
        state = restoring && snapshot.state() != State.COMPLETE && snapshot.state() != State.CANCELLED
                ? State.PAUSED : snapshot.state();
    }

    /** 恢复后等待真实回执或人工恢复，不能把未知在途任务重发一遍。 */
    public static Hk3ExactOrder restore(Snapshot snapshot) {
        return new Hk3ExactOrder(snapshot, true);
    }

    public synchronized Snapshot snapshot() {
        return new Snapshot(orderId, owner, total, completed, activeAmount, activeToken, state);
    }

    public synchronized BigInteger remaining() { return total.subtract(completed); }

    public synchronized UUID beginBatch(long amount) {
        if (state != State.READY || activeToken != null) throw new IllegalStateException("订单尚不可开始下一批");
        BigInteger requested = BigInteger.valueOf(amount);
        if (requested.signum() <= 0 || requested.compareTo(remaining()) > 0) {
            throw new IllegalArgumentException("子批数量必须为正数且不能超过余量");
        }
        activeAmount = requested;
        activeToken = UUID.randomUUID();
        state = State.RUNNING;
        return activeToken;
    }

    /** 旧入口只适用于已确认整批成功或确定零产出的失败。 */
    public synchronized boolean finish(UUID token, boolean success) {
        return finish(token, success, success ? activeAmount : BigInteger.ZERO);
    }

    /** 只核销匹配回执的真实目标产出；失败或取消也不能丢掉部分完成量。 */
    public synchronized boolean finish(UUID token, boolean success, BigInteger produced) {
        if (activeToken == null || !activeToken.equals(token)) return false;
        if (produced == null || produced.signum() < 0 || produced.compareTo(activeAmount) > 0
                || success && !produced.equals(activeAmount)) {
            throw new IllegalArgumentException("回执产出必须在子批范围内，成功回执必须足量");
        }
        completed = completed.add(produced);
        activeAmount = BigInteger.ZERO;
        activeToken = null;
        if (state != State.CANCELLED) {
            if (completed.equals(total)) state = State.COMPLETE;
            else if (!success || state == State.PAUSED) state = State.PAUSED;
            else state = State.READY;
        }
        return true;
    }

    public synchronized boolean pause() {
        if (state != State.READY && state != State.RUNNING) return false;
        state = State.PAUSED;
        return true;
    }

    public synchronized boolean resume() {
        if (state != State.PAUSED || activeToken != null) return false;
        state = State.READY;
        return true;
    }

    /** 保留在途令牌，由外层据此取消真实CPU任务。 */
    public synchronized boolean cancel() {
        if (state == State.COMPLETE || state == State.CANCELLED) return false;
        state = State.CANCELLED;
        return true;
    }

    public static BigInteger parsePositiveDecimal(String text) {
        Objects.requireNonNull(text);
        if (text.isEmpty() || text.length() > MAX_DECIMAL_DIGITS) {
            throw new IllegalArgumentException("数量必须为1至" + MAX_DECIMAL_DIGITS + "位正十进制整数");
        }
        for (int index = 0; index < text.length(); index++) {
            char digit = text.charAt(index);
            if (digit < '0' || digit > '9') throw new IllegalArgumentException("数量只能包含十进制数字");
        }
        BigInteger value = new BigInteger(text);
        if (value.signum() <= 0) throw new IllegalArgumentException("数量必须大于零");
        return value;
    }

    private static void validate(Snapshot snapshot) {
        Objects.requireNonNull(snapshot);
        Objects.requireNonNull(snapshot.orderId());
        Objects.requireNonNull(snapshot.owner());
        Objects.requireNonNull(snapshot.total());
        Objects.requireNonNull(snapshot.completed());
        Objects.requireNonNull(snapshot.activeAmount());
        Objects.requireNonNull(snapshot.state());
        if (snapshot.total().signum() <= 0 || snapshot.total().compareTo(MAX_TOTAL) > 0
                || snapshot.completed().signum() < 0 || snapshot.completed().compareTo(snapshot.total()) > 0
                || snapshot.activeAmount().signum() < 0
                || snapshot.activeAmount().compareTo(snapshot.total().subtract(snapshot.completed())) > 0) {
            throw new IllegalArgumentException("父订单数量状态越界");
        }
        boolean active = snapshot.activeAmount().signum() > 0;
        if (active != (snapshot.activeToken() != null)) throw new IllegalArgumentException("在途数量与令牌不一致");
        if (snapshot.state() == State.READY && active || snapshot.state() == State.RUNNING && !active) {
            throw new IllegalArgumentException("父订单运行状态与在途令牌不一致");
        }
        boolean done = snapshot.completed().equals(snapshot.total());
        if (snapshot.state() == State.COMPLETE && (!done || active)
                || done && snapshot.state() != State.COMPLETE && snapshot.state() != State.CANCELLED) {
            throw new IllegalArgumentException("父订单完成状态与完成量不一致");
        }
    }
}
