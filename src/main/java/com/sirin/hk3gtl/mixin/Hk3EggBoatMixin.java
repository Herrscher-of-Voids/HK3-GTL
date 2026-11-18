package com.sirin.hk3gtl.mixin;

import com.sirin.hk3gtl.common.easter.Hk3EggNativeMachineScenes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BoatItem;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** 原版放船只观察addFreshEntity真实结果，取消生成不能借成功交互结果领收藏。 */
@Mixin(BoatItem.class)
public abstract class Hk3EggBoatMixin {
    @Redirect(method = "use", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/level/Level;addFreshEntity(Lnet/minecraft/world/entity/Entity;)Z"))
    private boolean hk3gtl$spawn(Level level, Entity entity, Level useLevel, Player player, InteractionHand hand) {
        boolean spawned = level.addFreshEntity(entity);
        if (player instanceof ServerPlayer serverPlayer) Hk3EggNativeMachineScenes.boatSpawned(serverPlayer, entity, spawned);
        return spawned;
    }
}
