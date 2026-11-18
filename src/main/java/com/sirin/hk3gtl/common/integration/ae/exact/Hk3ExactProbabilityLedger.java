package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** 仅记录预算和权威完整批次回执；调用方负责真实投料、持久化与输出归属，不操作物品库存。 */
public final class Hk3ExactProbabilityLedger<K> {
    public enum Status { ACTIVE, SATISFIED, NO_CHANCE, BUDGET_EXHAUSTED, CANCELLED, RECOVERY_REQUIRED }

    public record Pending(UUID token, String metadataId, long attempts) {
        public Pending {
            Objects.requireNonNull(token);
            Objects.requireNonNull(metadataId);
            if (attempts <= 0) throw new IllegalArgumentException("在途批次次数必须为正数");
        }
    }

    /** 只能由能证明整批结束且输出已归属该订单的机器适配器签发，不接受库存增量或超时猜测。 */
    public record Receipt(UUID token, String metadataId, long attempts, BigInteger actualOutput) {
        public Receipt {
            Objects.requireNonNull(token);
            Objects.requireNonNull(metadataId);
            Objects.requireNonNull(actualOutput);
            if (attempts <= 0 || actualOutput.signum() < 0) {
                throw new IllegalArgumentException("概率批次回执无效");
            }
        }
    }

    public record Snapshot<K>(Hk3ExactProbabilityPlan<K> plan, BigInteger allocatedAttempts,
            BigInteger actualOutput, Pending pending, Receipt lastReceipt, boolean cancelled) {}

    private final Hk3ExactProbabilityPlan<K> plan;
    private BigInteger allocatedAttempts = BigInteger.ZERO;
    private BigInteger actualOutput = BigInteger.ZERO;
    private Pending pending;
    private Receipt lastReceipt;
    private boolean cancelled;
    private boolean recoveryRequired;

    public Hk3ExactProbabilityLedger(Hk3ExactProbabilityPlan<K> plan) {
        this.plan = Objects.requireNonNull(plan);
    }

    public static <K> Hk3ExactProbabilityLedger<K> restore(Snapshot<K> snapshot) {
        Objects.requireNonNull(snapshot);
        var ledger = new Hk3ExactProbabilityLedger<>(snapshot.plan());
        BigInteger allocated = snapshot.allocatedAttempts();
        Pending pending = snapshot.pending();
        Receipt receipt = snapshot.lastReceipt();
        if (allocated.signum() < 0 || allocated.compareTo(ledger.plan.attemptCapacity()) > 0 || snapshot.actualOutput() == null
                || snapshot.actualOutput().signum() < 0 || pending != null
                && (!pending.metadataId().equals(ledger.plan.metadataId()) || BigInteger.valueOf(pending.attempts()).compareTo(allocated) > 0)
                || receipt != null && (!receipt.metadataId().equals(ledger.plan.metadataId())
                || BigInteger.valueOf(receipt.attempts()).compareTo(allocated) > 0 || pending != null && pending.token().equals(receipt.token()))) {
            throw new IllegalArgumentException("概率账本快照无效");
        }
        BigInteger completed = allocated.subtract(pending == null ? BigInteger.ZERO : BigInteger.valueOf(pending.attempts()));
        if ((completed.signum() > 0) != (receipt != null)) {
            throw new IllegalArgumentException("已结束批次缺少回执或空账本包含回执");
        }
        ledger.validateOutput(completed, snapshot.actualOutput());
        if (receipt != null) {
            ledger.validateOutput(BigInteger.valueOf(receipt.attempts()), receipt.actualOutput());
            if (BigInteger.valueOf(receipt.attempts()).compareTo(completed) > 0 || receipt.actualOutput().compareTo(snapshot.actualOutput()) > 0) {
                throw new IllegalArgumentException("概率回执与累计完成量不一致");
            }
        }
        if (ledger.plan.chance().signum() == 0 && allocated.signum() > 0) {
            throw new IllegalArgumentException("零概率计划不能存在已投料批次");
        }
        ledger.allocatedAttempts = allocated;
        ledger.actualOutput = snapshot.actualOutput();
        ledger.pending = pending;
        ledger.lastReceipt = receipt;
        ledger.cancelled = snapshot.cancelled();
        ledger.recoveryRequired = pending != null;
        return ledger;
    }

    /** 必须先持久化该预留，再交给真实机器；未确认的批次不能自动重投。 */
    public synchronized Optional<Pending> begin() {
        return begin(actualOutput.compareTo(plan.target()) >= 0);
    }

    public synchronized Optional<Pending> begin(boolean targetsSatisfied) {
        if (status(targetsSatisfied) != Status.ACTIVE || pending != null) return Optional.empty();
        BigInteger remaining = plan.target().subtract(actualOutput).max(BigInteger.ONE);
        long attempts = plan.expectedAttempts(remaining).orElseThrow()
                .min(BigInteger.valueOf(plan.maxBatch()))
                .min(plan.attemptCapacity().subtract(allocatedAttempts)).longValueExact();
        pending = new Pending(UUID.randomUUID(), plan.metadataId(), attempts);
        allocatedAttempts = allocatedAttempts.add(BigInteger.valueOf(attempts));
        return Optional.of(pending);
    }

    public synchronized boolean complete(Receipt receipt) {
        Objects.requireNonNull(receipt);
        if (lastReceipt != null && receipt.token().equals(lastReceipt.token())) {
            if (!receipt.equals(lastReceipt)) throw new IllegalArgumentException("同一批次出现冲突回执");
            return false;
        }
        if (pending == null || !receipt.token().equals(pending.token())
                || !receipt.metadataId().equals(pending.metadataId()) || receipt.attempts() != pending.attempts()) {
            throw new IllegalArgumentException("回执不属于当前完整在途批次");
        }
        validateOutput(BigInteger.valueOf(receipt.attempts()), receipt.actualOutput());
        actualOutput = actualOutput.add(receipt.actualOutput());
        lastReceipt = receipt;
        pending = null;
        recoveryRequired = false;
        return true;
    }

    public synchronized void cancel() {
        cancelled = true;
    }

    public synchronized void withdrawUnstarted(UUID token) {
        if (pending == null || !pending.token().equals(token)) throw new IllegalArgumentException("预留令牌不匹配");
        allocatedAttempts = allocatedAttempts.subtract(BigInteger.valueOf(pending.attempts()));
        pending = null;
        recoveryRequired = false;
    }

    public synchronized void markUnknown(UUID token) {
        if (pending == null || !pending.token().equals(token)) {
            throw new IllegalArgumentException("未知结果不属于当前在途批次");
        }
        recoveryRequired = true;
    }

    public synchronized Status status() {
        return status(actualOutput.compareTo(plan.target()) >= 0);
    }

    public synchronized Status status(boolean targetsSatisfied) {
        if (recoveryRequired) return Status.RECOVERY_REQUIRED;
        if (cancelled) return Status.CANCELLED;
        if (targetsSatisfied) return Status.SATISFIED;
        if (plan.chance().signum() == 0) return Status.NO_CHANCE;
        if (pending == null && allocatedAttempts.equals(plan.attemptCapacity())) return Status.BUDGET_EXHAUSTED;
        return Status.ACTIVE;
    }

    public synchronized Snapshot<K> snapshot() {
        return new Snapshot<>(plan, allocatedAttempts, actualOutput, pending, lastReceipt, cancelled);
    }

    private void validateOutput(BigInteger attempts, BigInteger output) {
        BigInteger upper = plan.successYield().multiply(attempts);
        if (output.compareTo(upper) > 0 || output.remainder(plan.successYield()).signum() != 0
                || plan.chance().equals(plan.chanceScale()) && !output.equals(upper)) {
            throw new IllegalArgumentException("真实回执与固定单次产出元数据矛盾");
        }
    }
}
