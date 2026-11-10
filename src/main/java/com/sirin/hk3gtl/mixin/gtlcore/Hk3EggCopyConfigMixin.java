package com.sirin.hk3gtl.mixin.gtlcore;
import org.gtlcore.gtlcore.common.item.ConfigurationCopyBehavior;
import net.minecraft.world.entity.player.Player;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(value=ConfigurationCopyBehavior.class,remap=false)
/** 【变更记录 #1】2026-10-01 12:16:23（修订128）：删除：无；新增/修改：读取复制行为已提交后对应成功消息，保留原消息，失败与同设备粘贴不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggCopyConfigMixin {
    @Redirect(method="onItemUseFirst",at=@At(value="INVOKE",target="Lnet/minecraft/world/entity/player/Player;displayClientMessage(Lnet/minecraft/network/chat/Component;Z)V",remap=true))
    private void hk3gtl$message(Player player,Component message,boolean overlay,ItemStack stack,UseOnContext context){player.displayClientMessage(message,overlay);com.sirin.hk3gtl.common.easter.Hk3EggTools.copyMessage(player,message,context);}
}
