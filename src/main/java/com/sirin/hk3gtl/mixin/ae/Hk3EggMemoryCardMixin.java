package com.sirin.hk3gtl.mixin.ae;
import appeng.items.tools.MemoryCardItem;
import appeng.api.implementations.items.MemoryCardMessages;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=MemoryCardItem.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:03:54（修订128）：删除无；新增当前AE成功回调旁注；修改无；用途：已审核原条件，不干预AE权限和生产。 */
public abstract class Hk3EggMemoryCardMixin {
    @Inject(method="notifyUser",at=@At("RETURN"))
    private void hk3gtl$settings(Player player,MemoryCardMessages message,CallbackInfo ci){if(player instanceof ServerPlayer p)com.sirin.hk3gtl.common.easter.Hk3EggAeDevices.memory(p,message);}
}
