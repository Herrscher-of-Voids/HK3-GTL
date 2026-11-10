package com.sirin.hk3gtl.common.network;


/**
 * 【文件职责】
 * - 处理 DialoguePlayerChoiceC2SPacket 网络同步与通信。
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
/**
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：选择包加入当前段落ID及长度限制，拒绝过时段落请求。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 通用对话选择包 (C2S) —— 客户端告知服务端玩家的选项选择。
 */
public class DialoguePlayerChoiceC2SPacket {

    private final String dialogueId;
    private final int choiceIndex;
    private final String segmentId;
    private final long nonce;

    public DialoguePlayerChoiceC2SPacket(String dialogueId, String segmentId, int choiceIndex, long nonce) {
        this.nonce = nonce;
        this.dialogueId = dialogueId;
        this.segmentId = segmentId;
        this.choiceIndex = choiceIndex;
    }

    public static void encode(DialoguePlayerChoiceC2SPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.dialogueId);
        buf.writeUtf(pkt.segmentId);
        buf.writeVarInt(pkt.choiceIndex);
        buf.writeLong(pkt.nonce);
    }

    public static DialoguePlayerChoiceC2SPacket decode(FriendlyByteBuf buf) {
        return new DialoguePlayerChoiceC2SPacket(buf.readUtf(128), buf.readUtf(128), buf.readVarInt(), buf.readLong());
    }

    public static void handle(DialoguePlayerChoiceC2SPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null) {
                DialogueSessionManager.onPlayerChoice(player, pkt.dialogueId, pkt.segmentId, pkt.choiceIndex, pkt.nonce);
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
