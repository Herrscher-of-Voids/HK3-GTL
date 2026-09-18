package com.sirin.hk3gtl.common.network;



import com.sirin.hk3gtl.client.dialogue.Hk3DialogueScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 通用对话启动包 (S2C) —— 服务端通知客户端打开对话界面。
 */
public class DialogueOpenS2CPacket {

    private final String dialogueId;
    private final String startSegmentId;
    private final int extraData;

    public DialogueOpenS2CPacket(String dialogueId, String startSegmentId, int extraData) {
        this.dialogueId = dialogueId;
        this.startSegmentId = startSegmentId;
        this.extraData = extraData;
    }

    public static void encode(DialogueOpenS2CPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.dialogueId);
        buf.writeUtf(pkt.startSegmentId);
        buf.writeVarInt(pkt.extraData);
    }

    public static DialogueOpenS2CPacket decode(FriendlyByteBuf buf) {
        return new DialogueOpenS2CPacket(buf.readUtf(), buf.readUtf(), buf.readVarInt());
    }

    public static void handle(DialogueOpenS2CPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() ->
                DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                        Hk3DialogueScreen.openFromPacket(pkt.dialogueId, pkt.startSegmentId, pkt.extraData)
                )
        );
        ctx.get().setPacketHandled(true);
    }
}
