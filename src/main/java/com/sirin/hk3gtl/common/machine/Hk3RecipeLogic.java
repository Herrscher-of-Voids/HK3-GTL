package com.sirin.hk3gtl.common.machine;

import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3CrossMachineOrders;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import com.sirin.hk3gtl.common.research.Hk3ResearchHwLoad;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.capability.Hk3MaterialTick;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.capability.IDualEnergyConsumer;
import com.sirin.hk3gtl.common.easter.Hk3EggEnergy;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.network.chat.Component;
import java.math.BigInteger;
import java.util.UUID;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;

 





 






 





 





 





 





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
    private Hk3ResearchHwLoad hwLoad;
    private boolean workingScope;
    private boolean tickHandled;
    private boolean tickSucceeded;
    private long lastFailureLog;

    public Hk3RecipeLogic(IRecipeLogicMachine machine) { super(machine); }

    public boolean dispatchProbabilityOrder() {
        boolean handled = Hk3ProbabilitySupport.AVAILABLE
                && com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService.find(this);
        if (handled) { lastFailedMatches = null; lastOriginRecipe = null; }
        return handled;
    }

    @Override public void findAndHandleRecipe() {
        if (!dispatchProbabilityOrder()) super.findAndHandleRecipe();
    }

    @Override public void onRecipeFinish() {
        if (Hk3ProbabilitySupport.AVAILABLE
                && com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService.blocksFinish(this)) {
            setWaiting(Component.literal("专属概率订单完成条件待恢复，原批次令牌保留"));
            return;
        }
        super.onRecipeFinish();
    }

    @Override protected boolean handleRecipeIO(GTRecipe recipe, com.gregtechceu.gtceu.api.capability.recipe.IO io) {
        if (Hk3ProbabilitySupport.AVAILABLE) {
            Boolean result = com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService.input(this, recipe, io);
            if (result != null) return result;
        }
        boolean handled = super.handleRecipeIO(recipe, io);
        if (handled && io == IO.IN)
            Hk3CrossMachineOrders.started((Hk3WorkableMultiblockMachine) getMachine(), recipe);
        return handled;
    }

    public Hk3EnergyTick getEnergyTick() { return workingScope ? energyTick : null; }

    public void recordEuPayment(UUID payer, BigInteger amount) { hwLoad.grid(payer, amount); }

    public boolean retryPendingRefund() {
        if (workingScope) return true;
        try {
            if (energyTick == null) energyTick = Hk3RefundJournal.resume(getMachine());
            if (energyTick == null) return true;
            if (energyTick.finish(false)) { energyTick = null; return true; }
            reportFailure(energyTick.failure());
        } catch (RuntimeException problem) { reportFailure(problem); }
        setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
        return false;
    }

    @Override
    public void handleRecipeWorking() {
        if (Hk3ProbabilitySupport.AVAILABLE
                && com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService.blocksWork(this)) {
            setWaiting(Component.literal("专属概率订单已暂停，原批次令牌保留"));
            return;
        }
        if (workingScope) throw new IllegalStateException("不允许嵌套运行同一机器");
        if (!(getMachine().getLevel() instanceof ServerLevel level) || !level.getServer().isSameThread()) return;
        if (!retryPendingRefund()) return;
        try { energyTick = Hk3RefundJournal.open(getMachine()); }
        catch (RuntimeException problem) {
            reportFailure(problem);
            setWaiting(Component.translatable("hk3gtl.machine.energy_refund_pending"));
            return;
        }
        workingScope = true;
        hwLoad = new Hk3ResearchHwLoad((Hk3WorkableMultiblockMachine) getMachine());
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
            hwLoad = null;
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
            hwLoad.honkai(owner, cost);
            if (cost.signum() > 0) {
                BigInteger committedCost = cost;
                energyTick.onCommit(() -> Hk3EggEnergy.paid(getMachine(), owner, true));
                energyTick.onCommit(() -> com.sirin.hk3gtl.common.dispatch.Hk3EnergyDispatch.paid(getMachine(), owner, committedCost, recipe));
            }
        }
        GTRecipe tickRecipe = recipe;
        if (Hk3RecipePower.marked(recipe)) {
            if (!Hk3RecipePower.pay(recipe, this)) return COMMIT_FAILED;
            tickRecipe = Hk3RecipePower.withoutEU(recipe);
        }
        GTRecipe finalTickRecipe = tickRecipe;
        result = recipe.hasTick() ? Hk3MaterialTick.run(energyTick, finalTickRecipe, this,
                () -> commitTick(() -> GTRecipe.ActionResult.SUCCESS,
                        () -> handleTickRecipeIO(finalTickRecipe, IO.IN),
                        () -> handleTickRecipeIO(finalTickRecipe, IO.OUT))) : GTRecipe.ActionResult.SUCCESS;
        tickSucceeded = result.isSuccess();
        if (tickSucceeded) {
            energyTick.onCommit(() -> Hk3EggEnergy.worked(getMachine()));
            energyTick.onCommit(() -> hwLoad.worked(recipe));
        }
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
