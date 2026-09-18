package com.sirin.hk3gtl.common.network;



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
