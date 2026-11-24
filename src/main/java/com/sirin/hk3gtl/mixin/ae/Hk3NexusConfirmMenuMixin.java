package com.sirin.hk3gtl.mixin.ae;

import appeng.api.config.CpuSelectionMode;
import appeng.api.networking.IGrid;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.sugar.Local;
import appeng.api.networking.crafting.CalculationStrategy;
import appeng.api.networking.crafting.ICraftingCPU;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.ICraftingSubmitResult;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.api.storage.ISubMenuHost;
import appeng.core.sync.packets.CraftConfirmPlanPacket;
import appeng.crafting.execution.CraftingSubmitResult;
import appeng.helpers.IMenuCraftingPacket;
import appeng.me.helpers.PlayerSource;
import appeng.me.cluster.implementations.CraftingCPUCluster;
import appeng.menu.AEBaseMenu;
import appeng.menu.guisync.GuiSync;
import appeng.menu.me.crafting.CraftAmountMenu;
import appeng.menu.me.crafting.CraftConfirmMenu;
import appeng.menu.me.crafting.CraftingPlanSummary;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativeMenus;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativePlan;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactOrderService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusPlanSummary;
import org.gtlcore.gtlcore.integration.ae2.common.ILongCraftConfirmMenu;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.MenuType;
import org.spongepowered.asm.mixin.Dynamic;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Future;

@Mixin(value = CraftConfirmMenu.class, remap = false, priority = 1300)
public abstract class Hk3NexusConfirmMenuMixin extends AEBaseMenu implements Hk3NexusNativeMenus.Confirm {
    @Shadow private ICraftingCPU selectedCpu;
    @Shadow private AEKey whatToCraft;
    @Shadow private int amount;
    @Shadow private Future<ICraftingPlan> job;
    @Shadow private ICraftingPlan result;
    @Shadow private CraftingPlanSummary plan;
    @Shadow @Final private ISubMenuHost host;
    @Shadow private List<IMenuCraftingPacket.AutoCraftEntry> autoCraftingQueue;
    @Shadow public boolean autoStart;
    @Shadow public CraftConfirmMenu.SyncableSubmitResult submitError;
    @Shadow public abstract void clearError();
    @Unique private Hk3NexusNativePlan hk3gtl$exactPlan;
    @Unique private Hk3ExactOrderService.NativePreview hk3gtl$parentPlan;
    @Unique private BigInteger hk3gtl$requested;
    @Unique private CalculationStrategy hk3gtl$strategy;
    @Unique @GuiSync(42) public String hk3gtl$chanceText = "";
    @Unique private List<Hk3ProbabilityOrderService.NexusQuote> hk3gtl$routes = List.of();

    @Inject(method = "<init>", at = @At("TAIL"))
    private void hk3gtl$bindAttempts(int id, Inventory inventory, ISubMenuHost host, CallbackInfo ci) {
        registerClientAction("hk3gtlNexusAttempts", String.class, this::hk3gtl$startProbability);
    }

    @Override public String hk3gtl$probabilityHint() { return hk3gtl$chanceText; }

    @Override public void hk3gtl$startProbability(String attempts) {
        if (isClientSide()) { sendClientAction("hk3gtlNexusAttempts", attempts); return; }
        if (hk3gtl$routes.isEmpty() || !attempts.matches("[1-9][0-9]{0,255}") || !isValidMenu()) return;
        var node = getActionHost().getActionableNode();
        if (node == null || !node.isActive() || node.getGrid() != hk3gtl$exactPlan.grid()
                || !hk3gtl$exactPlan.host().isOn(node.getGrid())) {
            getPlayer().sendSystemMessage(Component.literal("原网络的万象天枢已离线"));
            return;
        }
        try {
            hk3gtl$exactPlan.host().submitProbability(hk3gtl$exactPlan, (ServerPlayer) getPlayer(), hk3gtl$routes, new BigInteger(attempts));
        } catch (IllegalArgumentException unavailable) {
            getPlayer().sendSystemMessage(Component.literal("未提交：" + unavailable.getMessage()));
            return;
        }
        hk3gtl$exactPlan = null;
        hk3gtl$routes = List.of();
        hk3gtl$returnAfterOrder();
    }

    @Unique private void hk3gtl$clearPreview() {
        if (job != null) job.cancel(true);
        job = null;
        result = null;
        plan = null;
        hk3gtl$exactPlan = null;
        hk3gtl$routes = List.of();
        hk3gtl$chanceText = "";
    }

    protected Hk3NexusConfirmMenuMixin(MenuType<?> type, int id, Inventory inventory, Object host) {
        super(type, id, inventory, host);
    }

    @Dynamic("GTLCore 合并到确认页的长整数规划入口")
    @ModifyExpressionValue(method = "gtlcore$planLongAmountJob(Lappeng/api/stacks/AEKey;JLappeng/api/networking/crafting/CalculationStrategy;Z)Z",
            at = @At(value = "INVOKE", target = "Lorg/gtlcore/gtlcore/integration/ae2/graph/CraftingEngineRouter;useGraph()Z"), require = 1)
    private boolean hk3gtl$reserveForCoreGraph(boolean useGraph, @Local IGrid grid) {
        return useGraph && Hk3NexusCrafting.firstOn(grid) == null;
    }

    @Override public void hk3gtl$planAmount(AEKey target, BigInteger requested, CalculationStrategy strategy) {
        if (hk3gtl$parentPlan != null) hk3gtl$parentPlan.cancel();
        hk3gtl$parentPlan = null;
        hk3gtl$clearPreview();
        hk3gtl$strategy = strategy;
        if (requested.bitLength() <= 63) {
            ((ILongCraftConfirmMenu) this).gtlcore$planLongAmountJob(target, requested.longValueExact(), strategy);
            return;
        }
        clearError();
        whatToCraft = target;
        amount = Integer.MAX_VALUE;
        var nexus = Hk3NexusCrafting.firstOn(getActionHost().getActionableNode().getGrid());
        if (nexus == null) hk3gtl$parentPlan = Hk3ExactOrderService.previewNative((CraftConfirmMenu) (Object) this, getActionHost(), target, requested);
        else job = nexus.calculate(target, requested, new PlayerSource(getPlayer(), getActionHost()), strategy);
    }

    @Inject(method = "broadcastChanges", at = @At("HEAD"), remap = true)
    private void hk3gtl$finishNexusPlan(CallbackInfo ci) {
        if (!(job instanceof Hk3NexusCrafting.Calculation pending)) return;
        var node = getActionHost().getActionableNode();
        if (node == null || !node.isActive() || node.getGrid() != pending.grid || !pending.host.isOn(pending.grid) || pending.isCancelled()) {
            hk3gtl$clearPreview();
            getPlayer().sendSystemMessage(Component.literal("规划中断：万象天枢已离开当前网络"));
            setValidMenu(false);
            return;
        }
        if (!pending.isDone()) return;
        job = null;
        if (pending.isCompletedExceptionally()) {
            getPlayer().sendSystemMessage(Component.literal("天枢规划失败，请重新下单"));
            setValidMenu(false);
            return;
        }
        var preview = (Hk3NexusNativePlan) pending.getNow(null);
        hk3gtl$requested = pending.requested;
        hk3gtl$strategy = pending.strategy;
        hk3gtl$exactPlan = preview;
        selectedCpu = preview.host().availableCpu();
        hk3gtl$routes = List.of();
        hk3gtl$chanceText = "";
        if (!preview.probabilityNeeds().isEmpty()) {
            autoStart = false;
            plan = preview.summary();
            if (preview.onlyProbabilityMissing()) {
                try {
                    var routes = Hk3ProbabilityOrderService.nexusQuotes((ServerPlayer) getPlayer(), preview.host().grid(), preview.probabilityNeeds());
                    String title = routes.size() == 1 ? routes.get(0).odds() : routes.size() + " 种概率产物";
                    hk3gtl$chanceText = title + '\n' + String.join("\n", routes.stream()
                            .map(Hk3ProbabilityOrderService.NexusQuote::description).toList());
                    plan = Hk3NexusPlanSummary.of(preview.target(), preview.amount(), preview.exactBytes(), false,
                            Map.of(), Map.of(), preview.probabilityNeeds(), Map.of(), Map.of());
                    hk3gtl$routes = routes;
                } catch (IllegalArgumentException unavailable) {
                    getPlayer().sendSystemMessage(Component.literal("概率合成：" + unavailable.getMessage()));
                }
            }
            sendPacketToClient(new CraftConfirmPlanPacket(plan));
            return;
        }
        if (preview.simulation() && !preview.reason().isEmpty()) getPlayer().sendSystemMessage(Component.literal(preview.reason()));
        plan = preview.summary();
        sendPacketToClient(new CraftConfirmPlanPacket(plan));
        if (autoStart && !plan.isSimulation()) ((CraftConfirmMenu) (Object) this).startJob();
    }

    @Inject(method = "broadcastChanges", at = @At("HEAD"), remap = true)
    private void hk3gtl$finishParentPlan(CallbackInfo ci) {
        if (isClientSide() || hk3gtl$parentPlan == null || plan != null) return;
        hk3gtl$parentPlan.tick();
        if (!hk3gtl$parentPlan.isDone()) return;
        try {
            plan = hk3gtl$parentPlan.summary();
            sendPacketToClient(new CraftConfirmPlanPacket(plan));
            if (autoStart && !plan.isSimulation()) ((CraftConfirmMenu) (Object) this).startJob();
        } catch (Exception failure) {
            hk3gtl$parentPlan.cancel();
            hk3gtl$parentPlan = null;
            getPlayer().sendSystemMessage(Component.literal("规划未提交：" + failure.getMessage()));
            setValidMenu(false);
        }
    }

    @Inject(method = "cpuMatches", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$exactCpu(ICraftingCPU cpu, CallbackInfoReturnable<Boolean> ci) {
        var host = job instanceof Hk3NexusCrafting.Calculation pending ? pending.host
                : hk3gtl$exactPlan != null ? hk3gtl$exactPlan.host() : null;
        if (host != null) ci.setReturnValue(cpu == host.availableCpu());
        else if (hk3gtl$parentPlan != null) ci.setReturnValue(cpu instanceof CraftingCPUCluster && !cpu.isBusy()
                && cpu.getSelectionMode() != CpuSelectionMode.MACHINE_ONLY);
        else if (cpu instanceof Hk3NexusCrafting.NexusCpu) ci.setReturnValue(false);
    }

    @Inject(method = "startJob", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$startNative(CallbackInfo ci) {
        if (isClientSide() || hk3gtl$exactPlan == null && hk3gtl$parentPlan == null) return;
        ci.cancel();
        clearError();
        if (!hk3gtl$routes.isEmpty()) return;
        if (plan == null || plan.isSimulation()) return;
        if (hk3gtl$parentPlan != null) {
            try { hk3gtl$parentPlan.start(selectedCpu); }
            catch (IOException failure) {
                getPlayer().sendSystemMessage(Component.literal("订单未提交：" + failure.getMessage()));
                return;
            }
            hk3gtl$parentPlan = null;
        } else {
            IActionSource source = new PlayerSource(getPlayer(), getActionHost());
            var node = getActionHost().getActionableNode();
            ICraftingSubmitResult submitted = node == null || !node.isActive() ? CraftingSubmitResult.CPU_OFFLINE
                    : node.getGrid().getCraftingService().submitJob(hk3gtl$exactPlan, null, selectedCpu, true, source);
            if (!submitted.successful()) {
                submitError = new CraftConfirmMenu.SyncableSubmitResult(submitted);
                return;
            }
            hk3gtl$exactPlan = null;
        }
        hk3gtl$returnAfterOrder();
    }

    @Unique private void hk3gtl$returnAfterOrder() {
        autoStart = false;
        if (autoCraftingQueue != null && !autoCraftingQueue.isEmpty())
            CraftConfirmMenu.openWithCraftingList(getActionHost(), (ServerPlayer) getPlayer(), getLocator(), autoCraftingQueue);
        else host.returnToMainMenu(getPlayer(), (CraftConfirmMenu) (Object) this);
    }

    @Inject(method = "goBack", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$backNative(CallbackInfo ci) {
        var requested = hk3gtl$requestedAmount();
        if (isClientSide() || requested == null) return;
        ci.cancel();
        AEKey target = whatToCraft;
        if (hk3gtl$parentPlan != null) hk3gtl$parentPlan.cancel();
        hk3gtl$parentPlan = null;
        hk3gtl$exactPlan = null;
        CraftAmountMenu.open((ServerPlayer) getPlayer(), getLocator(), target, 1);
        if (getPlayer().containerMenu instanceof CraftAmountMenu menu) {
            ((Hk3NexusNativeMenus.Amount) menu).hk3gtl$initialAmount(requested.toString());
            menu.broadcastChanges();
        }
    }

    @Inject(method = "replan", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$replanNative(CallbackInfo ci) {
        var requested = hk3gtl$requestedAmount();
        if (isClientSide() || requested == null) return;
        ci.cancel();
        hk3gtl$planAmount(whatToCraft, requested, job instanceof Hk3NexusCrafting.Calculation pending ? pending.strategy : hk3gtl$strategy);
    }

    @Unique private BigInteger hk3gtl$requestedAmount() {
        if (job instanceof Hk3NexusCrafting.Calculation pending) return pending.requested;
        if (hk3gtl$exactPlan != null) return hk3gtl$requested;
        return hk3gtl$parentPlan != null ? hk3gtl$parentPlan.amount() : null;
    }

    @Inject(method = "removed", at = @At("HEAD"), remap = true)
    private void hk3gtl$closeNativePlan(net.minecraft.world.entity.player.Player player, CallbackInfo ci) {
        if (job instanceof Hk3NexusCrafting.Calculation) hk3gtl$clearPreview();
        if (hk3gtl$parentPlan != null) hk3gtl$parentPlan.cancel();
        hk3gtl$parentPlan = null;
        hk3gtl$exactPlan = null;
    }
}
