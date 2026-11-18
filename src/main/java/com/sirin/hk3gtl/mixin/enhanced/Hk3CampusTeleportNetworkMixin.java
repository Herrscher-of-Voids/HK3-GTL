package com.sirin.hk3gtl.mixin.enhanced;

import com.llamalad7.mixinextras.sugar.Local;
import com.gtl.enhancedcore.common.world.campus.CampusPlanAccess;
import com.gtl.enhancedcore.common.world.campus.CampusTeleportNetwork;
import com.gtl.enhancedcore.common.world.plot.PlotChunkGenerator;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.campus.Hk3CampusMarkerBeamPacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.PacketDistributor;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(value = CampusTeleportNetwork.class, remap = false)
public abstract class Hk3CampusTeleportNetworkMixin {
    @Redirect(method = "validateDevice", at = @At(value = "INVOKE",
            target = "Lcom/gtl/enhancedcore/common/world/plot/PlotSettings;isCampus()Z"))
    private static boolean hk3gtl$gridTravel(PlotSettings settings) { return true; }

    @Inject(method = "travel", at = @At("TAIL"))
    private static void hk3gtl$markerBeam(CallbackInfo ci,
            @Local(argsOnly = true) ServerPlayer player,
            @Local PlotChunkGenerator generator, @Local CampusPlanAccess.Target target) {
        var dimension = player.serverLevel().dimension().location();
        Hk3CampusMarkerBeamPacket packet;
        if (target.kind() == CampusPlanAccess.Kind.MACHINE) {
            var plot = target.plot();
            var bounds = target.bounds();
            var marker = new BlockPos(plot.controllerX(), generator.settings().surfaceY() + plot.controllerY(), plot.controllerZ());
            packet = new Hk3CampusMarkerBeamPacket(dimension, marker,
                    Math.min(bounds.minX(), target.arrivalX()) - 16, Math.min(bounds.minZ(), target.arrivalZ()) - 16,
                    Math.max(bounds.maxX(), target.arrivalX()) + 16, Math.max(bounds.maxZ(), target.arrivalZ()) + 16);
        } else {
            packet = new Hk3CampusMarkerBeamPacket(dimension, null, 0, 0, 0, 0);
        }
        Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), packet);
    }
}
