package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.IGrid;
import appeng.api.networking.crafting.CalculationStrategy;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.ICraftingSimulationRequester;
import appeng.api.stacks.AEKey;
import appeng.me.service.CraftingService;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.Hk3AePlanningService;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;

// Mixin 0.8.5 对同一 HEAD 按优先级从低到高插入回调，先于 GTLCore 的 1000 执行。
@Mixin(value = CraftingService.class, remap = false, priority = 900)
public abstract class Hk3AePlanningMixin {
    @Shadow @Final private IGrid grid;

    @Inject(method = "beginCraftingCalculation", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$planOnNexus(Level level, ICraftingSimulationRequester requester, AEKey target, long amount,
            CalculationStrategy strategy, CallbackInfoReturnable<Future<ICraftingPlan>> ci) {
        var server = level.getServer();
        if (server == null) return;
        if (!server.isSameThread()) {
            ci.setReturnValue(server.submit(() -> grid.getCraftingService().beginCraftingCalculation(level, requester, target, amount, strategy)).join());
            return;
        }
        var host = Hk3NexusCrafting.plannerOn(grid);
        if (host != null) ci.setReturnValue(host.calculate(target, BigInteger.valueOf(amount), requester.getActionSource(), strategy));
    }

    @WrapOperation(method = "beginCraftingCalculation(Lnet/minecraft/world/level/Level;Lappeng/api/networking/crafting/ICraftingSimulationRequester;Lappeng/api/stacks/AEKey;JLappeng/api/networking/crafting/CalculationStrategy;)Ljava/util/concurrent/Future;",
            at = @At(value = "INVOKE", target = "Ljava/util/concurrent/ExecutorService;submit(Ljava/util/concurrent/Callable;)Ljava/util/concurrent/Future;"),
            require = 1, expect = 1)
    private <T> Future<T> hk3gtl$boundedPlanning(ExecutorService executor, Callable<T> calculation,
                                               Operation<Future<T>> original, Level level) {
        var server = level.getServer();
        return server == null ? original.call(executor, calculation) : Hk3AePlanningService.submit(server, calculation);
    }
}
