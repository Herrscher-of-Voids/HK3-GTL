package com.sirin.hk3gtl.common.network;


/**
 * 【文件职责】
 * - 处理 DialogueAbortS2CPacket 网络同步与通信。
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
import com.sirin.hk3gtl.client.dialogue.Hk3DialogueScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 服务端强制关闭对话界面（不触发结束处理器），用于校验失败等场景。
 */
public class DialogueAbortS2CPacket {

    private final String dialogueId;
    /** 发给玩家的翻译键，可为空 */
    private final String messageKey;

    public DialogueAbortS2CPacket(String dialogueId, String messageKey) {
        this.dialogueId = dialogueId;
        this.messageKey = messageKey;
    }

    public static void encode(DialogueAbortS2CPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.dialogueId);
        buf.writeUtf(pkt.messageKey);
    }

    public static DialogueAbortS2CPacket decode(FriendlyByteBuf buf) {
        return new DialogueAbortS2CPacket(buf.readUtf(), buf.readUtf());
    }

    public static void handle(DialogueAbortS2CPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() ->
                DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                        Hk3DialogueScreen.abortFromPacket(pkt.dialogueId, pkt.messageKey)
                )
        );
        ctx.get().setPacketHandled(true);
    }
}
