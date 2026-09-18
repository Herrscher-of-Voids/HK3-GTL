package com.sirin.hk3gtl.common.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;


public record ClearParticlesS2CPacket() {

    public static void encode(ClearParticlesS2CPacket pkt, FriendlyByteBuf buf) {
        // 无字段：本包仅作为“立即清除粒子”的信号
    }

    public static ClearParticlesS2CPacket decode(FriendlyByteBuf buf) {
        return new ClearParticlesS2CPacket();
    }

    public static void handle(ClearParticlesS2CPacket pkt, Supplier<NetworkEvent.Context> ctxSupplier) {
        NetworkEvent.Context ctx = ctxSupplier.get();
        // 仅客户端物理端执行，服务端不加载客户端类，避免 ClassNotFound。
        ctx.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> ClientParticleClearHandler::clear));
        ctx.setPacketHandled(true);
    }
}
