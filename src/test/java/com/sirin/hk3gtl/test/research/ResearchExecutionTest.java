package com.sirin.hk3gtl.test.research;

/**
 * 【文件职责／本轮边界】验证批准压力公式、材料敏感度、100题与255750点总成本。
 * 【变更记录 #3】2026-09-29 21:06:40（第 3 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：验证批准压力公式、材料敏感度、100题与255750点总成本。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchMath;
import com.sirin.hk3gtl.common.research.Hk3ResearchWorkQueue;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 【变更记录 #1】2026-09-22 15:23:00（内测5第4次代码更新）
 * 删除：无。新增：付费研究执行、持久化、权限与公式回归，无真实玩家存档操作。
 * 修改：不使用绕过研究的游戏命令；以可计数原子回调模拟可信仓库扣费。
 * 用途：验证重复请求/停机/重启不能重复扣款或加速，材料快照保持不变。
 * Behavioral regression for paid jobs, restart and pause safety using counted atomic fake adapters.
 * 通过不表示GUI、真实能源仓、研究点生产和多方块实机已验收。
 * Passing does not certify GUI, real inventory/energy adapters, point production or formed structures.
 */
/**
 * 【变更记录 #2】2026-09-27 04:15:46（第 2 次备注 · 内测5修订90）
 * 删除：无。新增：完成查询重入、异常扣电、异常完成及二选一支付模式回归。
 * 修改：保留支付、实验和槽位规则，拒绝回调重入；异常后保留已发生的任务计时。
 * 用途：验证付费任务、点数生产及存档恢复的一致性，不改退款或团队归属。
 */
public final class ResearchExecutionTest {
    private static final UUID OWNER = UUID.fromString("11111111-1111-1111-1111-111111111111");
    private static final UUID OTHER = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final String FACILITY = "minecraft:overworld@10,64,20";

    /** 独立JavaExec入口；失败抛错使check失败，不依赖-ea。 / Standalone check entry, fail explicitly without -ea. */
    public static void main(String[] args) {
        paidLifecycle(); capacityAndUniqueness(); completionRetry(); corruptData(); formulas(); reentryAndExceptions();
        System.out.println("Research execution: paid start, slot capacity, pause/restart, duplicate ticks, receipts and formulas passed");
    }

    /** 用真实账本跑开题到完成：暂停不扣费，重启不重新付款，知识和任务同时结算。
     * Exercise the real ledger from paid start to completion, with pause and restart between ticks.
     */
    private static void paidLifecycle() {
        Hk3ResearchData data = new Hk3ResearchData();
        var quote = quote("RN-HED", FACILITY, 1, 2, "materials");
        AtomicInteger fees = new AtomicInteger(); AtomicInteger energy = new AtomicInteger();
        check(!data.startResearch(OWNER, quote, false, () -> { fees.incrementAndGet(); return true; }), "evidence before debit");
        check(!data.startResearch(OWNER, quote, true, () -> false), "insufficient payment");
        check(data.researchJob(OWNER, "RN-HED") == null, "failed payment leaves no job");
        check(data.startResearch(OWNER, quote, true, () -> { fees.incrementAndGet(); return true; }), "paid start");
        check(!data.startResearch(OWNER, quote, true, () -> { fees.incrementAndGet(); return true; }), "duplicate start");
        check(fees.get() == 1, "exactly one fee");
        check(!data.completed(OWNER, "RN-HED"), "payment is not completion");
        quote.paid().putLong("Count", 999); // 防御性副本。 / Defensive receipt copy.
        check(data.researchJob(OWNER, "RN-HED").quote().paid().getLong("Count") == 7, "immutable receipt");
        check(data.advanceResearch(OWNER, "RN-HED", FACILITY, 10, true, false, 1,
                () -> { energy.incrementAndGet(); return true; }) == Hk3ResearchWorkQueue.Outcome.PAUSED, "offline pause");
        check(data.advanceResearch(OWNER, "RN-HED", FACILITY, 10, false, true, 1,
                () -> { energy.incrementAndGet(); return true; }) == Hk3ResearchWorkQueue.Outcome.PAUSED, "unformed pause");
        data.advanceResearch(OWNER, "RN-HED", "other", 10, true, true, 1, () -> { energy.incrementAndGet(); return true; });
        check(energy.get() == 0, "invalid host never charged");
        check(data.advanceResearch(OWNER, "RN-HED", FACILITY, 10, true, true, 1, () -> false)
                == Hk3ResearchWorkQueue.Outcome.PAUSED, "power shortage");
        data.advanceResearch(OWNER, "RN-HED", FACILITY, 11, true, true, 1, () -> { energy.incrementAndGet(); return true; });
        check(data.researchJob(OWNER, "RN-HED").progress() == 1, "one powered tick");
        data = Hk3ResearchData.load(data.save(new CompoundTag()));
        check(data.researchJob(OWNER, "RN-HED").quote().paid().getLong("Count") == 7, "receipt survives restart");
        check(data.advanceResearch(OWNER, "RN-HED", FACILITY, 11, true, true, 1,
                () -> { energy.incrementAndGet(); return true; }) == Hk3ResearchWorkQueue.Outcome.DUPLICATE_TICK, "restart same tick blocked");
        check(data.advanceResearch(OTHER, "RN-HED", FACILITY, 12, true, true, 1, () -> true)
                == Hk3ResearchWorkQueue.Outcome.MISSING, "owner isolation");
        check(data.advanceResearch(OWNER, "RN-HED", FACILITY, 10000, true, true, 1,
                () -> { energy.incrementAndGet(); return true; }) == Hk3ResearchWorkQueue.Outcome.COMPLETED, "one tick after long gap");
        check(energy.get() == 2 && fees.get() == 1, "only actual running ticks charged");
        check(data.completed(OWNER, "RN-HED") && data.researchJob(OWNER, "RN-HED") == null, "knowledge and job settle together");
        check(!data.startResearch(OWNER, quote, true, () -> { fees.incrementAndGet(); return true; }), "completed topic cannot charge again");
        check(Hk3ResearchData.load(data.save(new CompoundTag())).completed(OWNER, "RN-HED"), "completion survives restart");
    }

    /** 实际目录覆盖所有五阶槽位；同课题跨机器仍只能一份，满槽不扣费。
     * Check all five capacities using real topics; cross-facility duplicate topics cannot charge again.
     */
    private static void capacityAndUniqueness() {
        for (int lab = 1; lab <= 5; lab++) {
            final int level = lab;
            var topics = Hk3ResearchCatalog.bundled().topics().values().stream()
                    .filter(t -> t.lab() <= level).limit(Hk3ResearchMath.slots(lab) + 1L).toList();
            Hk3ResearchWorkQueue queue = new Hk3ResearchWorkQueue();
            AtomicInteger fees = new AtomicInteger();
            for (int i = 0; i < topics.size(); i++) {
                String topic = topics.get(i).id();
                boolean ok = queue.start(OWNER, quote(topic, FACILITY, lab, 20, "points"), id -> !id.equals(topic), true,
                        () -> { fees.incrementAndGet(); return true; });
                check(ok == (i < Hk3ResearchMath.slots(lab)), "lab slot cap " + lab);
            }
            check(fees.get() == Hk3ResearchMath.slots(lab), "full slot does not charge");
            String first = topics.get(0).id();
            check(!queue.start(OWNER, quote(first, "second", lab, 20, "points"), id -> false, true,
                    () -> { throw new AssertionError("duplicate charged"); }), "cross-machine topic uniqueness");
            check(!queue.start(OTHER, quote(first, FACILITY, lab, 20, "points"), id -> false, true,
                    () -> { throw new AssertionError("borrowed host charged"); }), "host owner binding");
            check(Hk3ResearchWorkQueue.load(queue.save()).snapshot(OWNER, first) != null, "capacity survives restart");
        }
        Hk3ResearchWorkQueue queue = new Hk3ResearchWorkQueue();
        check(!queue.start(OWNER, quote("RN-RCA", FACILITY, 1, 20, "points"), id -> false, true,
                () -> { throw new AssertionError("locked research charged"); }), "core prerequisites enforced");
    }

    /** 完成回调暂时拒绝时保留已付款满进度，重试不再耗电。 / Retry rejected settlement without recharging energy or losing paid progress. */
    private static void completionRetry() {
        Hk3ResearchWorkQueue queue = new Hk3ResearchWorkQueue();
        queue.start(OWNER, quote("RN-HED", FACILITY, 1, 1, "points"), id -> false, true, () -> true);
        check(queue.advance(OWNER, "RN-HED", FACILITY, 1, true, true, 1, () -> true, () -> false)
                == Hk3ResearchWorkQueue.Outcome.WAITING_COMPLETION, "pending completion retained");
        queue = Hk3ResearchWorkQueue.load(queue.save());
        check(queue.advance(OWNER, "RN-HED", FACILITY, 2, true, true, 1,
                () -> { throw new AssertionError("recharged finished work"); }, () -> true)
                == Hk3ResearchWorkQueue.Outcome.COMPLETED, "settlement retry");
    }

    /** 损坏/重复任务必须拒绝而非丢弃；未知课题保留费用供后续恢复。 / Reject malformed/duplicate jobs; preserve retired IDs and receipts for recovery. */
    private static void corruptData() {
        Hk3ResearchWorkQueue queue = new Hk3ResearchWorkQueue();
        queue.start(OWNER, quote("RN-HED", FACILITY, 1, 20, "materials"), id -> false, true, () -> true);
        CompoundTag original = queue.save();
        CompoundTag bad = original.copy();
        bad.getList("Jobs", Tag.TAG_COMPOUND).getCompound(0).putDouble("Progress", Double.NaN);
        reject(() -> Hk3ResearchWorkQueue.load(bad));
        CompoundTag duplicate = original.copy();
        ListTag list = duplicate.getList("Jobs", Tag.TAG_COMPOUND); list.add(list.getCompound(0).copy());
        reject(() -> Hk3ResearchWorkQueue.load(duplicate));
        CompoundTag retired = original.copy();
        retired.getList("Jobs", Tag.TAG_COMPOUND).getCompound(0).putString("Topic", "RN-RETIRED");
        check(Hk3ResearchWorkQueue.load(retired).snapshot(OWNER, "RN-RETIRED") != null, "retired paid job preserved");
        CompoundTag missing = original.copy(); missing.getList("Jobs", Tag.TAG_COMPOUND).getCompound(0).remove("Paid");
        reject(() -> Hk3ResearchWorkQueue.load(missing));
    }

    /** 核对已确认公式的锚点、S01免疫与异常输入，不把演示数字当作正式课题价格。
     * Verify formula reference cases and S01 immunity without inventing per-topic prices.
     */
    private static void formulas() {
        near(Hk3ResearchMath.speed(1, 1000, 0, false, false), 1);
        // 修订100：使用批准稿独立计算参考量，不引用被测pressure函数作为期望值。
        double q=0.4125, reduced=q*Math.pow(0.25,1.25);
        near(Hk3ResearchMath.speed(2,100,0,false,false),1/(1+1.2*q+1.2*q*q+0.6*Math.pow(q,4)));
        near(Hk3ResearchMath.speed(2,100,0.75,false,false),1/(1+1.2*reduced+1.2*reduced*reduced+0.6*Math.pow(reduced,4)));
        near(Hk3ResearchMath.speed(5, 0, 0, true, true), 3);
        check(Hk3ResearchMath.materialCount(3, 2, 100, 0) == 4, "ceil pressure materials");
        check(Hk3ResearchMath.materialCount(100, 2, 100, 0,0) == 100, "insensitive materials");
        check(com.sirin.hk3gtl.common.research.Hk3ResearchPlans.all().size()==100,"100 priced topics");
        check(com.sirin.hk3gtl.common.research.Hk3ResearchPlans.all().values().stream().mapToLong(p -> p.points()).sum()==255750,"approved total point budget");
        check(Hk3ResearchMath.materialCount(3, 1, 1000, 0) == 3, "S01 material immunity");
        check(Hk3ResearchMath.materialCount(Long.MAX_VALUE, 1, 0, 0) == Long.MAX_VALUE, "large exact count");
        reject(() -> Hk3ResearchMath.materialCount(Long.MAX_VALUE, 2, 100, 0));
        reject(() -> Hk3ResearchMath.speed(2, Double.NaN, 0, false, false));
        reject(() -> Hk3ResearchMath.slots(6));
    }

    private static Hk3ResearchWorkQueue.Quote quote(String topic, String facility, int lab, long ticks, String mode) {
        CompoundTag paid = new CompoundTag(); paid.putLong("Count", 7);
        return new Hk3ResearchWorkQueue.Quote(topic, facility, lab, ticks, 2_013_265_920L, mode, paid);
    }
    /** 重入必须在扣费前拒绝；失败结算与异常扣电重启后不重复推进。 */
    private static void reentryAndExceptions() {
        Hk3ResearchWorkQueue queue = new Hk3ResearchWorkQueue();
        var q = quote("RN-HED", FACILITY, 1, 1, "materials");
        AtomicInteger fees = new AtomicInteger();
        try {
            queue.start(OWNER, q, id -> {
                queue.start(OWNER, q, ignored -> false, true, () -> { fees.incrementAndGet(); return true; });
                return false;
            }, true, () -> { fees.incrementAndGet(); return true; });
            throw new AssertionError("predicate reentry accepted");
        } catch (IllegalStateException expected) { }
        check(fees.get() == 0 && queue.snapshot(OWNER, "RN-HED") == null, "reentry before payment");
        check(queue.start(OWNER, q, id -> false, true, () -> true), "guard resets after exception");
        try {
            queue.advance(OWNER, "RN-HED", FACILITY, 1, true, true, 1, () -> true,
                    () -> { throw new IllegalStateException("completion unavailable"); });
            throw new AssertionError("exception swallowed");
        } catch (IllegalStateException expected) { }
        var restored = Hk3ResearchWorkQueue.load(queue.save());
        AtomicInteger completed = new AtomicInteger();
        check(restored.advance(OWNER, "RN-HED", FACILITY, 1, true, true, 1,
                () -> { throw new AssertionError("duplicate energy"); }, () -> true)
                == Hk3ResearchWorkQueue.Outcome.DUPLICATE_TICK, "exception tick persisted");
        check(restored.advance(OWNER, "RN-HED", FACILITY, 2, true, true, 1,
                () -> { throw new AssertionError("finished job charged"); },
                () -> { completed.incrementAndGet(); return true; }) == Hk3ResearchWorkQueue.Outcome.COMPLETED,
                "completion retries without power");
        restored.advance(OWNER, "RN-HED", FACILITY, 3, true, true, 1, () -> true,
                () -> { completed.incrementAndGet(); return true; });
        check(completed.get() == 1, "completion callback exactly once after successful settlement");
        var data = new Hk3ResearchData();
        data.startResearch(OWNER, q, true, () -> true);
        data.setDirty(false);
        try {
            data.advanceResearch(OWNER, "RN-HED", FACILITY, 4, true, true, 1,
                    () -> { throw new IllegalStateException("atomic power adapter failed"); });
            throw new AssertionError("power exception swallowed");
        } catch (IllegalStateException expected) { }
        check(data.isDirty(), "exception tick marks saved data dirty");
        var dataRestored = Hk3ResearchData.load(data.save(new CompoundTag()));
        check(dataRestored.advanceResearch(OWNER, "RN-HED", FACILITY, 4, true, true, 1,
                () -> { throw new AssertionError("same tick retried after restart"); })
                == Hk3ResearchWorkQueue.Outcome.DUPLICATE_TICK, "power exception recovery");
        check(dataRestored.researchJob(OWNER, "RN-HED").progress() == 0, "failed energy made no progress");
        reject(() -> quote(" ", FACILITY, 1, 1, "points"));
        reject(() -> quote("RN-HED", FACILITY, 1, 1, "points+materials"));
    }

    private static void near(double actual, double expected) { check(Math.abs(actual - expected) < 1e-10, "formula mismatch"); }
    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
    private static void reject(Runnable action) {
        try { action.run(); } catch (IllegalArgumentException | ArithmeticException expected) { return; }
        throw new AssertionError("Invalid state accepted");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
