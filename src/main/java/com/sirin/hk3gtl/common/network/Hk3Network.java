package com.sirin.hk3gtl.common.network;

/** 【变更记录 #10】2026-10-01 00:17:25（修订122）：删除无；新增/修改：新增五方应用视图，协议20要求客户端服务端同版；用途：五方首信与团队限定交流保持一致。 */

/** 【变更记录 #9】2026-10-01 00:00:53（修订121）：删除无；新增/修改：首信包新增上下文字段，协议19拒绝旧端误读；用途：个人与团队记录隔离，保留历史与权限。 */

/**
 * 【文件职责／本轮边界】协议13升至14，避免旧客户端错用新增研究布局与供电字段。
 * 【变更记录 #5】2026-09-29 21:06:40（第 5 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：协议13升至14，避免旧客户端错用新增研究布局与供电字段。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */


/** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
/**
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：网络协议升至10；客户端与服务端必须同时使用新包。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
/**
 * 【变更记录 #2】2026-09-29 18:22:20（内测5修订94）
 * - 删除：无；保留历史代码与数据入口。
 * - 新增：五方贸易服务端结算支持及失败校验。
 * - 修改：协议10升至11，追加仅服务端发送的贸易视图；客户端和服务端必须同版。
 * - 用途：执行一次性交齐与交付前无损取消；报价未审核不开放，不授予研究完成。
 */
/** 【变更记录 #3】2026-09-29 18:57:18（内测5修订95）：协议12追加私人手机视图与通知。 */
/** 【变更记录 #4】2026-09-29 19:50:20（内测5修订99）：删除：贸易网络包；协议升至13防止旧包序号错配；新增：无；修改：按负责人决定撤下五方贸易；用途：保留其他系统独立运行。 */
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
/**
 * 【变更记录 #6】2026-09-30 15:49:23（第6次编号备注 · 内测5修订109）
 * 删除：过期的计算或无运行依据的分支；保留历史备注。
 * 新增／修改：注视同步包增加字段，协议升至15，避免新旧客户端误解包。
 * 用途：统一注视与研究联动，服务端判定；不新增结构或贴图。
 */
/**
 * 【变更记录 #7】2026-09-30 16:20:43（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：通知视图增加消息ID/分类/正文打开语义，协议升至16，拒绝旧端误读与无ID覆盖。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/** 【变更记录 #8】2026-09-30 19:49:34（修订116）：删除无；新增微讯息接入；修改：协议18并绑定社交请求为C2S；用途：保留原手机布局与权限，AI不进入服务器业务。 */
/** 【变更记录 #11】2026-10-01 00:44:40（修订123）：删除无；新增/修改：协议升至21，防旧客户端误处理卷轴和个人补谈；用途：个人交流、团队决定及额外收藏分开，保留真实记录。 */
/** 【变更记录 #12】2026-10-01 00:59:10（修订124）：删除无；新增/修改：协议22，客户端读取动态首信补谈总步数；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
/** 【变更记录 #13】2026-10-01 04:19:02（修订128）：删除：旧固定上限或被替代的分支；新增/修改：注册有界阅读片段包，服务端验证本人的当前授权正文；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #14】2026-10-01 04:24:23（修订128）：删除：旧固定上限或被替代的分支；新增/修改：新阅读协议升级版本号，拒绝旧包与新包混连；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #15】2026-10-01 04:27:55（修订128）：删除：旧固定上限或被替代的分支；新增/修改：注册仅手机实际交互的有界包，拒绝任意彩蛋编号和客户端分数；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #16】2026-10-01 04:34:58（修订128）：删除：旧固定上限或被替代的分支；新增/修改：注册IF只读会话令牌包，方向固定服务端到客户端；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #17】2026-10-01 18:42:57（修订140）：删除无；新增仅C2S审查动作包；修改协议至24拒绝旧包错位；用途：正式会面选择有逐页令牌，双端需同版。 */
/** 【变更记录 #18】2026-10-01 19:03:37（修订141）：删除：无；新增／修改：新增实体同步需要双方同版，协议24升25；用途：琪亚娜二审形象和终审统一称谓，保留其他会话行为。 */
/** 【变更记录 #19】2026-11-01 00:36:24（第19次备注 · 内测5修订192）：删除无；新增仅C2S手机后台状态请求；修改在注册末尾追加包且协议25升26，拒绝新端向未注册该包的旧服务端轮询；用途：后台采样不占聊天命令垃圾计数，安装、电量和20tick限流仍由原poll核验。 */
/** 修订198：通用对话包追加服务端逐段令牌，协议27拒绝旧端混连。 */
public class Hk3Network {

    /** 协议版本号，客户端和服务端必须一致，否则握手失败 */
    /** 【变更记录 #16】2026-11-05（修订205）：笔记请求新增标签和任务标志；协议28拒绝旧端错读，双端须同时更新。 */
    private static final String PROTOCOL_VERSION = "33";

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

        CHANNEL.registerMessage(packetIndex++,com.sirin.hk3gtl.common.review.Hk3ReviewActionPacket.class,
                com.sirin.hk3gtl.common.review.Hk3ReviewActionPacket::encode,com.sirin.hk3gtl.common.review.Hk3ReviewActionPacket::decode,
                com.sirin.hk3gtl.common.review.Hk3ReviewActionPacket::handle,java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER));

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

        CHANNEL.registerMessage(packetIndex++, com.sirin.hk3gtl.common.phone.Hk3SocialPacket.class,
                com.sirin.hk3gtl.common.phone.Hk3SocialPacket::encode, com.sirin.hk3gtl.common.phone.Hk3SocialPacket::decode,
                com.sirin.hk3gtl.common.phone.Hk3SocialPacket::handle, java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER));

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
        // 中文备注：该处说明已按当前代码行为整理。
        CHANNEL.registerMessage(packetIndex++, Hk3LetterOpenPacket.class,
                Hk3LetterOpenPacket::encode, Hk3LetterOpenPacket::decode, Hk3LetterOpenPacket::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(packetIndex++, com.sirin.hk3gtl.common.phone.Hk3PhonePacket.class,
                com.sirin.hk3gtl.common.phone.Hk3PhonePacket::encode, com.sirin.hk3gtl.common.phone.Hk3PhonePacket::decode,
                com.sirin.hk3gtl.common.phone.Hk3PhonePacket::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(packetIndex++, com.sirin.hk3gtl.common.phone.Hk3PhoneNotePacket.class,
                com.sirin.hk3gtl.common.phone.Hk3PhoneNotePacket::encode, com.sirin.hk3gtl.common.phone.Hk3PhoneNotePacket::decode,
                com.sirin.hk3gtl.common.phone.Hk3PhoneNotePacket::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER));
        CHANNEL.registerMessage(packetIndex++,com.sirin.hk3gtl.common.easter.Hk3EggReadPacket.class,
            com.sirin.hk3gtl.common.easter.Hk3EggReadPacket::encode,com.sirin.hk3gtl.common.easter.Hk3EggReadPacket::decode,
            com.sirin.hk3gtl.common.easter.Hk3EggReadPacket::handle,java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER));
        CHANNEL.registerMessage(packetIndex++,com.sirin.hk3gtl.common.easter.Hk3EggUiPacket.class,
            com.sirin.hk3gtl.common.easter.Hk3EggUiPacket::encode,com.sirin.hk3gtl.common.easter.Hk3EggUiPacket::decode,
            com.sirin.hk3gtl.common.easter.Hk3EggUiPacket::handle,java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER));
        CHANNEL.registerMessage(packetIndex++,com.sirin.hk3gtl.common.easter.Hk3EggDialoguePacket.class,
            com.sirin.hk3gtl.common.easter.Hk3EggDialoguePacket::encode,com.sirin.hk3gtl.common.easter.Hk3EggDialoguePacket::decode,
            com.sirin.hk3gtl.common.easter.Hk3EggDialoguePacket::handle,java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(packetIndex++,com.sirin.hk3gtl.common.phone.Hk3PhoneStatusRequestC2SPacket.class,
            com.sirin.hk3gtl.common.phone.Hk3PhoneStatusRequestC2SPacket::encode,com.sirin.hk3gtl.common.phone.Hk3PhoneStatusRequestC2SPacket::decode,
            com.sirin.hk3gtl.common.phone.Hk3PhoneStatusRequestC2SPacket::handle,java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER));
        CHANNEL.registerMessage(packetIndex++,Hk3BuildFramePacket.class,Hk3BuildFramePacket::encode,
            Hk3BuildFramePacket::decode,Hk3BuildFramePacket::handle,
            java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER));
        CHANNEL.registerMessage(packetIndex++,com.sirin.hk3gtl.common.farview.Hk3FarViewPacket.class,
            com.sirin.hk3gtl.common.farview.Hk3FarViewPacket::encode,com.sirin.hk3gtl.common.farview.Hk3FarViewPacket::decode,
            com.sirin.hk3gtl.common.farview.Hk3FarViewPacket::handle,java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(packetIndex++,com.sirin.hk3gtl.common.farview.Hk3FarViewPacket.Request.class,
            com.sirin.hk3gtl.common.farview.Hk3FarViewPacket.Request::encode,com.sirin.hk3gtl.common.farview.Hk3FarViewPacket.Request::decode,
            com.sirin.hk3gtl.common.farview.Hk3FarViewPacket.Request::handle,java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER));
        CHANNEL.registerMessage(packetIndex++,com.sirin.hk3gtl.common.machine.w03.Hk3W03FieldPacket.class,
            com.sirin.hk3gtl.common.machine.w03.Hk3W03FieldPacket::encode,com.sirin.hk3gtl.common.machine.w03.Hk3W03FieldPacket::decode,
            com.sirin.hk3gtl.common.machine.w03.Hk3W03FieldPacket::handle,java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(packetIndex++,com.sirin.hk3gtl.common.machine.tree.Hk3TreeProjectionPacket.class,
            com.sirin.hk3gtl.common.machine.tree.Hk3TreeProjectionPacket::encode,com.sirin.hk3gtl.common.machine.tree.Hk3TreeProjectionPacket::decode,
            com.sirin.hk3gtl.common.machine.tree.Hk3TreeProjectionPacket::handle,java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
    }
}
