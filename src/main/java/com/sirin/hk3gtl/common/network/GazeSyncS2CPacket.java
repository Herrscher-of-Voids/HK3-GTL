package com.sirin.hk3gtl.common.network;

import com.sirin.hk3gtl.client.gaze.Hk3ClientGazeState;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;


public record GazeSyncS2CPacket(int gaze, int gazeMax, boolean bufferActive) {

    public static void encode(GazeSyncS2CPacket pkt, FriendlyByteBuf buf) {
        buf.writeVarInt(pkt.gaze);
        buf.writeVarInt(pkt.gazeMax);
        buf.writeBoolean(pkt.bufferActive);
    }

    public static GazeSyncS2CPacket decode(FriendlyByteBuf buf) {
        return new GazeSyncS2CPacket(buf.readVarInt(), buf.readVarInt(), buf.readBoolean());
    }

    public static void handle(GazeSyncS2CPacket pkt, Supplier<NetworkEvent.Context> ctxSupplier) {
        NetworkEvent.Context ctx = ctxSupplier.get();
        // 仅在客户端物理端应用，服务端环境不加载客户端类，避免 ClassNotFound。
        ctx.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                Hk3ClientGazeState.update(pkt.gaze(), pkt.gazeMax(), pkt.bufferActive())));
        ctx.setPacketHandled(true);
    }
}
