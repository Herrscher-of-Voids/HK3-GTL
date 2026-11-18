package com.sirin.hk3gtl.common.network;

import com.sirin.hk3gtl.client.ae.Hk3ProbabilityAmountScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.network.NetworkEvent;

import java.util.UUID;
import java.util.function.Supplier;

public record Hk3ProbabilityOrderStatusPacket(int menuId, UUID orderId, int candidateCount,
        int orderCount, boolean previewReady, String text) {
    public static void encode(Hk3ProbabilityOrderStatusPacket packet, FriendlyByteBuf buffer) {
        buffer.writeVarInt(packet.menuId);
        buffer.writeBoolean(packet.orderId != null);
        if (packet.orderId != null) buffer.writeUUID(packet.orderId);
        buffer.writeVarInt(packet.candidateCount);
        buffer.writeVarInt(packet.orderCount);
        buffer.writeBoolean(packet.previewReady);
        buffer.writeUtf(packet.text, 8192);
    }

    public static Hk3ProbabilityOrderStatusPacket decode(FriendlyByteBuf buffer) {
        return new Hk3ProbabilityOrderStatusPacket(buffer.readVarInt(),
                buffer.readBoolean() ? buffer.readUUID() : null, buffer.readVarInt(),
                buffer.readVarInt(), buffer.readBoolean(), buffer.readUtf(8192));
    }

    public static void handle(Hk3ProbabilityOrderStatusPacket packet, Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        if (context.getDirection().getReceptionSide().isClient() && ModList.get().isLoaded("ae2")) {
            context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                    () -> () -> Hk3ProbabilityAmountScreen.receiveStatus(packet)));
        }
        context.setPacketHandled(true);
    }
}
