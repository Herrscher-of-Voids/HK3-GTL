package com.sirin.hk3gtl.mixin.gtlcore;
import org.gtlcore.gtlcore.common.item.ConfigurationCopyBehavior;
import net.minecraft.world.entity.player.Player;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(value=ConfigurationCopyBehavior.class,remap=false)
 
public abstract class Hk3EggCopyConfigMixin {
    @Redirect(method="onItemUseFirst",at=@At(value="INVOKE",target="Lnet/minecraft/world/entity/player/Player;displayClientMessage(Lnet/minecraft/network/chat/Component;Z)V",remap=true))
    private void hk3gtl$message(Player player,Component message,boolean overlay,ItemStack stack,UseOnContext context){player.displayClientMessage(message,overlay);com.sirin.hk3gtl.common.easter.Hk3EggTools.copyMessage(player,message,context);}
}
