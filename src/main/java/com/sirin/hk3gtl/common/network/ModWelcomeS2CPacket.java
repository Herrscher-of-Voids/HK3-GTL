package com.sirin.hk3gtl.common.network;

import com.sirin.hk3gtl.client.bootstrap.Hk3ModWelcomeScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * 【文件职责】
 * - 服务端进世界时下发模组欢迎/加载状态，客户端弹出介绍界面。
 *
 * 【变更记录】2026-05-19
 * - 新增：内测二进世界自检结果同步包。
 */
/** 【变更记录 #1】2026-10-01 16:11:00（修订133）：删除无限制长度读取；新增64条/每条1024字符边界与不可变快照；修改接收后等待安全阅读时机；用途：完整更新说明生命周期，不传内部变更日志。 */
/** 【变更记录 #2】2026-10-31 15:36:22（第2次备注 · 修订188）：删除无；新增保留网络连接身份；修改客户端排队入口接收包所属连接；用途：断线后延迟执行的旧包不能绑定到新连接。 */
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
