package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiController;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3NativeWonderCheck;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3NativeWonderPattern;
import it.unimi.dsi.fastutil.longs.LongSet;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(targets = "org.gtlcore.gtlcore.api.pattern.PatternRetryBounds", remap = false)
public abstract class Hk3NativeWonderRetryBoundsMixin {
    @Inject(method = "create", at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$fullBounds(IMultiController controller, BlockPattern pattern,
            CallbackInfoReturnable<BoundingBox> callback) {
        if (pattern instanceof Hk3NativeWonderPattern wonder)
            callback.setReturnValue(Hk3NativeWonderCheck.bounds(controller, wonder));
    }

    @Inject(method = "fixedPositions", at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$useBounds(IMultiController controller, BlockPattern pattern,
            CallbackInfoReturnable<LongSet> callback) {
        if (pattern instanceof Hk3NativeWonderPattern) callback.setReturnValue(null);
    }
}
