package com.sirin.hk3gtl.test.persistence;

import com.sirin.hk3gtl.common.capability.*;
import com.sirin.hk3gtl.common.machine.Hk3RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import net.minecraft.nbt.CompoundTag;
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;

import java.math.BigInteger;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

public final class DualEnergyTickTest {
    private static int checks;
    private static final UUID OWNER = new UUID(0, 1), OTHER = new UUID(0, 2);
    private static final BigInteger HUGE = BigInteger.TEN.pow(60);
    private static void check(boolean pass, String reason) { checks++; if (!pass) throw new AssertionError(reason); }
    private static void reject(Runnable operation) {
        try { operation.run(); throw new AssertionError("非法操作被接受"); }
        catch (IllegalStateException | IllegalArgumentException expected) { checks++; }
    }
    private static final class Fixture {
        final HonkaiWirelessSavedData hw = new HonkaiWirelessSavedData();
        final Map<UUID, BigInteger> eu = new HashMap<>();
        final AtomicInteger receipts = new AtomicInteger(), dirty = new AtomicInteger();
        boolean refuse;
        Fixture() { hw.insert(OWNER, HUGE, false); eu.put(OWNER, HUGE); }
        boolean pay(Hk3EnergyTick tick, UUID account, BigInteger delta) {
            return pay(tick, account, delta, () -> {});
        }
        boolean pay(Hk3EnergyTick tick, UUID account, BigInteger delta, Runnable beforeRefund) {
            if (refuse || eu.getOrDefault(account, BigInteger.ZERO).add(delta).signum() < 0) return false;
            eu.put(account, eu.getOrDefault(account, BigInteger.ZERO).add(delta));
            tick.undoWith(() -> Hk3GridEnergyRefund.reverse(eu, account, delta, () -> { beforeRefund.run(); dirty.incrementAndGet(); }));
            tick.onCommit(receipts::incrementAndGet);
            return true;
        }
        boolean input(Hk3EnergyTick tick, List<Long> demands) {
            return Hk3GridEnergyPayment.input(demands, () -> eu.get(OWNER), delta -> pay(tick, OWNER, delta), false).remaining() == null;
        }
    }

    public static void main(String[] args) throws Exception {
        net.minecraft.SharedConstants.tryDetectVersion();
        noEnergy(); failureStages(); successfulTicks(); retryAndIdentity(); reentrantFinishes(); generated(); contract();
        com.sirin.hk3gtl.common.capability.RefundPersistenceTest.main(new String[0]);
        System.out.println("Dual energy tick: " + checks + " checks passed; isolated production helpers and wiring, live machine acceptance pending");
    }
    private static void noEnergy() {
        var f = new Fixture(); var tx = new Hk3EnergyTick(); f.hw.setAmount(OWNER, BigInteger.ONE);
        check(!f.hw.reserve(OWNER, BigInteger.TEN, tx), "HW不足全额拒绝");
        check(tx.finish(false) && f.hw.getAmount(OWNER).equals(BigInteger.ONE) && f.eu.get(OWNER).equals(HUGE), "不足未动EU和HW");
        var closed = tx; reject(() -> f.hw.reserve(OWNER, BigInteger.ONE, closed));
        tx = new Hk3EnergyTick(); check(f.hw.reserve(null, BigInteger.ZERO, tx), "无HW费用允许零票据");
        check(!f.hw.reserve(null, BigInteger.ONE, tx), "未绑定不能预留正费用");
        var open = tx; reject(() -> f.hw.reserve(OWNER, BigInteger.valueOf(-1), open));
        check(!HonkaiWirelessNetwork.reserve(OWNER, BigInteger.ONE, tx), "实际网络未启动时不免费预留");
    }
    private static void failureStages() {
        for (int mode = 0; mode < 6; mode++) {
            var f = new Fixture(); var tx = new Hk3EnergyTick(); int failure = mode;
            var progress = new AtomicInteger(12);
            if (mode == 1) f.eu.put(OWNER, BigInteger.valueOf(3));
            BigInteger euBefore = f.eu.get(OWNER);
            try {
                tx.runWork(() -> {
                    check(f.hw.reserve(OWNER, BigInteger.valueOf(17), tx), "已预留HW");
                    tx.onCommit(f.receipts::incrementAndGet);
                    if (failure == 0) f.refuse = true;
                    var result = Hk3RecipeLogic.commitTick(() -> GTRecipe.ActionResult.SUCCESS,
                            () -> f.input(tx, List.of(10L, 20L)), () -> failure != 2);
                    if (!result.isSuccess() || failure == 3) return;
                    if (failure == 4) throw new IllegalStateException("工作回调异常");
                    if (failure == 5) {
                        check(f.pay(tx, OWNER, BigInteger.valueOf(9)), "tick产电实际入账");
                        throw new IllegalStateException("后续输出异常");
                    }
                    progress.incrementAndGet();
                }, () -> progress.get() == 13);
            } catch (IllegalStateException expected) { check(mode >= 4, "仅预期异常"); }
            check(tx.settled() && progress.get() == 12, "拒付、部分、输出、onWorking及异常均不推进");
            check(f.hw.getAmount(OWNER).equals(HUGE) && f.eu.get(OWNER).equals(euBefore), "失败双能源净改量为零");
            check(f.receipts.get() == 0, "失败不算双能源彩蛋");
            check(tx.finish(false) && f.eu.get(OWNER).equals(euBefore), "重复收尾不能重复退款");
        }
    }
    private static void successfulTicks() {
        var f = new Fixture(); int ticks = 20;
        for (int n = 0; n < ticks; n++) {
            var tx = new Hk3EnergyTick(); var progress = new AtomicInteger();
            tx.runWork(() -> {
                check(f.hw.reserve(OWNER, BigInteger.valueOf(7), tx), "每次预留HW");
                tx.onCommit(f.receipts::incrementAndGet);
                check(f.input(tx, List.of(11L, 19L)), "本次EU完整支付");
                check(f.receipts.get() == progress.get(), "预留不提前记录本次回执");
                progress.incrementAndGet();
            }, () -> progress.get() == 1);
            check(tx.finish(false), "已确认不再退款");
            // 下次只比较本次回执时清计数，不改变两个真实账户。
            check(f.receipts.get() == 2, "确认后两能源各一个回执"); f.receipts.set(0);
        }
        check(f.hw.getAmount(OWNER).equals(HUGE.subtract(BigInteger.valueOf(7L * ticks))), "成功累计HW准确");
        check(f.eu.get(OWNER).equals(HUGE.subtract(BigInteger.valueOf(30L * ticks))), "成功累计EU准确");
        var restored = HonkaiWirelessSavedData.load(f.hw.save(new CompoundTag()));
        check(restored.getAmount(OWNER).equals(f.hw.getAmount(OWNER)), "结算后HW可序列化重载");
        var tx = new Hk3EnergyTick();
        check(f.hw.reserve(OWNER, BigInteger.ONE, tx), "已推进后异常场景预留");
        tx.onCommit(() -> { throw new IllegalStateException("回执故障"); });
        tx.onCommit(f.receipts::incrementAndGet);
        reject(() -> tx.runWork(() -> { throw new IllegalStateException("推进之后异常"); }, () -> true));
        check(tx.settled() && tx.failure() != null && f.receipts.get() == 1, "回执异常不撤销已推进且不阻断其他回执");
        check(f.hw.getAmount(OWNER).equals(restored.getAmount(OWNER).subtract(BigInteger.ONE)), "已推进即保留本次费用");
    }
    private static void retryAndIdentity() {
        var f = new Fixture(); var otherWorld = new HonkaiWirelessSavedData();
        otherWorld.insert(OWNER, BigInteger.TEN, false);
        var tx = new Hk3EnergyTick(); f.hw.reserve(OWNER, BigInteger.valueOf(8), tx);
        check(f.pay(tx, OWNER, BigInteger.valueOf(-12)), "绑定原EU账户");
        f.eu.put(OTHER, BigInteger.valueOf(100)); f.eu.put(OWNER, f.eu.get(OWNER).add(BigInteger.valueOf(41)));
        f.hw.insert(OWNER, BigInteger.valueOf(31), false);
        tx.finish(false);
        check(f.eu.get(OWNER).equals(HUGE.add(BigInteger.valueOf(41))) && f.eu.get(OTHER).intValueExact() == 100, "退款只加实际已付差量、不覆盖外部收入或其他账户");
        check(f.hw.getAmount(OWNER).equals(HUGE.add(BigInteger.valueOf(31))) && otherWorld.getAmount(OWNER).equals(BigInteger.TEN), "HW原账本退款不串档");
        var retry = new Hk3EnergyTick(); var calls = new ArrayList<String>(); var reject = new AtomicInteger(1);
        retry.undoWith(() -> calls.add("HW"));
        retry.undoWith(() -> { if (reject.getAndDecrement() > 0) throw new IllegalStateException("暂不可退款"); calls.add("EU"); });
        retry.undoWith(() -> calls.add("OUT"));
        retry.onCommit(() -> calls.add("错误回执"));
        check(!retry.finish(false) && calls.equals(List.of("OUT")), "退款失败保留后续逆序栈");
        reject(() -> retry.onCommit(() -> {})); reject(() -> retry.finish(true));
        check(retry.finish(false) && calls.equals(List.of("OUT", "EU", "HW")), "恢复后精确一次逆序退款");
        retry.finish(false); check(calls.size() == 3, "完成重试不重复退款或回执");
        var balance = new HashMap<UUID, BigInteger>(); balance.put(OWNER, BigInteger.ONE);
        reject(() -> Hk3GridEnergyRefund.reverse(balance, OWNER, BigInteger.TEN, () -> {}));
        check(balance.get(OWNER).equals(BigInteger.ONE), "外部消费后的产电退款不能写负余额");
    }
    private static void reentrantFinishes() {
        for (boolean advanced : new boolean[]{false, true}) {
            var f = new Fixture(); var tx = new Hk3EnergyTick();
            var calls = new ArrayList<String>(); var notifications = new AtomicInteger();
            check(f.hw.reserve(OWNER, BigInteger.valueOf(17), tx), "重入场景实际预留HW");
            tx.undoWith(() -> {
                check(f.eu.get(OWNER).equals(HUGE) && f.hw.getAmount(OWNER).equals(HUGE.subtract(BigInteger.valueOf(17))), "实际逆序先退EU再退HW");
                calls.add("HW");
            });
            check(f.pay(tx, OWNER, BigInteger.valueOf(-23), () -> {
                notifications.incrementAndGet();
                check(!tx.finish(advanced) && !tx.settled() && tx.failure() == null, "实际EU退款通知内同票据重入返回未完成且不改变状态或失败");
                check(f.eu.get(OWNER).equals(HUGE.subtract(BigInteger.valueOf(23))) && f.hw.getAmount(OWNER).equals(HUGE.subtract(BigInteger.valueOf(17))), "通知重入不提前改动实际EU和HW余额");
                calls.add("EU");
            }), "重入场景实际支付EU");
            tx.undoWith(() -> calls.add("OUT"));
            check(tx.finish(false) && tx.settled() && tx.failure() == null && calls.equals(List.of("OUT", "EU", "HW")), "无条件通知重入不阻断首轮逆序退款");
            check(notifications.get() == 1 && f.eu.get(OWNER).equals(HUGE) && f.hw.getAmount(OWNER).equals(HUGE) && f.dirty.get() == 1 && f.receipts.get() == 0, "通知重入只退款及通知一次且无额外双能源入账");
            check(tx.finish(false) && tx.finish(true) && calls.size() == 3 && notifications.get() == 1 && f.eu.get(OWNER).equals(HUGE) && f.hw.getAmount(OWNER).equals(HUGE) && f.dirty.get() == 1, "退款完成后重复收尾幂等且不重复入账");
        }
        {
            var f = new Fixture(); var retry = new Hk3EnergyTick();
            var calls = new ArrayList<String>(); var attempts = new AtomicInteger();
            var temporaryFailure = new IllegalStateException("退款通知暂时故障");
            check(f.hw.reserve(OWNER, BigInteger.valueOf(8), retry), "通知故障场景实际预留HW");
            retry.undoWith(() -> {
                check(f.eu.get(OWNER).equals(HUGE) && f.hw.getAmount(OWNER).equals(HUGE.subtract(BigInteger.valueOf(8))), "恢复后先退EU再退HW");
                calls.add("HW");
            });
            check(f.pay(retry, OWNER, BigInteger.valueOf(-12), () -> {
                check(!retry.finish(false) && !retry.finish(true) && retry.failure() == null, "故障或恢复通知中的重入保持未完成且不伪造失败");
                if (attempts.getAndIncrement() == 0) throw temporaryFailure;
                calls.add("EU");
            }), "通知故障场景实际支付EU");
            retry.undoWith(() -> calls.add("OUT"));
            check(!retry.finish(false) && !retry.settled() && retry.failure() == temporaryFailure && calls.equals(List.of("OUT")) && attempts.get() == 1, "通知故障保留原失败及尚未完成的逆序退款栈");
            check(f.eu.get(OWNER).equals(HUGE.subtract(BigInteger.valueOf(12))) && f.hw.getAmount(OWNER).equals(HUGE.subtract(BigInteger.valueOf(8))) && f.dirty.get() == 0 && f.receipts.get() == 0, "故障退款没有提前或额外入账");
            check(retry.finish(false) && retry.settled() && retry.failure() == null && attempts.get() == 2 && calls.equals(List.of("OUT", "EU", "HW")), "通知恢复后释放保护并按逆序重试且不重复已退回调");
            check(retry.finish(false) && retry.finish(true) && f.eu.get(OWNER).equals(HUGE) && f.hw.getAmount(OWNER).equals(HUGE) && f.dirty.get() == 1 && f.receipts.get() == 0 && attempts.get() == 2, "故障恢复及重复收尾仅精确退还一次双能源");
        }
        var f = new Fixture(); var outer = new Hk3EnergyTick(); var inner = new Hk3EnergyTick();
        check(f.hw.reserve(OWNER, BigInteger.valueOf(11), outer) && f.pay(outer, OWNER, BigInteger.valueOf(-13)), "外层票据支付双能源");
        check(f.hw.reserve(OWNER, BigInteger.valueOf(17), inner) && f.pay(inner, OWNER, BigInteger.valueOf(-19)), "内层票据支付双能源");
        var nested = new AtomicInteger();
        outer.undoWith(() -> {
            nested.incrementAndGet();
            check(inner.finish(false) && inner.settled(), "退款回调可正常结算不同票据");
            check(f.eu.get(OWNER).equals(HUGE.subtract(BigInteger.valueOf(13))) && f.hw.getAmount(OWNER).equals(HUGE.subtract(BigInteger.valueOf(11))), "嵌套退款仅退内层实际费用");
        });
        check(outer.finish(false) && outer.settled() && nested.get() == 1, "不同票据嵌套不被收尾保护误拒绝");
        check(f.eu.get(OWNER).equals(HUGE) && f.hw.getAmount(OWNER).equals(HUGE) && f.dirty.get() == 2 && f.receipts.get() == 0, "两票据嵌套退款无额外双能源入账");
        var committed = new Hk3EnergyTick(); var receiptCalls = new AtomicInteger();
        check(f.hw.reserve(OWNER, BigInteger.valueOf(7), committed) && f.pay(committed, OWNER, BigInteger.valueOf(-11)), "回执重入场景实际支付双能源");
        var receiptFailure = new IllegalStateException("首个回执故障");
        committed.onCommit(() -> { throw receiptFailure; });
        committed.onCommit(() -> {
            receiptCalls.incrementAndGet();
            check(committed.finish(false) && committed.finish(true) && committed.failure() == receiptFailure, "已提交回执内重复收尾幂等并保留原回执失败");
        });
        committed.onCommit(f.receipts::incrementAndGet);
        check(committed.finish(true) && committed.settled() && committed.failure() == receiptFailure && receiptCalls.get() == 1 && f.receipts.get() == 2, "回执重入不重复执行回执且故障不阻断后续回执");
        check(committed.finish(false) && committed.finish(true) && receiptCalls.get() == 1 && f.receipts.get() == 2 && f.eu.get(OWNER).equals(HUGE.subtract(BigInteger.valueOf(11))) && f.hw.getAmount(OWNER).equals(HUGE.subtract(BigInteger.valueOf(7))) && f.dirty.get() == 2, "已提交票据不因回执重入或重复收尾退款");
    }
    private static void generated() {
        var random = new Random(13920261001L);
        for (int i = 0; i < 500; i++) {
            var f = new Fixture(); var tx = new Hk3EnergyTick();
            BigInteger cost = new BigInteger(160, random).add(BigInteger.ONE);
            long eu = random.nextLong() & Long.MAX_VALUE; boolean succeeds = random.nextBoolean();
            check(f.hw.reserve(OWNER, cost, tx), "大额HW完整预留");
            check(f.input(tx, List.of(eu, eu)), "两项大额EU完整支付");
            tx.finish(succeeds);
            check(f.hw.getAmount(OWNER).equals(succeeds ? HUGE.subtract(cost) : HUGE), "生成样本HW守恒");
            check(f.eu.get(OWNER).equals(succeeds ? HUGE.subtract(BigInteger.valueOf(eu).multiply(BigInteger.TWO)) : HUGE), "生成样本EU守恒");
            check(f.receipts.get() == (succeeds ? 1 : 0), "生成样本仅成功回执");
        }
    }
    private static ClassNode node(String suffix) throws Exception {
        try (var in = DualEnergyTickTest.class.getResourceAsStream("/com/sirin/hk3gtl/" + suffix + ".class")) {
            var n = new ClassNode(); new ClassReader(Objects.requireNonNull(in)).accept(n, 0); return n;
        }
    }
    private static boolean calls(ClassNode node, String owner, String name) {
        for (var method : node.methods) for (var insn : method.instructions)
            if (insn instanceof MethodInsnNode call && call.owner.endsWith(owner) && call.name.equals(name)) return true;
        return false;
    }
    private static void contract() throws Exception {
        var logic = node("common/machine/Hk3RecipeLogic");
        check(calls(logic, "/RecipeLogic", "handleRecipeWorking"), "保留GT实际工作入口");
        check(calls(logic, "/Hk3EnergyTick", "runWork"), "生产工作使用finally收尾");
        check(calls(logic, "/HonkaiWirelessNetwork", "reserve"), "实际工作预留HW");
        check(calls(logic, "/Hk3DualEnergyCosts", "getMergedCost"), "保留合并后的真实费用");
        var trait = node("common/machine/trait/Hk3PlayerGridEnergyTrait");
        check(calls(trait, "/Hk3GridEnergyRefund", "capture") && calls(trait, "/Hk3RefundActions", "grid")
                && calls(node("common/capability/Hk3RefundActions"), "/Hk3GridEnergyRefund", "undo"), "EU捕获原账户及持久退款反向差量");
        check(calls(trait, "/Hk3EnergyTick", "onCommit"), "EU回执延后提交");
        var mixin = node("mixin/RecipeLogicMixin");
        check(mixin.methods.stream().noneMatch(m -> m.name.equals("hk3gtl$blocksDualEnergy")), "移除旧HEAD无退款实扣");
        check(!calls(mixin, "/Hk3EggEnergy", "paid"), "旧HEAD无运行回执");
        var network = node("common/capability/HonkaiWirelessNetwork");
        check(calls(network, "/HonkaiWirelessSavedData", "reserve"), "网络调用已测试的实际账本预留");
        var refund = node("common/capability/Hk3GridEnergyRefund");
        check(!calls(refund, "/WirelessEnergyManager", "setUserEU"), "退款不还原旧快照");
        check(calls(refund, "/Hk3GridEnergyRefund", "reverse"), "实际退款调用已测试差量逻辑");
    }
}
