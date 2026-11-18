package com.sirin.hk3gtl.common.campus;

import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;


public record Hk3CampusMarkerBeamPacket(ResourceLocation dimension, BlockPos marker, int minX, int minZ, int maxX, int maxZ) {
    public static void encode(Hk3CampusMarkerBeamPacket packet, FriendlyByteBuf buffer) {
        buffer.writeResourceLocation(packet.dimension);
        buffer.writeBoolean(packet.marker != null);
        if (packet.marker != null) {
            buffer.writeBlockPos(packet.marker);
            buffer.writeInt(packet.minX);
            buffer.writeInt(packet.minZ);
            buffer.writeInt(packet.maxX);
            buffer.writeInt(packet.maxZ);
        }
    }

    public static Hk3CampusMarkerBeamPacket decode(FriendlyByteBuf buffer) {
        var dimension = buffer.readResourceLocation();
        return buffer.readBoolean()
                ? new Hk3CampusMarkerBeamPacket(dimension, buffer.readBlockPos(), buffer.readInt(), buffer.readInt(), buffer.readInt(), buffer.readInt())
                : new Hk3CampusMarkerBeamPacket(dimension, null, 0, 0, 0, 0);
    }

    public static void handle(Hk3CampusMarkerBeamPacket packet, Supplier<NetworkEvent.Context> supplier) {
        var context = supplier.get();
        context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> com.sirin.hk3gtl.client.campus.Hk3CampusMarkerBeamRenderer.accept(packet)));
        context.setPacketHandled(true);
    }
}
