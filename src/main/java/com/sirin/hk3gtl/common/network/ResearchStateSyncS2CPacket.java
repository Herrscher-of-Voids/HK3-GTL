package com.sirin.hk3gtl.common.network;


/**
 * 【文件职责】
 * - 处理 ResearchStateSyncS2CPacket 网络同步与通信。
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
 *
 * 【变更记录 #2】2026-07-19 21:49:23（第 2 次备注 · revision 35）
 * - 删除：
 *   1) 删除 common 网络包对 Minecraft、LocalPlayer 客户端类的直接导入和客户端状态覆盖实现。
 * - 新增：
 *   1) 新增 ClientResearchStateSyncHandler 客户端执行器，集中处理玩家 persistentData 覆盖。
 * - 修改：
 *   1) handle 仍通过 DistExecutor 限制物理客户端，但只转发 NBT，不再让 common 包常量池引用客户端类。
 * - 用途：
 *   1) 隔离 S2C 数据包的编解码与客户端应用逻辑，降低专用服务器类加载客户端类的风险。
 */
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
