package com.sirin.hk3gtl.common.network;

import com.sirin.hk3gtl.client.gaze.Hk3ClientGazeState;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 【文件职责】
 * - 服务端 -> 客户端 注视度同步包：把玩家当前注视度、上限、缓冲状态下发给客户端 HUD。
 *
 * 【变更记录】2026-07-03
 * - 新增：终焉注视度系统可视化 HUD 的数据来源包。
 */
/**
 * 【变更记录 #1】2026-09-30 15:49:23（第1次编号备注 · 内测5修订109）
 * 删除：过期的计算或无运行依据的分支；保留历史备注。
 * 新增／修改：增加服务端个人有效值和在线团队最高值快照，客户端只显示。
 * 用途：统一注视与研究联动，服务端判定；不新增结构或贴图。
 */
public record GazeSyncS2CPacket(int gaze, int gazeMax, boolean bufferActive, int effectiveGaze, int teamGaze) {

    public static void encode(GazeSyncS2CPacket pkt, FriendlyByteBuf buf) {
        buf.writeVarInt(pkt.gaze);
        buf.writeVarInt(pkt.gazeMax);
        buf.writeBoolean(pkt.bufferActive);
        buf.writeVarInt(pkt.effectiveGaze);
        buf.writeVarInt(pkt.teamGaze);
    }

    public static GazeSyncS2CPacket decode(FriendlyByteBuf buf) {
        return new GazeSyncS2CPacket(buf.readVarInt(), buf.readVarInt(), buf.readBoolean(), buf.readVarInt(), buf.readVarInt());
    }

    public static void handle(GazeSyncS2CPacket pkt, Supplier<NetworkEvent.Context> ctxSupplier) {
        NetworkEvent.Context ctx = ctxSupplier.get();
        // 仅在客户端物理端应用，服务端环境不加载客户端类，避免 ClassNotFound。
        ctx.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                Hk3ClientGazeState.update(pkt.gaze(), pkt.gazeMax(), pkt.bufferActive(), pkt.effectiveGaze(), pkt.teamGaze())));
        ctx.setPacketHandled(true);
    }
}
