package com.sirin.hk3gtl.mixin.gtlcore;

import com.sirin.hk3gtl.common.multiblock.loading.Hk3NativeWonderCheck;
import net.minecraft.core.BlockPos;
import org.gtlcore.gtlcore.api.pattern.PatternMatchLayout;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = PatternMatchLayout.Traversal.class, remap = false)
public abstract class Hk3NativeWonderTraversalMixin {
    @Inject(method = "slice", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$batchSlice(int aisle, CallbackInfoReturnable<PatternMatchLayout.Slice> callback) {
        var check = Hk3NativeWonderCheck.current();
        if (check != null) callback.setReturnValue(check.slice());
    }

    @Inject(method = "position", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$batchPosition(int x, int y, int z, CallbackInfoReturnable<BlockPos> callback) {
        var check = Hk3NativeWonderCheck.current();
        if (check != null) callback.setReturnValue(check.position(x, y, z));
    }
}
