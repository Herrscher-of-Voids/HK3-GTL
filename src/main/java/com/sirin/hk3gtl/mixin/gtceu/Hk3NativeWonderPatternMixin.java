package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3MultiblockLoading;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3NativeWonderCheck;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3NativeWonderPattern;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import org.gtlcore.gtlcore.api.pattern.FixedPatternLayout;
import org.spongepowered.asm.mixin.Dynamic;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = BlockPattern.class, remap = false, priority = 1100)
public abstract class Hk3NativeWonderPatternMixin {
    @Inject(method = "checkPatternAt(Lcom/gregtechceu/gtceu/api/pattern/MultiblockState;Lnet/minecraft/core/BlockPos;Lnet/minecraft/core/Direction;Lnet/minecraft/core/Direction;ZZ)Z",
            at = @At("HEAD"), cancellable = true)
    private void hk3gtl$queueNativeCheck(MultiblockState state, BlockPos center, Direction front, Direction up,
            boolean flip, boolean save, CallbackInfoReturnable<Boolean> callback) {
        if ((Object) this instanceof Hk3NativeWonderPattern && Hk3NativeWonderCheck.current() == null) {
            if (state.world instanceof ServerLevel) Hk3MultiblockLoading.intercept(state);
            callback.setReturnValue(false);
        }
    }

    @Dynamic("GTL原生固定布局匹配入口")
    @WrapOperation(method = "gtlcore$checkPatternAt", at = @At(value = "INVOKE", target =
            "Lorg/gtlcore/gtlcore/api/pattern/WorldPatternMatcher;useFixedLayout(Lcom/gregtechceu/gtceu/api/pattern/MultiblockState;)Z"))
    private boolean hk3gtl$fixedNativeLayout(MultiblockState state, Operation<Boolean> original) {
        return Hk3NativeWonderCheck.current() != null || original.call(state);
    }

    @Dynamic("GTL原生固定布局匹配入口")
    @WrapOperation(method = "gtlcore$checkPatternAt", at = @At(value = "INVOKE", target =
            "Lorg/gtlcore/gtlcore/api/pattern/FixedPatternLayout;match([IILorg/gtlcore/gtlcore/api/pattern/FixedPatternLayout$SliceMatcher;)Z"))
    private boolean hk3gtl$matchBatches(int[] repetitions, int start,
            FixedPatternLayout.SliceMatcher matcher, Operation<Boolean> original) {
        var check = Hk3NativeWonderCheck.current();
        return check == null ? original.call(repetitions, start, matcher)
                : check.match(repetitions, start, matcher, original);
    }
}
