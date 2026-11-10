package com.sirin.hk3gtl.common.network;


/**
 * 【文件职责】
 * - 处理 DialogueCloseC2SPacket 网络同步与通信。
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
 * - 新增／修改：关闭包区分暂停与自然完成，服务端仍核验会话与正式终审末段。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 通用对话关闭包 (C2S) —— 客户端通知服务端对话已结束。
 */
public class DialogueCloseC2SPacket {

    private final String dialogueId;
    private final boolean completed;
    private final long nonce;

    public DialogueCloseC2SPacket(String dialogueId, boolean completed, long nonce) {
        this.nonce = nonce;
        this.dialogueId = dialogueId;
        this.completed = completed;
    }

    public static void encode(DialogueCloseC2SPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.dialogueId);
        buf.writeBoolean(pkt.completed);
        buf.writeLong(pkt.nonce);
    }

    public static DialogueCloseC2SPacket decode(FriendlyByteBuf buf) {
        return new DialogueCloseC2SPacket(buf.readUtf(128), buf.readBoolean(), buf.readLong());
    }

    public static void handle(DialogueCloseC2SPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null) {
                DialogueSessionManager.onDialogueEnd(player, pkt.dialogueId, pkt.completed, pkt.nonce);
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
