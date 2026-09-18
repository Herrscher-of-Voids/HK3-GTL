package com.sirin.hk3gtl.common.network;



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

    public DialoguePlayerChoiceC2SPacket(String dialogueId, int choiceIndex) {
        this.dialogueId = dialogueId;
        this.choiceIndex = choiceIndex;
    }

    public static void encode(DialoguePlayerChoiceC2SPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.dialogueId);
        buf.writeVarInt(pkt.choiceIndex);
    }

    public static DialoguePlayerChoiceC2SPacket decode(FriendlyByteBuf buf) {
        return new DialoguePlayerChoiceC2SPacket(buf.readUtf(), buf.readVarInt());
    }

    public static void handle(DialoguePlayerChoiceC2SPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null) {
                DialogueSessionManager.onPlayerChoice(player, pkt.dialogueId, pkt.choiceIndex);
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
