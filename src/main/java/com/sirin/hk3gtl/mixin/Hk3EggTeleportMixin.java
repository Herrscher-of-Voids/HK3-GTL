package com.sirin.hk3gtl.mixin;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(ServerPlayer.class)

public abstract class Hk3EggTeleportMixin {
    @Inject(method="teleportTo(Lnet/minecraft/server/level/ServerLevel;DDDFF)V",at=@At("RETURN"))private void hk3gtl$teleported(ServerLevel level,double x,double y,double z,float yaw,float pitch,CallbackInfo ci){com.sirin.hk3gtl.common.easter.Hk3EggPersonalScenes.teleported((ServerPlayer)(Object)this);}
}
