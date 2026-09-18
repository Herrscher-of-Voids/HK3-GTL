package com.sirin.hk3gtl.common.network;



import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * C2S 网络包：客户端提交研究请求到服务端。
 *
 * <h3>职责</h3>
 * 玩家在研究矩阵 GUI 中点击"提交研究"按钮时发送，
 * 服务端收到后调用 Hk3ResearchManager.submitResearchById 执行研究逻辑。
 *
 * <h3>序列化字段</h3>
 * <ul>
 *   <li>{@code researchId} - String，研究节点ID（如 "R-AB-001"），通过 writeUtf/readUtf 编解码</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * 如需传递额外参数（如批量提交），在此类中添加字段并更新 encode/decode。
 */
public class ResearchSubmitPacket {

    /** 序列化字段：要提交的研究节点ID */
    private final String researchId;

    public ResearchSubmitPacket(String researchId) {
        this.researchId = researchId;
    }

    /** 编码：写入研究ID字符串 */
    public static void encode(ResearchSubmitPacket packet, FriendlyByteBuf buf) {
        buf.writeUtf(packet.researchId);
    }

    /** 解码：读取研究ID字符串 */
    public static ResearchSubmitPacket decode(FriendlyByteBuf buf) {
        return new ResearchSubmitPacket(buf.readUtf());
    }

    /** 处理：在服务端主线程上执行研究提交（扣除材料、标记完成、同步状态） */
    public static void handle(ResearchSubmitPacket packet, Supplier<NetworkEvent.Context> contextSupplier) {
        NetworkEvent.Context context = contextSupplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null) {
                Hk3ResearchManager.submitResearchById(player, packet.researchId);
            }
        });
        context.setPacketHandled(true);
    }
}
