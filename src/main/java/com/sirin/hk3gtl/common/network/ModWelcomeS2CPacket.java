package com.sirin.hk3gtl.common.network;

import com.sirin.hk3gtl.client.bootstrap.Hk3ModWelcomeScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;


public record ModWelcomeS2CPacket(String modVersion, List<String> statusLines) {

    public static void encode(ModWelcomeS2CPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.modVersion);
        buf.writeVarInt(pkt.statusLines.size());
        for (String line : pkt.statusLines) {
            buf.writeUtf(line);
        }
    }

    public static ModWelcomeS2CPacket decode(FriendlyByteBuf buf) {
        String version = buf.readUtf();
        int n = buf.readVarInt();
        List<String> lines = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            lines.add(buf.readUtf());
        }
        return new ModWelcomeS2CPacket(version, lines);
    }

    public static void handle(ModWelcomeS2CPacket pkt, Supplier<NetworkEvent.Context> ctxSupplier) {
        NetworkEvent.Context ctx = ctxSupplier.get();
        ctx.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                Hk3ModWelcomeScreen.open(pkt.modVersion(), pkt.statusLines())));
        ctx.setPacketHandled(true);
    }
}
