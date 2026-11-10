package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3MaterialTick;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.capability.IDualEnergyConsumer;
import com.sirin.hk3gtl.common.easter.Hk3EggEnergy;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.network.chat.Component;
import java.math.BigInteger;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;

/**
 * 【变更记录 #1】2026-10-01 17:33:35（修订138）
 * 删除：无；新增：本模组单/多配方共用tick实际提交检查，先模拟再输入再输出。
 * 修改：实际输入失败不输出，任一提交失败返回失败给原推进器；保留研究/环境守卫及虚方法派发。
 * 用途：支付失败不能因上层丢弃boolean而继续推进；不替换第三方机器或重写并行规划。
 */
/**
 * 【变更记录 #2】2026-10-01 17:41:38（修订139）
 * 删除：工作入口之外直接结算HK双能源tick的路径。
 * 新增：工作调用票据、真实推进确认、失败逆序退能和待退款暂停。
 * 修改：先通过模拟再预留HW；保留父类实际工作顺序和子类IO派发，成功推进后才发能源彩蛋回执。
 * 用途：解决EU拒付、输出拒绝或onWorking中断时白扣HW/EU；不回滚物品和流体。
 */
/**
 * 【变更记录 #3】2026-10-17 14:44:46（第3次备注 · 内测5修订162）
 * 删除：仅服务退役虚数类型的旧锚扫描守卫调用。
 * 新增：无。修改：保留研究/注视度判定与EU、崩坏能预留、提交、退款和事实回执顺序。
 * 用途：现役工作票据不再依赖已删除设备，当前工业锚定事实仍由自身工艺检查。
 */
/**
 * 【变更记录 #4】2026-10-17 16:27:36（第4次备注 · 修订165）
 * 删除：标记高阶工况可由普通实体仓抢先支付EU的路径。
 * 新增：先额定/余额复检，使用原玩家网事务精确付款，再处理不含EU的tick副本。
 * 修改：保留原工作票据和失败退款；用途：long边界、跨配方总额和IO失败均不能少扣、双扣或白扣。
 */
/**
 * 【变更记录 #5】2026-10-17 16:55:08（第5次备注 · 修订165）
 * 删除：新增守卫的单路额定工程假设。
 * 新增：无；修改：高阶校验沿需求功率与精确费用数据，HK自带玩家网仍使用已有任意精度支付票据。
 * 用途：保留EU/HW预留一次、失败退款及成功事实回执，不将MAX启动材料误加高阶限制。
 */
/**
 * 【变更记录 #6】2026-11-06 00:21:21 Asia/Hong_Kong（第6次备注 · 修订212）
 * 删除：标准本地仓逐刻物料修改不能跟随能源退款的缺口；新增：限定当前配方实际IO的单刻物料记录域。
 * 修改：沿用虚方法派发和真实推进判据，失败按槽位逆序退还；KubeJS动作配方保持原路径。
 * 用途：不覆盖其他机器改写的槽位，不将局部回滚冒充特殊仓、配方首尾或硬崩原子事务。
 */
public class Hk3RecipeLogic extends RecipeLogic {
    private static final org.slf4j.Logger LOGGER = com.mojang.logging.LogUtils.getLogger();
    private static final GTRecipe.ActionResult COMMIT_FAILED = GTRecipe.ActionResult.fail(
            () -> Component.translatable("hk3gtl.machine.recipe_commit_failed"));
    private static final GTRecipe.ActionResult PAUSED = GTRecipe.ActionResult.fail(
            () -> Component.translatable("hk3gtl.compat.environment_paused"));
    private static final GTRecipe.ActionResult NO_HONKAI = GTRecipe.ActionResult.fail(
            () -> Component.translatable("hk3gtl.machine.honkai_payment_failed"));
    private static final GTRecipe.ActionResult UNSUPPORTED = GTRecipe.ActionResult.fail(
            () -> Component.translatable("hk3gtl.machine.energy_scope_required"));
    private Hk3EnergyTick energyTick;
    private boolean workingScope;
    private boolean tickHandled;
    private boolean tickSucceeded;
    private long lastFailureLog;

    public Hk3RecipeLogic(IRecipeLogicMachine machine) { super(machine); }

    public Hk3EnergyTick getEnergyTick() { return workingScope ? energyTick : null; }

    @Override
    public void handleRecipeWorking() {
        if (workingScope) throw new IllegalStateException("不允许嵌套运行同一机器");
        if (!(getMachine().getLevel() instanceof ServerLevel level) || !level.getServer().isSameThread()) return;
        if (energyTick != null && !energyTick.finish(false)) {
            reportFailure(energyTick.failure());
            setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
            return;
        }
        energyTick = new Hk3EnergyTick();
        workingScope = true;
        tickHandled = false;
        tickSucceeded = false;
        int before = progress;
        try {
            energyTick.runWork(super::handleRecipeWorking, () -> tickSucceeded && progress == before + 1);
        } catch (RuntimeException problem) {
            reportFailure(problem);
            setWaiting(Component.translatable("hk3gtl.machine.recipe_commit_failed"));
        } finally {
            // 原版GT及指定GTLCore均在IO成功、onWorking通过后恰好推进一次。
            workingScope = false;
            reportFailure(energyTick.failure());
            if (energyTick.settled()) energyTick = null;
            else setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
        }
    }

    private void reportFailure(RuntimeException problem) {
        if (problem == null) return;
        long now = System.nanoTime();
        if (lastFailureLog != 0 && now - lastFailureLog < 10_000_000_000L) return;
        lastFailureLog = now;
        LOGGER.warn("[HK3GTL] 机器物料或能源结算／退款异常，位置={}", getMachine().getPos(), problem);
    }

    @Override
    public GTRecipe.ActionResult handleTickRecipe(GTRecipe recipe) {
        if (!workingScope || energyTick == null || tickHandled) return UNSUPPORTED;
        tickHandled = true;
        // 未接入工作票据的外部推进器已拒绝；正常路径仍保留只读研究和环境判定。
        try {
            var machine = getMachine();
            var power = Hk3RecipePower.check(recipe, this);
            if (!power.isSuccess()) return power;
            if (Hk3RecipeAccess.blocks(recipe, machine)
                    || Hk3RecipeEnvironment.throttlesByGaze(machine)) return PAUSED;
        } catch (RuntimeException unavailable) { return PAUSED; }
        var result = recipe.hasTick() ? recipe.matchTickRecipe((IRecipeLogicMachine) getMachine()) : GTRecipe.ActionResult.SUCCESS;
        if (!result.isSuccess()) return result;
        if (getMachine() instanceof IDualEnergyConsumer consumer) {
            BigInteger cost = Hk3DualEnergyCosts.getMergedCost(recipe);
            if (cost == null) cost = BigInteger.valueOf(Hk3DualEnergyCosts.resolve(
                    recipe.id, getMachine().getDefinition().getId().getPath()));
            var owner = consumer.getDualEnergyOwner();
            if (!HonkaiWirelessNetwork.reserve(owner, cost, energyTick)) return NO_HONKAI;
            if (cost.signum() > 0) energyTick.onCommit(() -> Hk3EggEnergy.paid(getMachine(), owner, true));
        }
        GTRecipe tickRecipe = recipe;
        if (Hk3RecipePower.marked(recipe)) {
            if (!Hk3RecipePower.pay(recipe, this)) return COMMIT_FAILED;
            tickRecipe = Hk3RecipePower.withoutEU(recipe);
        }
        GTRecipe finalTickRecipe = tickRecipe;
        result = recipe.hasTick() ? Hk3MaterialTick.run(energyTick, finalTickRecipe,
                () -> commitTick(() -> GTRecipe.ActionResult.SUCCESS,
                        () -> handleTickRecipeIO(finalTickRecipe, IO.IN),
                        () -> handleTickRecipeIO(finalTickRecipe, IO.OUT))) : GTRecipe.ActionResult.SUCCESS;
        tickSucceeded = result.isSuccess();
        return result;
    }

    /** 不改写原失败原因；失败输入不能执行输出，回调异常不伪装成功。 */
    public static GTRecipe.ActionResult commitTick(Supplier<GTRecipe.ActionResult> simulate,
                                                  BooleanSupplier input, BooleanSupplier output) {
        var result = simulate.get();
        if (!result.isSuccess()) return result;
        if (!input.getAsBoolean() || !output.getAsBoolean()) return COMMIT_FAILED;
        return GTRecipe.ActionResult.SUCCESS;
    }
}
