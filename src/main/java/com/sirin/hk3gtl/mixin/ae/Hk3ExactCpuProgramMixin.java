package com.sirin.hk3gtl.mixin.ae;

import appeng.api.config.Actionable;
import appeng.api.config.PowerMultiplier;
import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.IGrid;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.ICraftingRequester;
import appeng.api.networking.crafting.ICraftingSubmitResult;
import appeng.api.networking.energy.IEnergyService;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.api.stacks.KeyCounter;
import appeng.crafting.execution.CraftingCpuHelper;
import appeng.crafting.execution.CraftingCpuLogic;
import appeng.crafting.execution.CraftingSubmitResult;
import appeng.crafting.execution.ElapsedTimeTracker;
import appeng.crafting.execution.ExecutingCraftingJob;
import appeng.crafting.inv.ListCraftingInventory;
import appeng.me.cluster.implementations.CraftingCPUCluster;
import appeng.me.service.CraftingService;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuProgram;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactCpuTracker;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactBoundPattern;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactProgramHost;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactProgramPlan;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactScaledPattern;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.gen.Invoker;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.Map;

/** 仅接管带证明的 HK3 程序；普通 AE／GTL 任务保留原执行器。 */
@Mixin(value = CraftingCpuLogic.class, remap = false, priority = 900)
 
public abstract class Hk3ExactCpuProgramMixin implements Hk3ExactProgramHost, Hk3ExactCpuTracker.ProgramAccess {
    @Shadow @Final private CraftingCPUCluster cluster;
    @Shadow @Final private ListCraftingInventory inventory;
    @Shadow private ExecutingCraftingJob job;
    @Shadow public abstract GenericStack getFinalJobOutput();
    @Shadow public abstract ElapsedTimeTracker getElapsedTimeTracker();
    @Shadow public abstract void cancel();
    @Invoker("finishJob") protected abstract void hk3gtl$finish(boolean success);
    @Invoker("postChange") protected abstract void hk3gtl$postChange(AEKey key);
    @Unique private Hk3ExactCpuProgram hk3gtl$program;
    @Unique private Hk3ExactCpuProgram hk3gtl$pendingProgram;
    @Unique private boolean hk3gtl$programFault;
    @Unique private boolean hk3gtl$cancelPending;
    @Unique private ListTag hk3gtl$disputedInputs;

    @Override public boolean hk3gtl$hasProgram() { return hk3gtl$program != null || hk3gtl$programFault; }

    @Override public boolean hk3gtl$recoverableProgram() {
        return !hk3gtl$programFault && !hk3gtl$cancelPending && hk3gtl$disputedInputs == null;
    }

    @Override public long hk3gtl$programProduced(boolean success, long original, AEKey target) {
        if (hk3gtl$programFault || hk3gtl$program == null || job == null || !hk3gtl$waitingEmpty()) return -1;
        long held = inventory.extract(target, Long.MAX_VALUE, Actionable.SIMULATE);
        long net = Math.max(0, held - hk3gtl$program.targetSeed());
        return success && (!hk3gtl$program.cursor().done() || net < original) ? -1 : Math.min(original, net);
    }

    @Inject(method = "trySubmitJob", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$guardProgram(IGrid grid, ICraftingPlan plan, IActionSource source,
            ICraftingRequester requester, CallbackInfoReturnable<ICraftingSubmitResult> ci) {
        hk3gtl$pendingProgram = null;
        if (hk3gtl$hasProgram()) ci.setReturnValue(CraftingSubmitResult.CPU_BUSY);
        else if (plan instanceof Hk3ExactProgramPlan && requester != null)
            ci.setReturnValue(CraftingSubmitResult.INCOMPLETE_PLAN);
        else if (plan instanceof Hk3ExactProgramPlan program) {
            try { hk3gtl$pendingProgram = new Hk3ExactCpuProgram(program); }
            catch (RuntimeException invalid) { ci.setReturnValue(CraftingSubmitResult.INCOMPLETE_PLAN); }
        }
    }

    @Inject(method = "trySubmitJob", at = @At("RETURN"))
    private void hk3gtl$bindProgram(IGrid grid, ICraftingPlan plan, IActionSource source,
            ICraftingRequester requester, CallbackInfoReturnable<ICraftingSubmitResult> ci) {
        if (ci.getReturnValue().successful() && plan instanceof Hk3ExactProgramPlan program) {
            hk3gtl$program = hk3gtl$pendingProgram;
            hk3gtl$programFault = hk3gtl$program == null;
            hk3gtl$cancelPending = false;
            cluster.markDirty();
        }
        hk3gtl$pendingProgram = null;
    }

    @Inject(method = "tickCraftingLogic", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$freezeBrokenProgram(IEnergyService energy, CraftingService service, CallbackInfo ci) {
        if (hk3gtl$programFault) ci.cancel();
        else if (hk3gtl$cancelPending) {
            if (hk3gtl$waitingEmpty()) cancel();
            ci.cancel();
        }
    }

    @Inject(method = "cancel", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$drainBeforeCancel(CallbackInfo ci) {
        if (!hk3gtl$hasProgram() || job == null) return;
        if (hk3gtl$programFault || hk3gtl$disputedInputs != null) {
            ci.cancel();
            return;
        }
        if (!hk3gtl$cancelPending) {
            hk3gtl$cancelPending = true;
            cluster.markDirty();
        }
        if (!hk3gtl$waitingEmpty()) ci.cancel();
    }

    // 守住原生收尾入口，避免依赖 GTL 高优先级合并的私有 tick 方法。
    @Inject(method = "finishJob", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$preventPrematureFinish(boolean success, CallbackInfo ci) {
        if (!success || !hk3gtl$hasProgram()) return;
        GenericStack target = getFinalJobOutput();
        if (target == null || hk3gtl$programProduced(true, target.amount(), target.what()) != target.amount()
                || !((Hk3ExactExecutingJobAccess) (Object) job).hk3gtl$tasks().isEmpty()) ci.cancel();
    }

    @Inject(method = "executeCrafting", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$executeProgram(int maxPatterns, CraftingService service, IEnergyService energy,
            Level level, CallbackInfoReturnable<Integer> ci) {
        if (!hk3gtl$hasProgram()) return;
        ci.setReturnValue(0);
        if (hk3gtl$programFault || hk3gtl$cancelPending || job == null || maxPatterns <= 0 || !hk3gtl$waitingEmpty()) return;
        var cursor = hk3gtl$program.cursor();
        if (cursor.waiting()) cursor.returned();
        var access = (Hk3ExactExecutingJobAccess) (Object) job;
        if (cursor.done()) {
            GenericStack target = getFinalJobOutput();
            if (!access.hk3gtl$tasks().isEmpty() || target == null
                    || hk3gtl$programProduced(true, target.amount(), target.what()) != target.amount()) {
                hk3gtl$programFault = true; cluster.markDirty(); return;
            }
            access.hk3gtl$remainingAmount(0);
            // 成品、种子及副产物仍在真实 CPU 库存内，由原生收尾退回网络。
            hk3gtl$finish(true);
            cluster.updateOutput(null);
            return;
        }
        IPatternDetails pattern = cursor.current();
        IPatternDetails nativePattern = Hk3ExactBoundPattern.original(pattern);
        long operations = Hk3ExactScaledPattern.operations(pattern);
        Object progress = access.hk3gtl$tasks().get(nativePattern);
        if (!(progress instanceof Hk3ExactTaskProgressAccess task) || task.hk3gtl$value() < operations) {
            hk3gtl$programFault = true; cluster.markDirty(); return;
        }
        for (var provider : service.getProviders(nativePattern)) {
            if (provider.isBusy()) continue;
            KeyCounter outputs = new KeyCounter(), containers = new KeyCounter();
            var inputs = CraftingCpuHelper.extractPatternInputs(pattern, inventory, level, outputs, containers);
            if (inputs == null) return;
            boolean pushed = false;
            boolean unknown = false;
            boolean dispatchStarted = false;
            try {
                double cost = CraftingCpuHelper.calculatePatternPower(inputs);
                if (energy.extractAEPower(cost, Actionable.SIMULATE, PowerMultiplier.CONFIG) < cost - 0.01) return;
                ListTag evidence = new ListTag();
                for (int slot = 0; slot < inputs.length; slot++) {
                    for (var input : inputs[slot]) {
                        CompoundTag entry = GenericStack.writeTag(new GenericStack(input.getKey(), input.getLongValue()));
                        entry.putInt("slot", slot); evidence.add(entry);
                    }
                }
                hk3gtl$disputedInputs = evidence;
                cluster.markDirty();
                dispatchStarted = true;
                pushed = provider.pushPattern(Hk3ExactScaledPattern.providerPattern(pattern),
                        Hk3ExactBoundPattern.providerInputs(pattern, inputs));
                if (!pushed) continue;
                // 投料成功后先写等待和游标；后续异常宁可冻结，也不能补发同一批。
                for (var output : outputs) access.hk3gtl$waitingFor().insert(output.getKey(), output.getLongValue(), Actionable.MODULATE);
                for (var output : containers) {
                    access.hk3gtl$waitingFor().insert(output.getKey(), output.getLongValue(), Actionable.MODULATE);
                    ((Hk3ExactTimeTrackerAccess) (Object) getElapsedTimeTracker())
                            .hk3gtl$add(output.getLongValue(), output.getKey().getType());
                }
                task.hk3gtl$value(task.hk3gtl$value() - operations);
                if (task.hk3gtl$value() == 0) access.hk3gtl$tasks().remove(nativePattern);
                cursor.pushed();
                cluster.markDirty();
                for (var output : outputs) hk3gtl$postChange(output.getKey());
                for (var output : containers) hk3gtl$postChange(output.getKey());
                energy.extractAEPower(cost, Actionable.MODULATE, PowerMultiplier.CONFIG);
                hk3gtl$disputedInputs = null;
                ci.setReturnValue(1);
                return;
            } catch (RuntimeException failure) {
                // provider 抛错可能发生在外部已收料之后，不能猜成失败并退回同一份材料。
                unknown = dispatchStarted;
                hk3gtl$programFault = true;
                cluster.markDirty();
                LogUtils.getLogger().error("HK3循环程序投料结果异常，已冻结并保留任务", failure);
                return;
            } finally {
                if (!pushed && !unknown) CraftingCpuHelper.reinjectPatternInputs(inventory, inputs);
                if (!unknown && !pushed) hk3gtl$disputedInputs = null;
            }
        }
    }

    @Inject(method = "insert", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$holdProgramReturn(AEKey key, long amount, Actionable mode,
            CallbackInfoReturnable<Long> ci) {
        if (!hk3gtl$hasProgram()) return;
        ci.setReturnValue(0L);
        if (hk3gtl$programFault || job == null || key == null || amount <= 0) return;
        var access = (Hk3ExactExecutingJobAccess) (Object) job;
        long accepted = access.hk3gtl$waitingFor().extract(key, amount, Actionable.SIMULATE);
        if (accepted <= 0) return;
        if (mode == Actionable.MODULATE) {
            inventory.insert(key, accepted, Actionable.MODULATE);
            access.hk3gtl$waitingFor().extract(key, accepted, Actionable.MODULATE);
            ((Hk3ExactTimeTrackerAccess) (Object) getElapsedTimeTracker()).hk3gtl$decrement(accepted, key.getType());
            hk3gtl$postChange(key);
            cluster.markDirty();
        }
        ci.setReturnValue(accepted);
    }

    @Unique private boolean hk3gtl$waitingEmpty() {
        if (job == null) return true;
        for (var entry : ((Hk3ExactExecutingJobAccess) (Object) job).hk3gtl$waitingFor().list)
            if (entry.getLongValue() > 0) return false;
        return true;
    }

    @Inject(method = "finishJob", at = @At("RETURN"))
    private void hk3gtl$clearProgram(boolean success, CallbackInfo ci) {
        if (job == null && hk3gtl$disputedInputs == null) {
            hk3gtl$program = null;
            hk3gtl$programFault = false;
            hk3gtl$cancelPending = false;
        }
    }

    @Inject(method = "writeToNBT", at = @At("RETURN"))
    private void hk3gtl$saveProgram(CompoundTag tag, CallbackInfo ci) {
        tag.remove(Hk3ExactCpuProgram.NBT);
        tag.putBoolean("hk3ExactProgramRequired", hk3gtl$hasProgram());
        tag.putBoolean("hk3ExactProgramFault", hk3gtl$programFault);
        tag.putBoolean("hk3ExactProgramCancelling", hk3gtl$cancelPending);
        tag.remove("hk3ExactDisputedInputs");
        if (hk3gtl$disputedInputs != null) tag.put("hk3ExactDisputedInputs", hk3gtl$disputedInputs.copy());
        if (hk3gtl$program != null) tag.put(Hk3ExactCpuProgram.NBT, hk3gtl$program.write());
    }

    @Inject(method = "readFromNBT", at = @At("RETURN"))
    private void hk3gtl$loadProgram(CompoundTag tag, CallbackInfo ci) {
        hk3gtl$program = null; hk3gtl$programFault = tag.getBoolean("hk3ExactProgramFault");
        hk3gtl$cancelPending = tag.getBoolean("hk3ExactProgramCancelling");
        hk3gtl$disputedInputs = tag.contains("hk3ExactDisputedInputs", Tag.TAG_LIST)
                ? tag.getList("hk3ExactDisputedInputs", Tag.TAG_COMPOUND).copy() : null;
        if (hk3gtl$disputedInputs != null) hk3gtl$programFault = true;
        if (!tag.getBoolean("hk3ExactProgramRequired")) {
            if (tag.contains(Hk3ExactCpuProgram.NBT) || hk3gtl$cancelPending) hk3gtl$programFault = true;
            return;
        }
        try {
            if (job == null || !tag.contains(Hk3ExactCpuProgram.NBT, Tag.TAG_COMPOUND))
                throw new IllegalArgumentException("CPU程序缺失，不能恢复无序执行");
            Map<IPatternDetails, BigInteger> remaining = new LinkedHashMap<>();
            ((Hk3ExactExecutingJobAccess) (Object) job).hk3gtl$tasks().forEach((pattern, value) -> {
                long count = ((Hk3ExactTaskProgressAccess) value).hk3gtl$value();
                if (count < 0) throw new IllegalArgumentException("CPU样板次数损坏");
                if (count > 0) remaining.put(pattern, BigInteger.valueOf(count));
            });
            hk3gtl$program = Hk3ExactCpuProgram.read(tag.getCompound(Hk3ExactCpuProgram.NBT), cluster.getLevel(),
                    remaining, getFinalJobOutput().amount());
        } catch (RuntimeException failure) {
            hk3gtl$programFault = true;
            LogUtils.getLogger().error("HK3循环程序恢复失败，保留原生库存与任务并冻结", failure);
        }
    }
}
