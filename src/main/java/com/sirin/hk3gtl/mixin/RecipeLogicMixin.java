package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.mojang.logging.LogUtils;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.slf4j.Logger;

import java.util.concurrent.atomic.AtomicLong;

 





@Mixin(value = RecipeLogic.class, remap = false)
 
 





 





public class RecipeLogicMixin {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final long HK3GTL$LOG_INTERVAL_NANOS = 10_000_000_000L;
    private static final AtomicLong HK3GTL$LAST_GUARD_LOG_NANOS = new AtomicLong();

    @Inject(method = "setupRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$guardRecipeStart(GTRecipe recipe, CallbackInfo ci) {
        RecipeLogic self = (RecipeLogic) (Object) this;
        MetaMachine machine = self.getMachine();
        if (recipe != null && hk3gtl$blocksResearch(recipe, machine, machine.getLevel())) ci.cancel();
    }

    /**
     * 单一只读工作守卫入口。实际能源结算由HK自有工作票据负责。
     */
    @Inject(method = "handleRecipeWorking", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$applyWorkingGuards(CallbackInfo ci) {
        RecipeLogic self = (RecipeLogic) (Object) this;
        GTRecipe recipe = self.getLastRecipe();
        if (recipe == null) return;

        MetaMachine machine = self.getMachine();
        Level level = machine.getLevel();

        if (hk3gtl$blocksResearch(recipe, machine, level)
                || hk3gtl$throttlesByGaze(recipe, machine, level)) {
            ci.cancel();
        }
    }

    private boolean hk3gtl$blocksResearch(GTRecipe recipe, MetaMachine machine, Level level) {
        try {
            return com.sirin.hk3gtl.common.research.Hk3RecipeAccess.blocks(recipe, machine);
        } catch (Exception exception) {
            hk3gtl$logGuardFailure("research_gate", exception);
            return true;
        }
    }

    private boolean hk3gtl$throttlesByGaze(GTRecipe recipe, MetaMachine machine, Level level) {
        try {
            return com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment.throttlesByGaze(machine);
        } catch (Exception exception) {
            hk3gtl$logGuardFailure("gaze", exception);
            return true;
        }
    }

    private static void hk3gtl$logGuardFailure(String stage, Exception exception) {
        long now = System.nanoTime();
        long previous = HK3GTL$LAST_GUARD_LOG_NANOS.get();
        if ((previous != 0L && now - previous < HK3GTL$LOG_INTERVAL_NANOS)
                || !HK3GTL$LAST_GUARD_LOG_NANOS.compareAndSet(previous, now)) {
            return;
        }
        LOGGER.warn("[HK3GTL] RecipeLogic 守卫异常，已取消当前 tick。stage={}, exceptionType={}, message={}",
                stage, exception.getClass().getName(), exception.getMessage());
    }
}
