package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(IronGolem.class)
/** 【变更记录 #1】2026-10-01 05:28:18（修订128）：删除无；新增铁傀儡真实生命回复的本人夜间修复回执；修改无；用途：只读真实事件，保留取消结果，不授正式资格。 */
public abstract class Hk3EggGolemMixin {
    @Unique private float hk3gtl$health;
    @Inject(method="mobInteract",at=@At("HEAD"))
    private void hk3gtl$before(Player player,InteractionHand hand,CallbackInfoReturnable<InteractionResult> cir){hk3gtl$health=((IronGolem)(Object)this).getHealth();}
    @Inject(method="mobInteract",at=@At("RETURN"))
    private void hk3gtl$after(Player player,InteractionHand hand,CallbackInfoReturnable<InteractionResult> cir){
        if(player instanceof ServerPlayer p&&p.level().isNight()&&cir.getReturnValue().consumesAction()&&((IronGolem)(Object)this).getHealth()>hk3gtl$health)com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p).putLong("golemRepairedAt",p.server.overworld().getGameTime());
    }
}
