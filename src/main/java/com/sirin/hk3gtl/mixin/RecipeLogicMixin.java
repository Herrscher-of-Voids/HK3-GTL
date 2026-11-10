package com.sirin.hk3gtl.mixin;

/** 中文说明：该处说明已按当前代码行为整理。*/

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

/**
 * 【变更记录 #1】2026-09-27 23:52:00（内测5修订91）
 * 删除：无功能删除。新增：共用Hk3RecipeAccess研究判定。
 * 修改：原包与增强版使用同一归属和研究查询，保留原有异常限频、注视度和扣费顺序。
 * 用途：避免两套执行路径的研究规则漂移，不增加条件查询副作用。
 */
@Mixin(value = RecipeLogic.class, remap = false)
/** 【变更记录 #2】2026-10-01 06:11:31（修订128）：删除：无；新增/修改：崩坏能真正扣款成功后记录同tick事实；不改变守卫、EU或崩坏能的扣费规则；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/**
 * 【变更记录 #3】2026-10-01 17:41:38（修订139）
 * 删除：handleRecipeWorking HEAD不可逆HW预扣及过早彩蛋回执。
 * 新增：无；修改：保留研究、虚数锚、注视度三项只读守卫，HW由HK自有工作票据结算。
 * 用途：失败或暂停不能白扣HW；第三方非HK机器没有新增能源成本。
 */
/**
 * 【变更记录 #4】2026-10-17 14:44:46（第4次备注 · 内测5修订162）
 * 删除：退役虚数锚的只读调用与异常限频包装分支。
 * 新增：无。修改：保留研究、注视度守卫和共用日志限频。
 * 用途：旧设备不继续限制现役配方；双能源工作票据与现行锚定研究不变。
 */
public class RecipeLogicMixin {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final long HK3GTL$LOG_INTERVAL_NANOS = 10_000_000_000L;
    private static final AtomicLong HK3GTL$LAST_GUARD_LOG_NANOS = new AtomicLong();

    /** 中文说明：该处说明已按当前代码行为整理。*/
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
