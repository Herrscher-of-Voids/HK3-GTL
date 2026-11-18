package com.sirin.hk3gtl.client.campus;

import com.mojang.blaze3d.systems.RenderSystem;
import com.sirin.hk3gtl.common.campus.Hk3CampusMarkerBeamPacket;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BeaconRenderer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;


@Mod.EventBusSubscriber(modid = "hk3gtl", value = Dist.CLIENT)
public final class Hk3CampusMarkerBeamRenderer {
    private static final int HEIGHT = 1024;
    private static final float[] RED = {1f, 0f, 0f};
    private static Hk3CampusMarkerBeamPacket target;

    private Hk3CampusMarkerBeamRenderer() {}

    public static void accept(Hk3CampusMarkerBeamPacket packet) {
        target = packet.marker() == null ? null : packet;
    }

    public static float depthFar() {
        if (target == null) return 0;
        var marker = target.marker();
        var camera = Minecraft.getInstance().gameRenderer.getMainCamera().getPosition();
        return (float) Math.sqrt(Math.max(camera.distanceToSqr(marker.getX() + .5, marker.getY(), marker.getZ() + .5),
                camera.distanceToSqr(marker.getX() + .5, marker.getY() + HEIGHT, marker.getZ() + .5))) + 64f;
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END || target == null) return;
        var mc = Minecraft.getInstance();
        if (mc.level == null || !target.dimension().equals(mc.level.dimension().location())) {
            target = null;
            return;
        }
        var position = mc.player.blockPosition();
        if (position.getX() < target.minX() || position.getX() > target.maxX()
                || position.getZ() < target.minZ() || position.getZ() > target.maxZ()) target = null;
    }

    @SubscribeEvent
    public static void logout(ClientPlayerNetworkEvent.LoggingOut event) { target = null; }

    @SubscribeEvent
    public static void render(RenderLevelStageEvent event) {
        if (event.getStage() != RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS || target == null) return;
        var mc = Minecraft.getInstance();
        var camera = event.getCamera().getPosition();
        var marker = target.marker();
        var pose = event.getPoseStack();
        var buffers = mc.renderBuffers().bufferSource();
        float fogStart = RenderSystem.getShaderFogStart(), fogEnd = RenderSystem.getShaderFogEnd();
        float distance = depthFar();
        RenderSystem.setShaderFogStart(distance);
        RenderSystem.setShaderFogEnd(distance + 1);
        pose.pushPose();
        pose.translate(marker.getX() - camera.x, marker.getY() - camera.y, marker.getZ() - camera.z);
        BeaconRenderer.renderBeaconBeam(pose, buffers, BeaconRenderer.BEAM_LOCATION, event.getPartialTick(), 1f,
                mc.level.getGameTime(), 0, HEIGHT, RED, .35f, .5f);
        buffers.endBatch(RenderType.beaconBeam(BeaconRenderer.BEAM_LOCATION, false));
        buffers.endBatch(RenderType.beaconBeam(BeaconRenderer.BEAM_LOCATION, true));
        pose.popPose();
        RenderSystem.setShaderFogStart(fogStart);
        RenderSystem.setShaderFogEnd(fogEnd);
    }
}
