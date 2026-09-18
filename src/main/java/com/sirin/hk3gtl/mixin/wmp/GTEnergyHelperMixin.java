package com.sirin.hk3gtl.mixin.wmp;

import com.sirin.hk3gtl.common.compat.wmp.Hk3WmpCircuitCompat;
import com.wmp.compat.GTEnergyHelper;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;


@Mixin(value = GTEnergyHelper.class, remap = false)
public abstract class GTEnergyHelperMixin {

    @Inject(method = "isCircuit", at = @At("RETURN"), cancellable = true, remap = false)
    private static void hk3gtl$recognizeCircuit(ItemStack stack, CallbackInfoReturnable<Boolean> cir) {
        if (!cir.getReturnValue() && Hk3WmpCircuitCompat.isHk3Circuit(stack)) {
            cir.setReturnValue(true);
        }
    }

    @Inject(method = "getCircuitVoltageTier", at = @At("RETURN"), cancellable = true, remap = false)
    private static void hk3gtl$recognizeTier(ItemStack stack, CallbackInfoReturnable<Integer> cir) {
        int tier = Hk3WmpCircuitCompat.getTier(stack);
        if (tier >= 0) cir.setReturnValue(tier);
    }
}
