package com.sirin.hk3gtl.common.network;



import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.function.Supplier;

/**
 * C2S 网络包：客户端请求服务端同步当前研究状态快照。
 *
 * <h3>职责</h3>
 * 无序列化字段的空包，仅作为触发信号。服务端收到后调用
 * Hk3ResearchManager.syncClientResearchState 将状态推送回客户端。
 *
 * <h3>触发时机</h3>
 * 客户端打开研究矩阵 GUI 时发送，确保 GUI 展示最新状态。
 *
 * <h3>修改指南</h3>
 * 如需携带额外参数（如筛选条件），在此类中添加字段并更新 encode/decode。
 */
public class ResearchStateSyncRequestC2SPacket {

    private static final int REQUEST_COOLDOWN_TICKS = 10;
    private static final ConcurrentMap<UUID, Integer> LAST_ACCEPTED_TICK = new ConcurrentHashMap<>();

    public ResearchStateSyncRequestC2SPacket() {
    }

    /** 编码：空包，无需写入数据 */
    public static void encode(ResearchStateSyncRequestC2SPacket packet, FriendlyByteBuf buf) {
    }

    /** 解码：空包，直接返回新实例 */
    public static ResearchStateSyncRequestC2SPacket decode(FriendlyByteBuf buf) {
        return new ResearchStateSyncRequestC2SPacket();
    }

    /** 处理：在服务端主线程上调用研究管理器同步状态回客户端 */
    public static void handle(ResearchStateSyncRequestC2SPacket packet, Supplier<NetworkEvent.Context> contextSupplier) {
        NetworkEvent.Context context = contextSupplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player == null) return;

            int currentTick = player.server.getTickCount();
            UUID playerId = player.getUUID();
            Integer lastTick = LAST_ACCEPTED_TICK.get(playerId);
            if (lastTick != null && currentTick - lastTick < REQUEST_COOLDOWN_TICKS) return;

            LAST_ACCEPTED_TICK.put(playerId, currentTick);
            Hk3ResearchManager.syncClientResearchState(player);
        });
        context.setPacketHandled(true);
    }

    public static void clearRateLimit(UUID playerId) {
        if (playerId != null) LAST_ACCEPTED_TICK.remove(playerId);
    }
}
