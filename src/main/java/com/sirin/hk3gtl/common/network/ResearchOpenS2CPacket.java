package com.sirin.hk3gtl.common.network;


/**
 * 【文件职责】
 * - 处理 ResearchOpenS2CPacket 网络同步与通信。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
