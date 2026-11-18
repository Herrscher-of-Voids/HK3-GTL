package com.sirin.hk3gtl.mixin.ae;
import appeng.items.tools.MemoryCardItem;
import appeng.api.implementations.items.MemoryCardMessages;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=MemoryCardItem.class,remap=false)

public abstract class Hk3EggMemoryCardMixin {
    @Inject(method="notifyUser",at=@At("RETURN"))
    private void hk3gtl$settings(Player player,MemoryCardMessages message,CallbackInfo ci){if(player instanceof ServerPlayer p)com.sirin.hk3gtl.common.easter.Hk3EggAeDevices.memory(p,message);}
}
