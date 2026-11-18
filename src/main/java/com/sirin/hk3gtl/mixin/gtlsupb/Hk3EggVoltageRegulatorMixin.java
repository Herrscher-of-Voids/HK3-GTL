package com.sirin.hk3gtl.mixin.gtlsupb;

import com.gtlsupb.gtlsupb.common.machine.multiblock.UniversalVoltageRegulator;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableItemStackHandler;
import com.sirin.hk3gtl.common.easter.Hk3EggVoltageSettings;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value=UniversalVoltageRegulator.class,remap=false)
public abstract class Hk3EggVoltageRegulatorMixin implements Hk3EggVoltageSettings.Access {
    @Shadow @Final protected NotifiableItemStackHandler circuitInventory;
    @Override public NotifiableItemStackHandler hk3gtl$circuits(){return circuitInventory;}

    @Inject(method="updateVoltageTier",at=@At("RETURN"))
    private void hk3gtl$changed(CallbackInfo callback){
        Hk3EggVoltageSettings.updated((UniversalVoltageRegulator)(Object)this);
    }
}
