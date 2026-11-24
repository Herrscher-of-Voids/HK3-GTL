package com.sirin.hk3gtl.mixin.ae;

import appeng.api.config.Actionable;
import appeng.api.networking.IGrid;
import appeng.api.networking.crafting.ICraftingCPU;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.ICraftingRequester;
import appeng.api.networking.crafting.ICraftingSubmitResult;
import appeng.api.networking.crafting.ICraftingWatcherNode;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.crafting.execution.CraftingSubmitResult;
import appeng.me.service.CraftingService;
import appeng.me.helpers.InterestManager;
import appeng.me.helpers.StackWatcher;
import com.google.common.collect.ImmutableSet;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import com.sirin.hk3gtl.common.config.Hk3AeSettings;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuTracker;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativePlan;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.math.BigInteger;
import java.util.HashSet;
import java.util.Set;

@Mixin(value = CraftingService.class, remap = false, priority = 1300)
public abstract class Hk3NexusCraftingServiceMixin {
    @Shadow @Final private IGrid grid;
    @Shadow @Final private InterestManager<StackWatcher<ICraftingWatcherNode>> interestManager;
    @Unique private Set<AEKey> hk3gtl$waiting = Set.of();

    @Inject(method = "onServerEndTick", at = @At("RETURN"))
    private void hk3gtl$notifyNexusRequests(CallbackInfo ci) {
        var runtimes = Hk3NexusCrafting.forGrid(grid);
        if (runtimes.isEmpty() && hk3gtl$waiting.isEmpty()) return;
        Set<AEKey> current = new HashSet<>();
        runtimes.forEach(runtime -> runtime.collectWaitingKeys(current));
        if (hk3gtl$waiting.equals(current)) return;
        Set<AEKey> changed = new HashSet<>(current);
        changed.addAll(hk3gtl$waiting);
        changed.removeIf(key -> current.contains(key) == hk3gtl$waiting.contains(key));
        hk3gtl$waiting = current;
        for (AEKey key : changed) {
            for (var watcher : interestManager.get(key)) watcher.getHost().onRequestChange(key);
            for (var watcher : interestManager.getAllStacksWatchers()) watcher.getHost().onRequestChange(key);
        }
    }

    @ModifyExpressionValue(method = "getCpus", at = @At(value = "INVOKE",
            target = "Lcom/google/common/collect/ImmutableSet$Builder;build()Lcom/google/common/collect/ImmutableSet;"))
    private ImmutableSet<ICraftingCPU> hk3gtl$nexusCpus(ImmutableSet<ICraftingCPU> original) {
        var runtimes = Hk3NexusCrafting.forGrid(grid);
        if (runtimes.isEmpty()) return original;
        ImmutableSet.Builder<ICraftingCPU> cpus = ImmutableSet.builder();
        cpus.addAll(original);
        runtimes.forEach(runtime -> cpus.addAll(runtime.cpus()));
        return cpus.build();
    }

    @Inject(method = "submitJob", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$submitNexus(ICraftingPlan plan, ICraftingRequester requester, ICraftingCPU cpu,
            boolean prioritizePower, IActionSource source, CallbackInfoReturnable<ICraftingSubmitResult> ci) {
        if (!(cpu instanceof Hk3NexusCrafting.NexusCpu) && !(plan instanceof Hk3NexusNativePlan)
                && Hk3ExactCpuTracker.currentSubmission() == null) return;
        if (plan instanceof Hk3NexusNativePlan exact) {
            var host = exact.host();
            if (exact.grid() != grid || !host.isOn(grid)) ci.setReturnValue(CraftingSubmitResult.CPU_OFFLINE);
            else if (cpu == null || cpu == host.availableCpu()) ci.setReturnValue(host.submitNative(plan, requester, source));
            else ci.setReturnValue(cpu.isBusy() ? CraftingSubmitResult.CPU_BUSY : CraftingSubmitResult.NO_CPU_FOUND);
        } else if (cpu instanceof Hk3NexusCrafting.NexusCpu selected) {
            ci.setReturnValue(!selected.host().isOn(grid) ? CraftingSubmitResult.CPU_OFFLINE : selected.isBusy()
                    ? CraftingSubmitResult.CPU_BUSY : selected.host().submitNative(plan, requester, source));
        } else if (cpu == null && Hk3ExactCpuTracker.currentSubmission() != null) {
            var host = Hk3NexusCrafting.firstOn(grid);
            if (host == null) return;
            var submitted = host.submitNative(plan, requester, source);
            if (submitted != CraftingSubmitResult.INCOMPLETE_PLAN) ci.setReturnValue(submitted);
        }
    }

    @ModifyReturnValue(method = "submitJob", at = @At("RETURN"))
    private ICraftingSubmitResult hk3gtl$tryNexusCpu(ICraftingSubmitResult result, ICraftingPlan plan,
            ICraftingRequester requester, ICraftingCPU cpu, boolean prioritizePower, IActionSource source) {
        if (cpu != null || result != CraftingSubmitResult.NO_CPU_FOUND || Hk3AeSettings.nexusPlannerEnabled()) return result;
        var host = Hk3NexusCrafting.firstOn(grid);
        return host == null ? result : host.submitNative(plan, requester, source);
    }

    @ModifyVariable(method = "insertIntoCpus", at = @At(value = "STORE", ordinal = 0), ordinal = 1)
    private long hk3gtl$nexusReturn(long inserted, AEKey key, long amount, Actionable mode) {
        for (var runtime : Hk3NexusCrafting.forGrid(grid)) inserted += runtime.accept(key, amount - inserted, mode);
        return inserted;
    }

    @ModifyReturnValue(method = "isRequesting", at = @At("RETURN"))
    private boolean hk3gtl$nexusRequest(boolean requesting, AEKey key) {
        return requesting || Hk3NexusCrafting.forGrid(grid).stream().anyMatch(runtime -> runtime.waiting(key).signum() > 0);
    }

    @ModifyVariable(method = "getRequestedAmount", at = @At(value = "STORE", ordinal = 0), ordinal = 0)
    private long hk3gtl$nexusRequestedAmount(long requested, AEKey key) {
        BigInteger count = BigInteger.valueOf(requested);
        for (var runtime : Hk3NexusCrafting.forGrid(grid)) count = count.add(runtime.waiting(key));
        return count.min(BigInteger.valueOf(Long.MAX_VALUE)).longValue();
    }

    @ModifyReturnValue(method = "isRequestingAny", at = @At("RETURN"))
    private boolean hk3gtl$nexusRequests(boolean requesting) {
        return requesting || Hk3NexusCrafting.forGrid(grid).stream().anyMatch(Hk3NexusCrafting::requestingAny);
    }

    @ModifyReturnValue(method = "hasCpu", at = @At("RETURN"))
    private boolean hk3gtl$hasNexus(boolean present, ICraftingCPU cpu) {
        return present || cpu instanceof Hk3NexusCrafting.NexusCpu nexus && Hk3NexusCrafting.forGrid(grid).contains(nexus.host());
    }
}
