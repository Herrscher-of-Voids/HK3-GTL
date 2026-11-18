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
 
public abstract class Hk3EggAnimalMealMixin {
    @Unique private int hk3gtl$age,hk3gtl$love;
    @Inject(method="mobInteract",at=@At("HEAD"))private void hk3gtl$before(Player p,InteractionHand hand,CallbackInfoReturnable<InteractionResult> ci){var a=(Animal)(Object)this;hk3gtl$age=a.getAge();hk3gtl$love=a.getInLoveTime();}
    @Inject(method="mobInteract",at=@At("RETURN"))private void hk3gtl$after(Player p,InteractionHand hand,CallbackInfoReturnable<InteractionResult> ci){var a=(Animal)(Object)this;if(p instanceof ServerPlayer s&&ci.getReturnValue().consumesAction()&&(a.getInLoveTime()>hk3gtl$love||hk3gtl$age<0&&a.getAge()>hk3gtl$age))com.sirin.hk3gtl.common.easter.Hk3EggPersonalScenes.farming(s,"feed");}
}
