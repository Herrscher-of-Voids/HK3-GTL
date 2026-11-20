package com.sirin.hk3gtl.mixin.stargate;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.compat.stargate.Hk3StargateQuestEvents;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import net.povstalec.sgjourney.common.sgjourney.StargateConnection;
import net.povstalec.sgjourney.common.sgjourney.Wormhole;
import net.povstalec.sgjourney.common.sgjourney.stargate.Stargate;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = Wormhole.class, remap = false)
public abstract class Hk3WormholeTravelMixin {
    @WrapOperation(method = "wormholeEntity", at = @At(value = "INVOKE", target =
            "Lnet/povstalec/sgjourney/common/sgjourney/stargate/Stargate;receiveTraveler(Lnet/minecraft/server/MinecraftServer;Lnet/povstalec/sgjourney/common/sgjourney/StargateConnection;Lnet/povstalec/sgjourney/common/sgjourney/stargate/Stargate;Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/phys/Vec3;Lnet/minecraft/world/phys/Vec3;Lnet/minecraft/world/phys/Vec3;)Lnet/minecraft/world/entity/Entity;"), require = 0)
    private Entity hk3gtl$trackArrival(Stargate destination, MinecraftServer server, StargateConnection connection,
            Stargate from, Entity traveler, Vec3 position, Vec3 speed, Vec3 relative, Operation<Entity> original) {
        if (!(traveler instanceof ServerPlayer player))
            return original.call(destination, server, connection, from, traveler, position, speed, relative);
        int before = Hk3StargateQuestEvents.travels(player);
        var level = player.serverLevel();
        Vec3 oldPosition = player.position();
        Entity arrived = original.call(destination, server, connection, from, player, position, speed, relative);
        if (arrived instanceof ServerPlayer result && Hk3StargateQuestEvents.travels(result) > before
                && result.level().dimension().equals(destination.getDimension())
                && (result.serverLevel() != level || !result.position().equals(oldPosition)))
            Hk3StargateQuestEvents.completed(result, from, destination);
        return arrived;
    }
}
