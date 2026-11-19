package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.crafting.CalculationStrategy;
import appeng.api.config.CpuSelectionMode;
import appeng.api.networking.crafting.ICraftingCPU;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.ICraftingSubmitResult;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.api.storage.ISubMenuHost;
import appeng.core.sync.packets.CraftConfirmPlanPacket;
import appeng.helpers.IMenuCraftingPacket;
import appeng.me.helpers.PlayerSource;
import appeng.me.cluster.implementations.CraftingCPUCluster;
import appeng.menu.AEBaseMenu;
import appeng.menu.me.crafting.CraftAmountMenu;
import appeng.menu.me.crafting.CraftConfirmMenu;
import appeng.menu.me.crafting.CraftingPlanSummary;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativeMenus;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativePlan;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactOrderService;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.MenuType;
import org.gtlcore.gtlcore.integration.ae2.common.ILongCraftConfirmMenu;
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
import java.util.concurrent.Future;

@Mixin(value = CraftConfirmMenu.class, remap = false, priority = 900)
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

    protected Hk3NexusConfirmMenuMixin(MenuType<?> type, int id, Inventory inventory, Object host) {
        super(type, id, inventory, host);
    }

    @Override public void hk3gtl$planNexus(AEKey target, BigInteger requested) {
        hk3gtl$planWithNexus(target, requested, CalculationStrategy.REPORT_MISSING_ITEMS);
    }

    @Unique
    private boolean hk3gtl$planWithNexus(AEKey target, BigInteger requested, CalculationStrategy strategy) {
        if (hk3gtl$parentPlan != null) hk3gtl$parentPlan.cancel();
        hk3gtl$parentPlan = null;
        if (job != null) job.cancel(true);
        job = null;
        result = null;
        clearError();
        whatToCraft = target;
        amount = requested.min(BigInteger.valueOf(Integer.MAX_VALUE)).intValue();
        var runtimes = Hk3NexusCrafting.forGrid(getActionHost().getActionableNode().getGrid());
        var preview = runtimes.get(0).preview(target, requested, getPlayer().getUUID());
        if (preview.simulation() && requested.compareTo(BigInteger.valueOf(Long.MAX_VALUE)) <= 0) {
            hk3gtl$exactPlan = null;
            return ((ILongCraftConfirmMenu) (Object) this).gtlcore$planLongAmountJob(target, requested.longValueExact(), strategy);
        }
        hk3gtl$exactPlan = preview;
        result = hk3gtl$exactPlan;
        plan = hk3gtl$exactPlan.summary();
        sendPacketToClient(new CraftConfirmPlanPacket(plan));
        broadcastChanges();
        if (autoStart && !plan.isSimulation()) ((CraftConfirmMenu) (Object) this).startJob();
        return true;
    }

    @Override public void hk3gtl$planParent(AEKey target, BigInteger requested) {
        if (job != null) job.cancel(true);
        if (hk3gtl$parentPlan != null) hk3gtl$parentPlan.cancel();
        job = null;
        result = null;
        plan = null;
        hk3gtl$exactPlan = null;
        clearError();
        whatToCraft = target;
        amount = requested.min(BigInteger.valueOf(Integer.MAX_VALUE)).intValue();
        hk3gtl$parentPlan = Hk3ExactOrderService.previewNative((CraftConfirmMenu) (Object) this, getActionHost(), target, requested);
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

    @Inject(method = "planJob", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$planNative(AEKey target, int requested, CalculationStrategy strategy, CallbackInfoReturnable<Boolean> ci) {
        if (isClientSide()) return;
        if (!Hk3NexusCrafting.forGrid(getActionHost().getActionableNode().getGrid()).isEmpty()) {
            ci.setReturnValue(hk3gtl$planWithNexus(target, BigInteger.valueOf(requested), strategy));
        }
    }

    @Inject(method = "cpuMatches", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$exactCpu(ICraftingCPU cpu, CallbackInfoReturnable<Boolean> ci) {
        if (hk3gtl$exactPlan != null) ci.setReturnValue(cpu instanceof Hk3NexusCrafting.NexusCpu && !cpu.isBusy());
        else if (hk3gtl$parentPlan != null) ci.setReturnValue(cpu instanceof CraftingCPUCluster && !cpu.isBusy()
                && cpu.getSelectionMode() != CpuSelectionMode.MACHINE_ONLY);
        else if (cpu instanceof Hk3NexusCrafting.NexusCpu) ci.setReturnValue(false);
    }

    @Inject(method = "startJob", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$startNative(CallbackInfo ci) {
        if (isClientSide() || hk3gtl$exactPlan == null && hk3gtl$parentPlan == null) return;
        ci.cancel();
        clearError();
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
            var grid = getActionHost().getActionableNode().getGrid();
            ICraftingSubmitResult submitted = grid.getCraftingService().submitJob(hk3gtl$exactPlan, null, selectedCpu, true, source);
            if (!submitted.successful()) {
                submitError = new CraftConfirmMenu.SyncableSubmitResult(submitted);
                return;
            }
            hk3gtl$exactPlan = null;
        }
        autoStart = false;
        if (autoCraftingQueue != null && !autoCraftingQueue.isEmpty())
            CraftConfirmMenu.openWithCraftingList(getActionHost(), (ServerPlayer) getPlayer(), getLocator(), autoCraftingQueue);
        else host.returnToMainMenu(getPlayer(), (CraftConfirmMenu) (Object) this);
    }

    @Inject(method = "goBack", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$backNative(CallbackInfo ci) {
        if (isClientSide() || hk3gtl$exactPlan == null && hk3gtl$parentPlan == null) return;
        ci.cancel();
        AEKey target = hk3gtl$exactPlan != null ? hk3gtl$exactPlan.target() : hk3gtl$parentPlan.target();
        BigInteger requested = hk3gtl$exactPlan != null ? hk3gtl$exactPlan.amount() : hk3gtl$parentPlan.amount();
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
        if (isClientSide() || hk3gtl$exactPlan == null && hk3gtl$parentPlan == null) return;
        ci.cancel();
        if (hk3gtl$exactPlan != null) hk3gtl$planNexus(hk3gtl$exactPlan.target(), hk3gtl$exactPlan.amount());
        else hk3gtl$planParent(hk3gtl$parentPlan.target(), hk3gtl$parentPlan.amount());
    }

    @Inject(method = "removed", at = @At("HEAD"), remap = true)
    private void hk3gtl$closeNativePlan(net.minecraft.world.entity.player.Player player, CallbackInfo ci) {
        if (hk3gtl$parentPlan != null) hk3gtl$parentPlan.cancel();
        hk3gtl$parentPlan = null;
        hk3gtl$exactPlan = null;
    }
}
