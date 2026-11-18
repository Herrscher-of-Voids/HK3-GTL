package com.sirin.hk3gtl.mixin.gtceu;

import com.sirin.hk3gtl.common.multiblock.loading.Hk3PatternLoading;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FluidState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 原始结构谓词直接读取世界时，沿用当前分批核验快照。 */
@Mixin(Level.class)
public abstract class Hk3PatternWorldReadMixin {
    @Inject(method="getBlockState(Lnet/minecraft/core/BlockPos;)Lnet/minecraft/world/level/block/state/BlockState;",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$patternState(BlockPos pos,CallbackInfoReturnable<BlockState> callback) {
        var loading=Hk3PatternLoading.current((Level)(Object)this);
        if(loading!=null)callback.setReturnValue(loading.blockState(pos));
    }

    @Inject(method="getBlockEntity(Lnet/minecraft/core/BlockPos;)Lnet/minecraft/world/level/block/entity/BlockEntity;",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$patternEntity(BlockPos pos,CallbackInfoReturnable<BlockEntity> callback) {
        var loading=Hk3PatternLoading.current((Level)(Object)this);
        if(loading!=null)callback.setReturnValue(loading.blockEntity(pos));
    }

    @Inject(method="getFluidState(Lnet/minecraft/core/BlockPos;)Lnet/minecraft/world/level/material/FluidState;",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$patternFluid(BlockPos pos,CallbackInfoReturnable<FluidState> callback) {
        var loading=Hk3PatternLoading.current((Level)(Object)this);
        if(loading!=null)callback.setReturnValue(loading.blockState(pos).getFluidState());
    }

    @Inject(method="isLoaded(Lnet/minecraft/core/BlockPos;)Z",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$patternLoaded(BlockPos pos,CallbackInfoReturnable<Boolean> callback) {
        var loading=Hk3PatternLoading.current((Level)(Object)this);
        if(loading!=null)callback.setReturnValue(loading.loaded(pos));
    }
}
