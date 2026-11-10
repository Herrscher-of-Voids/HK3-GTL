package com.sirin.hk3gtl.mixin;
import net.minecraft.world.item.HangingEntityItem;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.decoration.Painting;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(HangingEntityItem.class)
/** 【变更记录 #1】2026-10-01 06:23:20（修订128）：删除无；新增服务端真实事件旁注；修改无；用途：原条件、原世界结果不变，只授个人可选收藏。 */
public abstract class Hk3EggPaintingMixin {
    @Redirect(method="useOn",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/Level;addFreshEntity(Lnet/minecraft/world/entity/Entity;)Z"))
    private boolean hk3gtl$placed(Level level,Entity entity,UseOnContext context){boolean added=level.addFreshEntity(entity);if(added&&entity instanceof Painting painting&&context.getPlayer() instanceof ServerPlayer p)com.sirin.hk3gtl.common.easter.Hk3EggPaintingScenes.placed(p,painting);return added;}
}
