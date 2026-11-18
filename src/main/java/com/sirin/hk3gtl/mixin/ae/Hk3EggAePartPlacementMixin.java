package com.sirin.hk3gtl.mixin.ae;
import appeng.parts.AEBasePart;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=AEBasePart.class,remap=false)

public abstract class Hk3EggAePartPlacementMixin {
    @Inject(method="onPlacement",at=@At("RETURN"))private void hk3gtl$clear(Player p,CallbackInfo ci){if(!p.level().isClientSide)com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.cleared((AEBasePart)(Object)this);}
}
