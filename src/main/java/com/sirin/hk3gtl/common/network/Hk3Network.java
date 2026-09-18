package com.sirin.hk3gtl.common.network;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

/**
 * 网络通道注册中心 —— 负责注册所有 C2S/S2C 网络包。
 *
 * <h3>职责</h3>
 * 创建 Forge SimpleChannel 并注册所有自定义网络包（研究系统同步、对话触发等）。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增网络包：在 init() 末尾调用 CHANNEL.registerMessage()，packetIndex 自增</li>
 *   <li>网络包类需实现 encode/decode/handle 三个静态方法</li>
 *   <li>PROTOCOL_VERSION 变更会导致客户端/服务端版本不匹配被拒绝连接</li>
 * </ul>
 */
public class Hk3Network {

    /** 协议版本号，客户端和服务端必须一致，否则握手失败 */
    private static final String PROTOCOL_VERSION = "8";

    /** 网络包自增索引，每注册一个包 +1，不可重复 */
    private static int packetIndex = 0;

    /** 主网络通道，通道ID为 "hk3gtl:main" */
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(Hk3Constants.MOD_ID, "main"),
            () -> PROTOCOL_VERSION,
            PROTOCOL_VERSION::equals,
            PROTOCOL_VERSION::equals
    );

    /** 防止重复初始化的标记 */
    private static boolean initialized = false;

    /**
     * 注册所有网络包。在模组初始化阶段调用，仅执行一次。
     * 包注册顺序：研究同步包 → 通用对话包。
     */
    public static void init() {
        if (initialized) return;
        initialized = true;

        CHANNEL.registerMessage(
                packetIndex++,
                ResearchSubmitPacket.class,
                ResearchSubmitPacket::encode,
                ResearchSubmitPacket::decode,
                ResearchSubmitPacket::handle
        );

        CHANNEL.registerMessage(
                packetIndex++,
                ResearchStateSyncRequestC2SPacket.class,
                ResearchStateSyncRequestC2SPacket::encode,
                ResearchStateSyncRequestC2SPacket::decode,
                ResearchStateSyncRequestC2SPacket::handle
        );

        CHANNEL.registerMessage(
                packetIndex++,
                ResearchStateSyncS2CPacket.class,
                ResearchStateSyncS2CPacket::encode,
                ResearchStateSyncS2CPacket::decode,
                ResearchStateSyncS2CPacket::handle
        );

        CHANNEL.registerMessage(
                packetIndex++,
                ResearchOpenS2CPacket.class,
                ResearchOpenS2CPacket::encode,
                ResearchOpenS2CPacket::decode,
                ResearchOpenS2CPacket::handle
        );

        // ═══ 通用对话系统网络包 ═══

        CHANNEL.registerMessage(
                packetIndex++,
                DialogueOpenS2CPacket.class,
                DialogueOpenS2CPacket::encode,
                DialogueOpenS2CPacket::decode,
                DialogueOpenS2CPacket::handle
        );

        CHANNEL.registerMessage(
                packetIndex++,
                DialogueAdvanceS2CPacket.class,
                DialogueAdvanceS2CPacket::encode,
                DialogueAdvanceS2CPacket::decode,
                DialogueAdvanceS2CPacket::handle
        );

        CHANNEL.registerMessage(
                packetIndex++,
                DialoguePlayerChoiceC2SPacket.class,
                DialoguePlayerChoiceC2SPacket::encode,
                DialoguePlayerChoiceC2SPacket::decode,
                DialoguePlayerChoiceC2SPacket::handle
        );

        CHANNEL.registerMessage(
                packetIndex++,
                DialogueCloseC2SPacket.class,
                DialogueCloseC2SPacket::encode,
                DialogueCloseC2SPacket::decode,
                DialogueCloseC2SPacket::handle
        );

        CHANNEL.registerMessage(
                packetIndex++,
                DialogueAbortS2CPacket.class,
                DialogueAbortS2CPacket::encode,
                DialogueAbortS2CPacket::decode,
                DialogueAbortS2CPacket::handle
        );

        CHANNEL.registerMessage(
                packetIndex++,
                ModWelcomeS2CPacket.class,
                ModWelcomeS2CPacket::encode,
                ModWelcomeS2CPacket::decode,
                ModWelcomeS2CPacket::handle
        );

        // ═══ 终焉注视度系统 HUD 同步包 ═══
        CHANNEL.registerMessage(
                packetIndex++,
                GazeSyncS2CPacket.class,
                GazeSyncS2CPacket::encode,
                GazeSyncS2CPacket::decode,
                GazeSyncS2CPacket::handle
        );

        // ═══ 西琳出场特效·强制清除粒子包 ═══
        CHANNEL.registerMessage(
                packetIndex++,
                ClearParticlesS2CPacket.class,
                ClearParticlesS2CPacket::encode,
                ClearParticlesS2CPacket::decode,
                ClearParticlesS2CPacket::handle
        );

        // ═══ 坏结局·黑屏过渡与进程关闭包 ═══
        CHANNEL.registerMessage(
                packetIndex++,
                BadEndingBlackoutS2CPacket.class,
                BadEndingBlackoutS2CPacket::encode,
                BadEndingBlackoutS2CPacket::decode,
                BadEndingBlackoutS2CPacket::handle
        );
    }
}
