package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 【文件职责】增强版IV多任务执行器的工业降效，只拦截扣电与工时推进前的advance。
 * 【变更记录 #1】2026-11-04 21:03:18（第1次备注 · 内测5修订200）
 * 删除：无。新增：独立IV执行器调用共用工业守卫，异常暂停当前推进。
 * 修改：不取消serverTick，不动队列维护、已完成产物交付、取消退款、能源分配和并行参数。
 * 用途：IV不经过基类工作或tick方法也受既有分段约束；同刻判定纯读，不累积减益、不预扣能源。
 */
@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.common.recipe.iv.IvRecipeLogic", remap = false)
public abstract class EnhancedIndustrialGazeMixin {
    @Inject(method = "advance(Ljava/util/List;Lcom/gtl/enhancedcore/common/machine/TieredParallelMachine;)V",
            at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$guardIndustrialAdvance(CallbackInfo callback) {
        try {
            if (Hk3RecipeEnvironment.throttlesByGaze(((RecipeLogic) (Object) this).getMachine()))
                callback.cancel();
        } catch (RuntimeException unavailable) {
            callback.cancel();
        }
    }
}
