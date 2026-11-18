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
    public ModWelcomeS2CPacket {
        if (modVersion.length() > 128 || statusLines.size() > 64 || statusLines.stream().anyMatch(s -> s.length() > 1024))
            throw new IllegalArgumentException("更新摘要超出边界");
        statusLines = List.copyOf(statusLines);
    }

    public static void encode(ModWelcomeS2CPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.modVersion, 128);
        buf.writeVarInt(pkt.statusLines.size());
        for (String line : pkt.statusLines) {
            buf.writeUtf(line, 1024);
        }
    }

    public static ModWelcomeS2CPacket decode(FriendlyByteBuf buf) {
        String version = buf.readUtf(128);
        int n = buf.readVarInt();
        if (n < 0 || n > 64) throw new IllegalArgumentException("更新摘要条数无效");
        List<String> lines = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            lines.add(buf.readUtf(1024));
        }
        return new ModWelcomeS2CPacket(version, lines);
    }

    public static void handle(ModWelcomeS2CPacket pkt, Supplier<NetworkEvent.Context> ctxSupplier) {
        NetworkEvent.Context ctx = ctxSupplier.get();
        net.minecraft.network.Connection connection = ctx.getNetworkManager();
        ctx.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                Hk3ModWelcomeScreen.open(pkt.modVersion(), pkt.statusLines(), connection)));
        ctx.setPacketHandled(true);
    }
}
