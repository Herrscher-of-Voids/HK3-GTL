package com.sirin.hk3gtl.common.network;

import com.sirin.hk3gtl.client.ae.Hk3ExactAmountScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.network.NetworkEvent;

import java.util.Objects;
import java.util.UUID;
import java.util.function.Supplier;

/** 订单身份只来自服务端，并按当前容器编号隔离状态响应。 */
public record Hk3ExactOrderStatusPacket(int menuId, UUID orderId, String text) {
    public Hk3ExactOrderStatusPacket {
        Objects.requireNonNull(text);
        if (menuId < 0 || text.length() > 8192) throw new IllegalArgumentException("订单状态包越界");
    }

    public static void encode(Hk3ExactOrderStatusPacket packet, FriendlyByteBuf buffer) {
        buffer.writeVarInt(packet.menuId);
        buffer.writeBoolean(packet.orderId != null);
        if (packet.orderId != null) buffer.writeUUID(packet.orderId);
        buffer.writeUtf(packet.text, 8192);
    }

    public static Hk3ExactOrderStatusPacket decode(FriendlyByteBuf buffer) {
        return new Hk3ExactOrderStatusPacket(buffer.readVarInt(),
                buffer.readBoolean() ? buffer.readUUID() : null, buffer.readUtf(8192));
    }

    public static void handle(Hk3ExactOrderStatusPacket packet, Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        if (context.getDirection().getReceptionSide().isClient() && ModList.get().isLoaded("ae2")) {
            context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                    () -> () -> Hk3ExactAmountScreen.receiveStatus(packet.menuId, packet.orderId, packet.text)));
        }
        context.setPacketHandled(true);
    }
}
