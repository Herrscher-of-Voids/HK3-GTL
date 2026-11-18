package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.research.Hk3ErosionResearch;
import com.sirin.hk3gtl.common.research.Hk3LabExperimentRules;
import com.sirin.hk3gtl.common.research.Hk3ResearchMath;
import com.sirin.hk3gtl.common.research.Hk3ResearchWorkQueue;
import net.minecraft.nbt.CompoundTag;

import java.util.UUID;

public final class ErosionResearchModuleTest {
    private static final long EXTRA = Hk3Values.VA_LONG[19];
    private static int checks;

    private ErosionResearchModuleTest() {}

    public static void run() {
        checks = 0;
        eligibility();
        billing();
        completion();
        experiments();
        System.out.println("ErosionResearchModuleTest: " + checks + " checks passed; offline only");
    }

    private static void eligibility() {
        check(!Hk3ErosionResearch.allowed(1, true) && Hk3ErosionResearch.allowed(2, true)
                && Hk3ErosionResearch.allowed(5, true) && !Hk3ErosionResearch.allowed(6, true), "仅S02至S05开放安装资格");
        check(!Hk3ErosionResearch.allowed(2, false), "未完成课题不能安装");
        long base = 17, full = Hk3ErosionResearch.cost(base, true);
        check(full == base + EXTRA && Hk3ErosionResearch.cost(base, false) == base, "附加1A QSV保留基础课题费用");
        check(boost(true, true, true, "RN-ECA", base, full), "安装启用且恰好可支付完整费用");
        check(!boost(false, true, true, "RN-ECA", base, full), "研究资格不能被实体物品绕过");
        check(!boost(true, false, true, "RN-ECA", base, full), "开关不授予免费模块");
        check(!boost(true, true, false, "RN-ECA", base, full), "关闭模块恢复基础研究");
        check(!boost(true, true, true, "RN-ECA", base, full - 1), "少一EU也不提供加速");
        check(!boost(true, true, true, "RN-ECA", base, -1), "负余额不能获得加速");
        check(!boost(true, true, true, "RN-ECA", 0, full), "非法基础费用不提供加速");
        check(!boost(true, true, true, null, base, full)
                && !boost(true, true, true, "RN-NOT-A-TOPIC", base, full), "空课题和未知课题不提供加速");
        check(!boost(true, true, true, "RN-ECA", Long.MAX_VALUE, Long.MAX_VALUE), "超出long的总费回落基础研究");
        check(Hk3ErosionResearch.cost(Long.MAX_VALUE, false) == Long.MAX_VALUE, "基础最高费用不钳制");
        rejects(() -> Hk3ErosionResearch.cost(Long.MAX_VALUE, true), ArithmeticException.class, "溢出费用不得静默少收");
        rejects(() -> Hk3ErosionResearch.cost(0, false), IllegalArgumentException.class, "拒绝非法基础费用");
        double normal = Hk3ResearchMath.speed(2, 500, 0.5, false, false);
        double boosted = Hk3ResearchMath.speed(2, 500, 0.5, true, false);
        check(Math.abs(boosted - 1.5 * normal) < 1e-12, "正向增加50%后仍按原压力公式减速");
        check(Hk3ResearchMath.slots(2) == 2 && Hk3ResearchMath.slots(5) == 16, "模块不增加研究槽位");
    }

    private static void billing() {
        var h = new Harness();
        h.start("RN-ECA", 10, 7);
        h.start("RN-CPT", 10, 11);
        long first = Hk3ErosionResearch.cost(7, true), second = Hk3ErosionResearch.cost(11, true);
        h.balance = first + second;
        check(h.advance("RN-ECA", 1, true, true, true) == Hk3ResearchWorkQueue.Outcome.RUNNING, "第一课题实际推进");
        check(h.advance("RN-CPT", 1, true, true, true) == Hk3ResearchWorkQueue.Outcome.RUNNING, "第二课题独立推进");
        check(h.balance == 0 && h.paid == first + second && h.debits == 2, "每个推进课题分别扣基础和附加费用");
        check(h.queue.snapshot(h.scope, "RN-ECA").progress() == 1.5
                && h.queue.snapshot(h.scope, "RN-CPT").progress() == 1.5, "两项均只获得一次有效加速");
        check(h.advance("RN-ECA", 1, true, true, true) == Hk3ResearchWorkQueue.Outcome.DUPLICATE_TICK
                && h.debits == 2, "重复tick不重复扣费或推进");
        check(h.advance("RN-ECA", 2, true, true, true) == Hk3ResearchWorkQueue.Outcome.PAUSED
                && h.debits == 2 && h.queue.snapshot(h.scope, "RN-ECA").progress() == 1.5, "基础用电不足暂停且不收费");
        h.balance = 7;
        check(h.advance("RN-ECA", 3, true, true, true) == Hk3ResearchWorkQueue.Outcome.RUNNING, "只能支付基础费用时继续普通研究");
        check(h.balance == 0 && h.paid == first + second + 7
                && h.queue.snapshot(h.scope, "RN-ECA").progress() == 2.5, "附加费不足不免费加速也不取消研究");
        h.balance = first;
        check(h.advance("RN-ECA", 4, false, true, true) == Hk3ResearchWorkQueue.Outcome.PAUSED, "未成型暂停");
        check(h.advance("RN-ECA", 4, true, false, true) == Hk3ResearchWorkQueue.Outcome.PAUSED, "正式研究无人在线暂停");
        check(h.balance == first && h.debits == 3 && h.queue.snapshot(h.scope, "RN-ECA").progress() == 2.5,
                "暂停状态不触发扣费回调且保留进度");
        h.enabled = false;
        check(h.advance("RN-ECA", 4, true, true, true) == Hk3ResearchWorkQueue.Outcome.RUNNING
                && h.balance == EXTRA && h.queue.snapshot(h.scope, "RN-ECA").progress() == 3.5, "关闭模块按基础费用继续");
    }

    private static void completion() {
        var h = new Harness();
        h.start("RN-ECA", 1, 5);
        long full = Hk3ErosionResearch.cost(5, true);
        h.balance = full * 2;
        check(h.advance("RN-ECA", 1, true, true, false) == Hk3ResearchWorkQueue.Outcome.WAITING_COMPLETION, "满进度等待完成回执");
        check(h.paid == full && h.debits == 1 && h.queue.snapshot(h.scope, "RN-ECA").progress() == 1, "最后推进刻只扣本次完整费用");
        check(h.advance("RN-ECA", 2, true, true, false) == Hk3ResearchWorkQueue.Outcome.WAITING_COMPLETION
                && h.paid == full && h.debits == 1, "等待完成不继续收费");
        check(h.advance("RN-ECA", 3, true, true, true) == Hk3ResearchWorkQueue.Outcome.COMPLETED
                && h.paid == full && h.debits == 1, "完成回执重试不重复扣费");
        check(h.advance("RN-ECA", 4, true, true, true) == Hk3ResearchWorkQueue.Outcome.MISSING
                && h.balance == full, "空闲没有加速运行费");
    }

    private static void experiments() {
        for (String id : new String[]{"LAB-ALE", "LAB-OPR", "LAB-ERM-BASE", "LAB-ERM-AID"}) {
            check(!boost(true, true, true, id, 13, EXTRA + 13), id + "独立实验不启用模块加速");
        }
        var h = new Harness();
        h.start("LAB-ERM-AID", Hk3LabExperimentRules.get("LAB-ERM-AID").ticks(), 13);
        h.balance = EXTRA + 13;
        check(h.advance("LAB-ERM-AID", 1, true, true, true) == Hk3ResearchWorkQueue.Outcome.RUNNING,
                "辅助实验按原固定工况推进");
        check(h.paid == 13 && h.balance == EXTRA && h.queue.snapshot(h.scope, "LAB-ERM-AID").progress() == 1,
                "辅助实验只付原用电，不付模块附加费或获得加速");
    }

    private static boolean boost(boolean researched, boolean installed, boolean enabled, String topic, long base, long available) {
        return Hk3ErosionResearch.boost(2, researched, installed, enabled, topic, base, available);
    }

    private static final class Harness {
        private final Hk3ResearchWorkQueue queue = new Hk3ResearchWorkQueue();
        private final UUID scope = UUID.randomUUID();
        private long balance, paid;
        private int debits;
        private boolean enabled = true;

        private void start(String topic, long ticks, long base) {
            var receipt = new CompoundTag();
            receipt.putInt("夹具支付", 1);
            var experiment = Hk3LabExperimentRules.get(topic);
            String research = experiment == null ? topic : experiment.research();
            var quote = new Hk3ResearchWorkQueue.Quote(topic, "test:erm", 2, ticks, base,
                    experiment == null ? "points" : "materials", receipt);
            check(queue.start(scope, quote, id -> !id.equals(research), true, () -> true), "夹具启动真实队列：" + topic);
        }

        private Hk3ResearchWorkQueue.Outcome advance(String topic, long tick, boolean formed, boolean online, boolean complete) {
            var current = queue.snapshot(scope, topic);
            if (current == null) return queue.advance(scope, topic, "test:erm", tick, formed, online, 1,
                    () -> { throw new AssertionError("不存在的课题不得扣费"); }, () -> complete);
            long base = current.quote().eut();
            boolean boost = ErosionResearchModuleTest.boost(true, true, enabled, topic, base, balance);
            long amount = Hk3ErosionResearch.cost(base, boost);
            return queue.advance(scope, topic, "test:erm", tick, formed, online,
                    Hk3ResearchMath.speed(2, 0, 0, boost, false), () -> {
                        if (balance < amount) return false;
                        balance -= amount;
                        paid += amount;
                        debits++;
                        return true;
                    }, () -> complete);
        }
    }

    private static void rejects(Runnable action, Class<? extends RuntimeException> type, String message) {
        try {
            action.run();
        } catch (RuntimeException failure) {
            check(type.isInstance(failure), message);
            return;
        }
        throw new AssertionError(message);
    }

    private static void check(boolean condition, String message) {
        checks++;
        if (!condition) throw new AssertionError(message);
    }
}
