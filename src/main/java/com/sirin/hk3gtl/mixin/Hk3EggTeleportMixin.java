package com.sirin.hk3gtl.mixin;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(ServerPlayer.class)
/** 【变更记录 #1】2026-10-01 06:19:47（修订128）：删除无；新增真实操作及连续状态旁注；修改无；用途：只读已加载世界与本人回执，不改游戏结果、不授研究资格。 */
public abstract class Hk3EggTeleportMixin {
    @Inject(method="teleportTo(Lnet/minecraft/server/level/ServerLevel;DDDFF)V",at=@At("RETURN"))private void hk3gtl$teleported(ServerLevel level,double x,double y,double z,float yaw,float pitch,CallbackInfo ci){com.sirin.hk3gtl.common.easter.Hk3EggPersonalScenes.teleported((ServerPlayer)(Object)this);}
}
