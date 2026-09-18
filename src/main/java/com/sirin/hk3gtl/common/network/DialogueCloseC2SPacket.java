package com.sirin.hk3gtl.common.network;



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

    public DialogueCloseC2SPacket(String dialogueId) {
        this.dialogueId = dialogueId;
    }

    public static void encode(DialogueCloseC2SPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.dialogueId);
    }

    public static DialogueCloseC2SPacket decode(FriendlyByteBuf buf) {
        return new DialogueCloseC2SPacket(buf.readUtf());
    }

    public static void handle(DialogueCloseC2SPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null) {
                DialogueSessionManager.onDialogueEnd(player, pkt.dialogueId);
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
