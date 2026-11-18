package com.sirin.hk3gtl.mixin.ae;

import appeng.me.service.CraftingService;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.Hk3AePlanningService;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;

/** 只包裹原生规划提交点，图后端的提前路由和实际机器执行均保留。 */
@Mixin(value = CraftingService.class, remap = false)
public abstract class Hk3AePlanningMixin {
    @WrapOperation(method = "beginCraftingCalculation(Lnet/minecraft/world/level/Level;Lappeng/api/networking/crafting/ICraftingSimulationRequester;Lappeng/api/stacks/AEKey;JLappeng/api/networking/crafting/CalculationStrategy;)Ljava/util/concurrent/Future;",
            at = @At(value = "INVOKE", target = "Ljava/util/concurrent/ExecutorService;submit(Ljava/util/concurrent/Callable;)Ljava/util/concurrent/Future;"),
            require = 1, expect = 1)
    private <T> Future<T> hk3gtl$boundedPlanning(ExecutorService executor, Callable<T> calculation,
                                               Operation<Future<T>> original, Level level) {
        var server = level.getServer();
        return server == null ? original.call(executor, calculation) : Hk3AePlanningService.submit(server, calculation);
    }
}
