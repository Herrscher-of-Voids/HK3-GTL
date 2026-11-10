package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import java.util.Collection;

/**
 * 【文件职责】仅为紧凑巨构提供完整包围盒通知及每区块一个索引代表点。
 * 【变更记录 #1】2026-10-26 19:36:08（第1次备注 · 内测5修订177）
 * - 删除：无；新增：巨构边界命中和区块映射入口；修改：普通GT结构完全沿用原方法。
 * - 用途：空气内放入方块也会使结构失效，同时避免保存数千万个空气坐标。
 */
@Mixin(value = MultiblockState.class, remap = false)
public abstract class Hk3LargeStructureStateMixin {
    @Inject(method = "isPosInCache", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$contains(BlockPos pos, CallbackInfoReturnable<Boolean> callback) {
        var state = (MultiblockState) (Object) this;
        Hk3LargeStructurePattern.Bounds bounds = state.getMatchContext().get(Hk3LargeStructurePattern.BOUNDS_KEY);
        if (bounds != null) callback.setReturnValue(bounds.contains(pos));
    }

    @Inject(method = "getCache", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$chunkIndex(CallbackInfoReturnable<Collection<BlockPos>> callback) {
        var state = (MultiblockState) (Object) this;
        Hk3LargeStructurePattern.Bounds bounds = state.getMatchContext().get(Hk3LargeStructurePattern.BOUNDS_KEY);
        if (bounds != null) callback.setReturnValue(bounds.chunkRepresentatives());
    }
}
