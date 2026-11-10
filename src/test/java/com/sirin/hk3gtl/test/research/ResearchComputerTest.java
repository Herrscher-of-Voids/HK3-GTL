package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchWorkQueue;
import net.minecraft.nbt.CompoundTag;
import java.math.BigInteger;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 【变更记录 #1】2026-09-22 15:39:00（内测5第5次代码更新）
 * 删除：无。新增：真实点数账本与支付回归，验证产点、停机、切电路、重启、重复tick及开题。
 * 修改：测试使用固定所有者与可计数扣电，不启动游戏；用途：验证生产到付款链不复制资金。
 * Exercise actual ledger production-to-payment without game startup; counted power verifies no free or duplicated points.
 */
/**
 * 【变更记录 #2】2026-09-27 04:15:46（第 2 次备注 · 内测5修订90）
 * 删除：无。新增：计算机回调重入和点数/材料交叉重复提交回归。
 * 修改：保留支付、实验和槽位规则，拒绝回调重入；异常后保留已发生的任务计时。
 * 用途：验证付费任务、点数生产及存档恢复的一致性，不改退款或团队归属。
 */
public final class ResearchComputerTest {
    private static final UUID OWNER = UUID.fromString("33333333-3333-3333-3333-333333333333");
    private static final UUID OTHER = UUID.fromString("44444444-4444-4444-4444-444444444444");
    /** JavaExec入口；每条断言失败阻止check通过。 / Standalone check entry, assertion failures fail the build. */
    public static void main(String[] args) {
        production(); payments(); largeBalance(); paymentReentry();
        System.out.println("Research computer: 200-tick baseline, two machines, circuit changes, restart, power gates and point payment passed");
    }

    /** 生产计量：实际tick而非时间差，切电路保留余数，二台分别加点。
     * Meter actual ticks, preserve fractions across circuit swaps and credit each machine independently.
     */
    private static void production() {
        Hk3ResearchData data = new Hk3ResearchData();
        AtomicInteger power = new AtomicInteger();
        for (int i = 0; i < 199; i++) check(data.tickComputer(OWNER, "overworld@a", i, 0, true,
                () -> { power.incrementAndGet(); return true; }), "powered tick");
        check(data.points(OWNER).signum() == 0, "no point before 200 ticks");
        data = Hk3ResearchData.load(data.save(new CompoundTag()));
        check(!data.tickComputer(OWNER, "overworld@a", 198, 0, true, () -> { throw new AssertionError("duplicate energy"); }), "restart duplicate tick");
        check(!data.tickComputer(OWNER, "overworld@a", 199, 0, false, () -> true), "offline paused");
        check(!data.tickComputer(OWNER, "overworld@a", 199, -1, true, () -> true), "empty/low circuit paused");
        check(!data.tickComputer(OWNER, "overworld@a", 199, 0, true, () -> false), "power shortage");
        check(data.points(OWNER).signum() == 0, "paused work gives nothing");
        data.tickComputer(OWNER, "overworld@a", 10000, 0, true, () -> { power.incrementAndGet(); return true; });
        check(data.points(OWNER).equals(BigInteger.ONE) && power.get() == 200, "200 actual ticks one point");
        for (int i = 0; i < 200; i++) data.tickComputer(OWNER, "overworld@b", i, 0, true, () -> true);
        check(data.points(OWNER).equals(BigInteger.TWO), "two machines add points");
        for (int i = 0; i < 100; i++) data.tickComputer(OWNER, "quantum@a", i, 0, true, () -> true);
        for (int i = 100; i < 120; i++) data.tickComputer(OWNER, "quantum@a", i, 16, true, () -> true);
        check(data.points(OWNER).equals(BigInteger.valueOf(3)), "400 work plus 20 boosted ticks");
        check(data.points(OTHER).signum() == 0, "owner isolation");
        for (int i = 0; i < 199; i++) data.tickComputer(OWNER, "change", i, 0, true, () -> true);
        data.tickComputer(OTHER, "change", 200, 0, true, () -> true);
        check(data.points(OTHER).signum() == 0, "owner change cannot inherit fraction");
        data.removeComputer(OTHER, "change");
        data.tickComputer(OTHER, "change", 201, 16, true, () -> true);
        check(data.points(OTHER).signum() == 0, "replacement cannot restore old fraction");
    }

    /** 点数开题实扣一次，余额不足/前置不足不扣费，付款与任务经同一NBT往返。
     * Pay once using actual balances; rejected starts do not debit and save/load preserves both payment and job.
     */
    private static void payments() {
        Hk3ResearchData data = new Hk3ResearchData();
        for (int i = 0; i < 80; i++) data.tickComputer(OWNER, "pc", i, 16, true, () -> true);
        check(data.points(OWNER).equals(BigInteger.TWO), "earned two points");
        check(!data.startResearchWithPoints(OWNER, quote("RN-HED", 3), true), "insufficient balance");
        check(!data.startResearchWithPoints(OWNER, quote("RN-RCA", 1), true), "prerequisite/lab refusal");
        check(data.points(OWNER).equals(BigInteger.TWO), "rejected starts retain money");
        check(data.startResearchWithPoints(OWNER, quote("RN-HED", 1), true), "real point payment accepted");
        check(!data.startResearchWithPoints(OWNER, quote("RN-HED", 1), true), "duplicate payment refused");
        check(data.points(OWNER).equals(BigInteger.ONE), "one fee only");
        data = Hk3ResearchData.load(data.save(new CompoundTag()));
        check(data.points(OWNER).equals(BigInteger.ONE) && data.researchJob(OWNER, "RN-HED") != null, "payment/job same save");
        data.advanceResearch(OWNER, "RN-HED", "lab", 0, true, true, 1, () -> true);
        check(data.completed(OWNER, "RN-HED") && data.points(OWNER).equals(BigInteger.ONE), "completion does not charge again");
    }

    /** 超long余额无溢出，负数或类型损坏拒绝；不读真实存档。
     * Balances beyond long remain exact; reject negative or malformed data without touching real saves.
     */
    private static void largeBalance() {
        CompoundTag root = new CompoundTag(); CompoundTag accounts = new CompoundTag(); CompoundTag account = new CompoundTag();
        BigInteger huge = BigInteger.ONE.shiftLeft(100); account.putString("Points", huge.toString());
        accounts.put(OWNER.toString(), account); root.put("Accounts", accounts);
        Hk3ResearchData data = Hk3ResearchData.load(root);
        for (int i = 0; i < 40; i++) data.tickComputer(OWNER, "pc", i, 16, true, () -> true);
        check(data.points(OWNER).equals(huge.add(BigInteger.ONE)), "no artificial long cap");
        account.putString("Points", "-1");
        reject(() -> Hk3ResearchData.load(root).points(OWNER));
        account.putInt("Points", 10);
        reject(() -> Hk3ResearchData.load(root).points(OWNER));
    }

    private static Hk3ResearchWorkQueue.Quote quote(String topic, int points) {
        CompoundTag paid = new CompoundTag(); paid.putString("Points", Integer.toString(points));
        return new Hk3ResearchWorkQueue.Quote(topic, "lab", 1, 1, 1, "points", paid);
    }
    private static void paymentReentry() {
        var data = new Hk3ResearchData();
        try {
            data.tickComputer(OWNER, "pc", 0, 16, true, () -> {
                data.tickComputer(OWNER, "pc", 0, 16, true, () -> true);
                return true;
            });
            throw new AssertionError("computer reentry accepted");
        } catch (IllegalStateException expected) { }
        check(data.points(OWNER).signum() == 0, "failed callback no credit");
        for (int i=0; i<40; i++) data.tickComputer(OWNER, "pc", i, 16, true, () -> true);
        check(data.points(OWNER).equals(BigInteger.ONE), "guard releases and no hidden work");
        var materials = new CompoundTag(); materials.putLong("Count", 1);
        var q = new Hk3ResearchWorkQueue.Quote("RN-HED", "lab", 1, 1, 1, "materials", materials);
        check(!data.startResearchWithPoints(OWNER, q, true), "material quote cannot debit points");
        check(data.startResearch(OWNER, q, true, () -> true), "material-only payment");
        check(data.points(OWNER).equals(BigInteger.ONE), "materials preserve points");
        check(!data.startResearchWithPoints(OWNER, quote("RN-HED", 1), true), "cannot repay active material job with points");
        check(data.points(OWNER).equals(BigInteger.ONE), "duplicate alternate mode preserves points");
    }

    private static void check(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
    private static void reject(Runnable action) {
        try { action.run(); } catch (IllegalArgumentException expected) { return; }
        throw new AssertionError("Malformed balance accepted");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
