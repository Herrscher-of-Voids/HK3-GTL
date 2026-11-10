package com.sirin.hk3gtl.test.energy;

import com.sirin.hk3gtl.common.machine.energy.Hk3ReactorEnergyExecutor;
import com.sirin.hk3gtl.common.machine.energy.Hk3ReactorEnergyProfile;
import com.sirin.hk3gtl.common.machine.energy.Hk3ReactorEnergyData;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;
import net.minecraft.nbt.CompoundTag;

import java.math.BigInteger;
import java.util.List;
import java.util.UUID;

/**
 * 文件职责：验证 I19-I22 公共能源执行器的合同、输出拒绝、BigInteger 产电和账本重载。
 * 变更记录 #1 · 2026-10-18 21:46:33 · 修订167
 * - 删除：无。
 * - 新增：四级反应堆合同、输出拒绝不推进、超 long 产电和严格 SavedData 往返回归。
 * - 修改：无；仅使用隔离对象，不启动游戏世界或注册未经批准结构。
 * - 用途：验证后续获批控制器可以复用的公共核心，避免把静态负 EUt 当成已完成发电。
 * 变更记录 #2 · 2026-10-18 22:44:26 · 修订169
 * - 删除：无；保留原合同、累计量和NBT回归。
 * - 新增：验证未完成批次清理会被拒绝且状态保留，完成后才允许按策略删除。
 * - 修改：隔离测试现在覆盖账本清理边界，未启动Minecraft，也未绑定多方块结构。
 * - 用途：保护未来反应堆长时间运行时的持久进度，避免批次上限治理误伤活动工况。
 * 变更记录 #3 · 2026-10-18 23:13:00 · 修订170
 * - 删除：只核验计划第一项燃料输入的弱断言。
 * - 新增：逐配方核验四台反应堆的研究门槛、完整物品/流体进出、事实、工时、电压与暂定状态。
 * - 修改：按配方ID取能源合同，保证同一职责后续增加独立工况时批次仍能准确绑定。
 * - 用途：验证能源合同来自同一份工业计划，防止遗漏冷却液、乏燃料或研究条件。
 */
public final class ReactorEnergyExecutorTest {
    private static int checks;

    private record ExpectedPlan(String role, String recipeId, int tier, String prerequisite,
                                List<Hk3ResearchProcessPlans.Item> itemInputs,
                                List<Hk3ResearchProcessPlans.Item> itemOutputs,
                                List<Hk3ResearchProcessPlans.Fluid> fluidInputs,
                                List<Hk3ResearchProcessPlans.Fluid> fluidOutputs,
                                List<String> facts) {}

    private static void check(boolean ok, String message) {
        checks++;
        if (!ok) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        contracts();
        retryAndPersist();
        hugeOutput();
        System.out.println("Reactor energy executor: " + checks + " checks passed; structure binding remains approval-gated");
    }

    private static void contracts() {
        List<ExpectedPlan> expected = List.of(
                new ExpectedPlan("I19", "industrial_reactor_i19", 15, "RN-SRE",
                        List.of(item("hk3gtl:honkai_fuel_rod", 1)), List.of(item("hk3gtl:depleted_honkai_fuel_rod", 1)),
                        List.of(fluid("honkai_coolant", 1000)), List.of(fluid("hot_honkai_coolant", 1000)),
                        List.of("reactor_load", "reactor_spent_rod")),
                new ExpectedPlan("I20", "industrial_reactor_i20", 19, "RN-MRE",
                        List.of(item("hk3gtl:dense_honkai_fuel_rod", 2)), List.of(item("hk3gtl:depleted_dense_honkai_fuel_rod", 2)),
                        List.of(fluid("honkai_coolant", 2000)), List.of(fluid("hot_honkai_coolant", 2000)),
                        List.of("medium_reactor_load")),
                new ExpectedPlan("I21", "industrial_reactor_i21", 23, "RN-LRE",
                        List.of(item("hk3gtl:dense_honkai_fuel_rod", 4)), List.of(item("hk3gtl:depleted_dense_honkai_fuel_rod", 4)),
                        List.of(fluid("honkai_coolant", 4000)), List.of(fluid("hot_honkai_coolant", 4000)),
                        List.of("large_reactor_load")),
                new ExpectedPlan("I22", "industrial_reactor_i22", 28, "RN-URE",
                        List.of(item("hk3gtl:dense_honkai_fuel_rod", 8)), List.of(item("hk3gtl:depleted_dense_honkai_fuel_rod", 8)),
                        List.of(fluid("honkai_coolant", 8000)), List.of(fluid("hot_honkai_coolant", 8000)),
                        List.of("ultra_reactor_load")));
        check(Hk3ReactorEnergyProfile.all().size() >= expected.size(), "四个反应堆合同均已建立且允许后续扩展");
        for (ExpectedPlan spec : expected) {
            Hk3ReactorEnergyProfile profile = Hk3ReactorEnergyProfile.get(spec.recipeId());
            Hk3ResearchProcessPlans.Plan plan = profile.plan();
            check(profile.role().equals(spec.role()), spec.recipeId() + "机器职责准确");
            check(profile.voltageTier() == spec.tier(), spec.role() + "电压映射准确");
            check(plan.requirements().equals(List.of(spec.prerequisite())), spec.role() + "研究门槛准确");
            check(plan.inputs().equals(spec.itemInputs()), spec.role() + "完整燃料输入准确");
            check(plan.outputs().equals(spec.itemOutputs()), spec.role() + "完整乏燃料输出准确");
            check(plan.fluidInputs().equals(spec.fluidInputs()), spec.role() + "完整冷却液输入准确");
            check(plan.fluidOutputs().equals(spec.fluidOutputs()), spec.role() + "完整热冷却液输出准确");
            check(plan.ticks() == 3600 && profile.totalTicks() == plan.ticks(), spec.role() + "工时合同一致");
            check(plan.energyDirection().equals("output"), spec.role() + "确认为发电方向");
            check(plan.facts().equals(spec.facts()), spec.role() + "生产事实清单准确");
            check(plan.catalysts().isEmpty() && plan.experiment().isBlank(), spec.role() + "催化剂与实验合同准确");
            check(profile.provisional(), spec.role() + "暂定状态保留，不冒充最终配方");
            check(Hk3ReactorEnergyProfile.forRole(spec.role()).contains(profile), spec.role() + "按职责可检索多配方合同");
            check(Hk3ReactorEnergyExecutor.depletedOutput(spec.recipeId()).equals(spec.itemOutputs().get(0).id()), spec.role() + "乏燃料查询按配方绑定");
        }
        check(!Hk3ReactorEnergyProfile.forRole("I19").isEmpty(), "I19合同可按角色分组读取");
    }

    private static Hk3ResearchProcessPlans.Item item(String id, int count) {
        return new Hk3ResearchProcessPlans.Item(id, count);
    }

    private static Hk3ResearchProcessPlans.Fluid fluid(String id, int amount) {
        return new Hk3ResearchProcessPlans.Fluid(id, amount);
    }

    private static void retryAndPersist() {
        UUID owner = UUID.randomUUID();
        var batch = Hk3ReactorEnergyExecutor.start(owner, "industrial_reactor_i19");
        BigInteger[] bank = {BigInteger.ZERO};
        var blocked = Hk3ReactorEnergyExecutor.advance(batch, 1, eu -> false);
        check(blocked.equals(batch), "输出拒绝时不推进批次");
        batch = Hk3ReactorEnergyExecutor.advance(batch, 120, eu -> {
            bank[0] = bank[0].add(eu);
            return true;
        });
        check(batch.elapsedTicks() == 120 && bank[0].equals(Hk3ReactorEnergyProfile.get("industrial_reactor_i19").euPerTick().multiply(BigInteger.valueOf(120))), "区间产电守恒");
        Hk3ReactorEnergyData savedData = new Hk3ReactorEnergyData();
        savedData.put(batch);
        CompoundTag saved = savedData.save(new CompoundTag());
        var loadedData = Hk3ReactorEnergyData.load(saved);
        var loaded = loadedData.get(batch.batchId());
        check(loaded.equals(batch), "世界账本重载保持批次身份和累计量");
        var savedBatch = batch;
        expectRejected(() -> loadedData.put(new Hk3ReactorEnergyExecutor.Batch(savedBatch.batchId(), owner, savedBatch.role(),
                savedBatch.recipeId(), 60, savedBatch.totalTicks(), Hk3ReactorEnergyProfile.get(savedBatch.recipeId()).euPerTick().multiply(BigInteger.valueOf(60)), false)),
                "拒绝回退已记账的能源游标");
        expectRejected(() -> loadedData.put(new Hk3ReactorEnergyExecutor.Batch(savedBatch.batchId(), UUID.randomUUID(), savedBatch.role(),
                savedBatch.recipeId(), savedBatch.elapsedTicks(), savedBatch.totalTicks(), savedBatch.generatedEu(), false)),
                "拒绝复用批次ID更改归属");
        expectRejected(() -> loadedData.put(new Hk3ReactorEnergyExecutor.Batch(savedBatch.batchId(), owner, "I20",
                Hk3ReactorEnergyProfile.get("industrial_reactor_i20").recipeId(), savedBatch.elapsedTicks(), Hk3ReactorEnergyProfile.get("industrial_reactor_i20").totalTicks(),
                Hk3ReactorEnergyProfile.get("industrial_reactor_i20").euPerTick().multiply(BigInteger.valueOf(savedBatch.elapsedTicks())), false)),
                "拒绝复用批次ID更改机器职责");
        var finished = Hk3ReactorEnergyExecutor.advance(loaded, 10_000, eu -> { bank[0] = bank[0].add(eu); return true; });
        check(finished.completed() && finished.elapsedTicks() == 3600, "批次完成只到合同工时");
        var replay = Hk3ReactorEnergyExecutor.advance(finished, 1, eu -> { throw new AssertionError("完成批次不应重复输出"); });
        check(replay.equals(finished), "已完成游标不会继续推进");
        expectRejected(() -> loadedData.remove(finished.batchId()), "拒绝清理未完成批次");
        check(loadedData.get(finished.batchId()).equals(loaded), "拒绝清理后保留未完成批次");
        loadedData.put(finished);
        loadedData.remove(finished.batchId());
        check(loadedData.get(finished.batchId()) == null, "已完成批次可按审核策略清理");
    }

    private static void hugeOutput() {
        var batch = Hk3ReactorEnergyExecutor.start(UUID.randomUUID(), "industrial_reactor_i22");
        BigInteger[] accepted = {BigInteger.ZERO};
        var done = Hk3ReactorEnergyExecutor.advance(batch, 3600, eu -> {
            accepted[0] = accepted[0].add(eu);
            return true;
        });
        BigInteger expected = Hk3ReactorEnergyProfile.get("industrial_reactor_i22").totalEu();
        check(done.generatedEu().equals(expected), "I22总产电使用BigInteger不溢出");
        check(expected.compareTo(BigInteger.valueOf(Long.MAX_VALUE)) > 0, "I22总产电超过long边界仍可结算");
        check(accepted[0].equals(expected), "I22输出端实收金额等于批次总额");
        CompoundTag tampered = done.toNbt();
        tampered.putString("role", "I21");
        expectInvalid(tampered, "错误角色");
        tampered = done.toNbt();
        tampered.putString("recipeId", "industrial_reactor_i21");
        expectInvalid(tampered, "错误配方");
        tampered = done.toNbt();
        tampered.putInt("totalTicks", 3599);
        expectInvalid(tampered, "错误工时");
        tampered = done.toNbt();
        tampered.putString("generatedEu", expected.add(BigInteger.ONE).toString());
        expectInvalid(tampered, "伪造累计电量");
        tampered = done.toNbt();
        tampered.putString("unexpected", "reject");
        expectInvalid(tampered, "未知状态字段");
    }

    private static void expectInvalid(CompoundTag tag, String description) {
        try {
            Hk3ReactorEnergyExecutor.Batch.fromNbt(tag);
            throw new AssertionError(description + "未拒绝");
        } catch (IllegalArgumentException expectedFailure) {
            checks++;
        }
    }

    private static void expectRejected(Runnable action, String description) {
        try {
            action.run();
            throw new AssertionError(description + "未拒绝");
        } catch (IllegalArgumentException | IllegalStateException expectedFailure) {
            checks++;
        }
    }
}
