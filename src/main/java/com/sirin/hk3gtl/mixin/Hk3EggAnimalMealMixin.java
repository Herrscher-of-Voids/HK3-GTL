package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(Animal.class)
/** 【变更记录 #1】2026-10-01 06:23:20（修订128）：删除无；新增服务端真实事件旁注；修改无；用途：原条件、原世界结果不变，只授个人可选收藏。 */
public abstract class Hk3EggAnimalMealMixin {
    @Unique private int hk3gtl$age,hk3gtl$love;
    @Inject(method="mobInteract",at=@At("HEAD"))private void hk3gtl$before(Player p,InteractionHand hand,CallbackInfoReturnable<InteractionResult> ci){var a=(Animal)(Object)this;hk3gtl$age=a.getAge();hk3gtl$love=a.getInLoveTime();}
    @Inject(method="mobInteract",at=@At("RETURN"))private void hk3gtl$after(Player p,InteractionHand hand,CallbackInfoReturnable<InteractionResult> ci){var a=(Animal)(Object)this;if(p instanceof ServerPlayer s&&ci.getReturnValue().consumesAction()&&(a.getInLoveTime()>hk3gtl$love||hk3gtl$age<0&&a.getAge()>hk3gtl$age))com.sirin.hk3gtl.common.easter.Hk3EggPersonalScenes.farming(s,"feed");}
}
