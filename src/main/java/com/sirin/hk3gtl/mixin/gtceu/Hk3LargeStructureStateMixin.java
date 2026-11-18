package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import java.util.Collection;

 





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
