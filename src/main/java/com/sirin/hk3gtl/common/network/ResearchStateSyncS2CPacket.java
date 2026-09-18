package com.sirin.hk3gtl.common.network;



import com.sirin.hk3gtl.client.network.ClientResearchStateSyncHandler;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * S2C 网络包：服务端向客户端同步研究与事件状态。
 *
 * <h3>职责</h3>
 * 将服务端玩家 persistentData 中的研究/事件数据推送到客户端 LocalPlayer，
 * 确保研究 GUI 展示的前置状态、自动完成状态与服务端一致。
 *
 * <h3>序列化字段</h3>
 * <ul>
 *   <li>{@code researchData} - CompoundTag，包含所有 "hk3gtl_res_*" 和 "hk3gtl_evt_*" 键值对</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>如需同步额外数据，在 Hk3ResearchManager.syncClientResearchState 中添加到 CompoundTag</li>
 *   <li>客户端接收后在 applyClientState 中写入 LocalPlayer.persistentData</li>
 *   <li>applyClientState 会先清除旧的 hk3gtl_res_/hk3gtl_evt_ 前缀数据，再写入新数据</li>
 * </ul>
 */
public class ResearchStateSyncS2CPacket {

    /** 序列化字段：包含完整研究/事件状态的 NBT 标签 */
    private final CompoundTag researchData;

    public ResearchStateSyncS2CPacket(CompoundTag researchData) {
        this.researchData = researchData;
    }

    /** 编码：将 researchData NBT 写入网络缓冲区 */
    public static void encode(ResearchStateSyncS2CPacket packet, FriendlyByteBuf buf) {
        buf.writeNbt(packet.researchData);
    }

    /** 解码：从网络缓冲区读取 NBT 标签，null 时兜底为空 CompoundTag */
    public static ResearchStateSyncS2CPacket decode(FriendlyByteBuf buf) {
        CompoundTag tag = buf.readNbt();
        return new ResearchStateSyncS2CPacket(tag == null ? new CompoundTag() : tag);
    }

    /** 处理：在客户端主线程上执行状态覆盖（通过 DistExecutor 确保仅客户端运行） */
    public static void handle(ResearchStateSyncS2CPacket packet, Supplier<NetworkEvent.Context> contextSupplier) {
        NetworkEvent.Context context = contextSupplier.get();
        context.enqueueWork(() ->
                DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                        () -> () -> ClientResearchStateSyncHandler.apply(packet.researchData))
        );
        context.setPacketHandled(true);
    }
}
