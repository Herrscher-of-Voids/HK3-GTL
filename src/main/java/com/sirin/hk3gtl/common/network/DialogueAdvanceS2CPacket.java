package com.sirin.hk3gtl.common.network;



import com.sirin.hk3gtl.client.dialogue.Hk3DialogueScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 通用对话推进包 (S2C) —— 服务端通知客户端跳转到指定 segment。
 */
public class DialogueAdvanceS2CPacket {

    private final String dialogueId;
    private final String nextSegmentId;
    private final int extraData;

    public DialogueAdvanceS2CPacket(String dialogueId, String nextSegmentId, int extraData) {
        this.dialogueId = dialogueId;
        this.nextSegmentId = nextSegmentId;
        this.extraData = extraData;
    }

    public static void encode(DialogueAdvanceS2CPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.dialogueId);
        buf.writeUtf(pkt.nextSegmentId);
        buf.writeVarInt(pkt.extraData);
    }

    public static DialogueAdvanceS2CPacket decode(FriendlyByteBuf buf) {
        return new DialogueAdvanceS2CPacket(buf.readUtf(), buf.readUtf(), buf.readVarInt());
    }

    public static void handle(DialogueAdvanceS2CPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() ->
                DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                        Hk3DialogueScreen.advanceFromPacket(pkt.dialogueId, pkt.nextSegmentId, pkt.extraData)
                )
        );
        ctx.get().setPacketHandled(true);
    }
}
