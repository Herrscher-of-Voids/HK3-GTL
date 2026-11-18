package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(IronGolem.class)

public abstract class Hk3EggGolemMixin {
    @Unique private float hk3gtl$health;
    @Inject(method="mobInteract",at=@At("HEAD"))
    private void hk3gtl$before(Player player,InteractionHand hand,CallbackInfoReturnable<InteractionResult> cir){hk3gtl$health=((IronGolem)(Object)this).getHealth();}
    @Inject(method="mobInteract",at=@At("RETURN"))
    private void hk3gtl$after(Player player,InteractionHand hand,CallbackInfoReturnable<InteractionResult> cir){
        if(player instanceof ServerPlayer p&&p.level().isNight()&&cir.getReturnValue().consumesAction()&&((IronGolem)(Object)this).getHealth()>hk3gtl$health)com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p).putLong("golemRepairedAt",p.server.overworld().getGameTime());
    }
}
