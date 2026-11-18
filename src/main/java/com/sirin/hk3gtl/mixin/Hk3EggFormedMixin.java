package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=MultiblockControllerMachine.class,remap=false)

public abstract class Hk3EggFormedMixin {
    @Inject(method="onStructureFormed",at=@At("RETURN"))private void hk3gtl$formed(CallbackInfo ci){com.sirin.hk3gtl.common.easter.Hk3EggStructureScenes.formed((MultiblockControllerMachine)(Object)this);}
}
