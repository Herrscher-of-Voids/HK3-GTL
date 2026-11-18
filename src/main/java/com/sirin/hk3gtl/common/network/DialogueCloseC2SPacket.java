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
