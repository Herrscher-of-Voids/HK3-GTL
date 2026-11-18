package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.stacks.AEKey;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

import java.math.BigInteger;
import java.util.List;
import java.util.Map;

import static com.sirin.hk3gtl.common.integration.ae.exact.Hk3AeExactPlanAdapterTest.*;

/** 接真实 AE 计划类型，核对循环种子、压缩游标及持久化；不伪装客户端验收。 */
public final class Hk3ExactProgramTest {
    private static int checks;
    public static void main(String[] args) throws Exception {
        cursor();
        cycleAdapterAndNbt();
        multiOutput();
        wideSingleJob();
        alternativeCapacity();
        System.out.println("AE严格程序离线核验通过：" + checks + "项；未运行真实CPU/Mixin。");
    }

    private static void cursor() {
        var steps = List.of(new Hk3ExactPlanner.Step<>(List.of("a", "b"), BigInteger.ONE.shiftLeft(120)),
                new Hk3ExactPlanner.Step<>(List.of("c"), n(3)));
        var cursor = new Hk3ExactProgramCursor<>(steps);
        check(cursor.current().equals("a"), "先执行证书首项");
        cursor.pushed();
        check(cursor.current() == null && cursor.waiting(), "未回流不能推进");
        check(cursor.remainingCounts().get("a").equals(BigInteger.ONE.shiftLeft(120).subtract(n(1))), "大数重复不展开");
        check(cursor.remainingCounts().get("b").equals(BigInteger.ONE.shiftLeft(120)), "当前轮后项尚未扣除");
        rejected(cursor::pushed, "同一步不能重复投料");
        var restored = new Hk3ExactProgramCursor<>(steps, cursor.position());
        check(restored.remainingCounts().equals(cursor.remainingCounts()) && restored.waiting(), "重启保留在途");
        restored.returned(); check(restored.current().equals("b"), "回流后才进入下一样板");
        restored.pushed(); restored.returned(); check(restored.current().equals("a"), "有序整轮重复");
        rejected(() -> new Hk3ExactProgramCursor<>(steps, new Hk3ExactProgramCursor.Position(0, 2, n(1), false)), "坏索引拒绝重置");
        rejected(() -> new Hk3ExactProgramCursor<>(steps, new Hk3ExactProgramCursor.Position(0, 0, n(0), false)), "坏重复量拒绝重置");
        var last = new Hk3ExactProgramCursor<>(List.of(new Hk3ExactPlanner.Step<>(List.of("x"), n(1))));
        last.pushed(); check(last.exhausted() && !last.done(), "全部投料不等于产出完成");
        last.returned(); check(last.done() && last.remainingCounts().isEmpty(), "末批真实回流后结束");
    }

    private static void cycleAdapterAndNbt() throws Exception {
        AEKey a = key("seed"), b = key("cycle_middle");
        Pattern forward = new Pattern("forward"), back = new Pattern("back");
        var snapshot = snapshot(a, Map.of(a, n(1)), graph(recipe(forward, Map.of(a, n(1)), b, n(1)),
                recipe(back, Map.of(b, n(1)), a, n(2))), n(5));
        var detail = snapshot.planDetailed(n(10), () -> false);
        check(detail.result().successful() && detail.orderedExecutionRequired(), "有库存的增益环进入严格程序");
        var nativePlan = Hk3AeExactPlanAdapter.toNative(snapshot, 10, detail).orElseThrow();
        check(nativePlan instanceof Hk3ExactProgramPlan, "执行证书真正接入可提交计划");
        var plan = (Hk3ExactProgramPlan) nativePlan;
        check(plan.targetSeed() == 1 && plan.usedItems().get(a) == 1, "原生抽取真实启动种子");
        check(plan.patternTimes().get(forward) == 10 && plan.patternTimes().get(back) == 10, "样板次数守恒");
        check(detail.result().surplus().get(a).equals(n(1)), "成品新增十个以外归还种子");
        var program = new Hk3ExactCpuProgram(plan);
        program.cursor().pushed();
        CompoundTag saved = program.write(pattern -> { var tag = new CompoundTag(); tag.putString("id", ((Pattern) pattern).name()); return tag; });
        var patterns = Map.<String, IPatternDetails>of("forward", forward, "back", back);
        var counts = program.cursor().remainingCounts();
        var loaded = Hk3ExactCpuProgram.read(saved, tag -> patterns.get(tag.getString("id")), counts, 10);
        check(loaded.cursor().waiting() && loaded.cursor().remainingCounts().equals(counts), "CPU程序连同真实剩余任务恢复");
        check(loaded.targetSeed() == 1, "CPU恢复种子基线");
        rejected(() -> Hk3ExactCpuProgram.read(saved, tag -> patterns.get(tag.getString("id")), Map.of(forward, n(10)), 10), "原生任务不符冻结");
        CompoundTag corrupt = saved.copy(); corrupt.remove("remaining");
        rejected(() -> Hk3ExactCpuProgram.read(corrupt, tag -> patterns.get(tag.getString("id")), counts, 10), "缺字段拒绝恢复");
        CompoundTag badIndex = saved.copy(); badIndex.getList("steps", Tag.TAG_COMPOUND).getCompound(0).putIntArray("recipes", new int[]{99});
        rejected(() -> Hk3ExactCpuProgram.read(badIndex, tag -> patterns.get(tag.getString("id")), counts, 10), "坏样板索引拒绝恢复");
        check(snapshot(a, Map.of(), graph(recipe(forward, Map.of(a, n(1)), b, n(1)),
                recipe(back, Map.of(b, n(1)), a, n(2))), n(5)).planDetailed(n(10), () -> false).result().status()
                == Hk3ExactPlanner.Status.MISSING_INPUT, "没有种子不能凭净收益自举");
    }

    private static void multiOutput() throws Exception {
        AEKey ore = key("multi_ore"), left = key("multi_left"), right = key("multi_right"), target = key("multi_target");
        Pattern split = new Pattern("split"), make = new Pattern("make");
        var pair = new Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>(split, Map.of(ore, n(1)), Map.of(left, n(2), right, n(3)), n(1));
        var graph = graph(pair, recipe(make, Map.of(left, n(2), right, n(3)), target, n(1)));
        var snapshot = snapshot(target, Map.of(ore, n(10)), graph, n(5));
        var detailed = snapshot.planDetailed(n(10), () -> false);
        check(detailed.result().successful() && detailed.result().batches().get(split).equals(n(10)), "共生副产物只投一次料");
        var plan = Hk3AeExactPlanAdapter.toNative(snapshot, 10, detailed).orElseThrow();
        check(plan.usedItems().get(ore) == 10 && plan.patternTimes().get(split) == 10, "共生产物计划真实接原生次数");
    }

    private static void wideSingleJob() throws Exception {
        AEKey ore = key("wide_ore"), target = key("wide_target");
        long amount = Long.MAX_VALUE / 2;
        var snapshot = snapshot(target, Map.of(ore, n(amount)), graph(recipe(new Pattern("wide"), Map.of(ore, n(1)), target, n(1))), n(2));
        var detailed = snapshot.planDetailed(n(amount), () -> false);
        var plan = Hk3AeExactPlanAdapter.toNative(snapshot, amount, detailed).orElseThrow();
        check(plan.bytes() == Long.MAX_VALUE && Hk3ExactCpuCapacity.requiredBytes(plan).compareTo(n(Long.MAX_VALUE)) > 0,
                "单任务精确字节超过long而非仅父订单分批");
        var batch = Hk3ExactBatchPlanner.select(snapshot, n(amount), n(Long.MAX_VALUE).multiply(n(2)), () -> false);
        check(batch != null && batch.amount() == amount, "单CPU超long容量真正容纳整份本批任务");
    }

    private static void alternativeCapacity() throws Exception {
        AEKey a = key("expensive_input"), b = key("cheap_input"), target = key("alternate_target");
        Pattern expensive = new Pattern("expensive"), cheap = new Pattern("cheap");
        var snapshot = snapshot(target, Map.of(a, n(100), b, n(100)), Map.of(target,
                List.of(recipe(expensive, Map.of(a, n(100)), target, n(1)), recipe(cheap, Map.of(b, n(1)), target, n(1))),
                a, List.of(), b, List.of()), n(3));
        var one = Hk3ExactBatchPlanner.select(snapshot, n(1), n(50), () -> false);
        check(one != null && one.amount() == 1 && one.plan().patternTimes().containsKey(cheap),
                "首路线库存可行但容量不足时选可装入CPU的备选");
        var two = Hk3ExactBatchPlanner.select(snapshot, n(2), n(50), () -> false);
        check(two != null && two.amount() == 2 && two.plan().patternTimes().containsKey(cheap),
                "候选接纳在搜索内部保持容量二分单调");
    }

    private static void rejected(Runnable action, String message) {
        try { action.run(); } catch (IllegalArgumentException | IllegalStateException failure) { check(true, message); return; }
        throw new AssertionError(message);
    }
    private static void check(boolean condition, String message) { checks++; if (!condition) throw new AssertionError(message); }
}
