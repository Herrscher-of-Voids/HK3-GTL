package com.sirin.hk3gtl.common.network;



import com.sirin.hk3gtl.client.research.Hk3ResearchMatrixScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * S2C：服务端确认研究矩阵交互有效后，通知客户端打开研究 GUI。
 */
public class ResearchOpenS2CPacket {

    public ResearchOpenS2CPacket() {}

    public static void encode(ResearchOpenS2CPacket packet, FriendlyByteBuf buf) {}

    public static ResearchOpenS2CPacket decode(FriendlyByteBuf buf) {
        return new ResearchOpenS2CPacket();
    }

    public static void handle(ResearchOpenS2CPacket packet, Supplier<NetworkEvent.Context> contextSupplier) {
        NetworkEvent.Context context = contextSupplier.get();
        context.enqueueWork(() ->
                DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> Hk3ResearchMatrixScreen.openFromPacket())
        );
        context.setPacketHandled(true);
    }
}
