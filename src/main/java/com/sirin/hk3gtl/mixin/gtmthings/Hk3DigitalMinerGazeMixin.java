package com.sirin.hk3gtl.mixin.gtmthings;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets = "com.hepdd.gtmthings.common.block.machine.trait.miner.DigitalMinerLogic", remap = false)
public abstract class Hk3DigitalMinerGazeMixin {
    @Unique private long hk3gtl$pausedTicks;

    @Inject(method = "serverTick", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$miningTick(CallbackInfo callback) {
        if (Hk3RecipeEnvironment.throttlesByGaze(((RecipeLogic) (Object) this).getMachine())) {
            hk3gtl$pausedTicks++;
            callback.cancel();
        }
    }

    @Redirect(method = "serverTick", at = @At(value = "INVOKE",
            target = "Lcom/gregtechceu/gtceu/api/machine/MetaMachine;getOffsetTimer()J"), require = 1)
    private long hk3gtl$miningClock(MetaMachine machine) {
        return machine.getOffsetTimer() - hk3gtl$pausedTicks;
    }
}
