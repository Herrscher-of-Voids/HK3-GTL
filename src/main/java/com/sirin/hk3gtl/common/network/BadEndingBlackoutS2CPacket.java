package com.sirin.hk3gtl.common.network;

import com.sirin.hk3gtl.client.badending.Hk3BadEndingClientState;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 服务端 -> 客户端 坏结局黑屏过渡包。
 *
 * <p>客户端收到后开始全屏黑屏淡入（fadeTicks），随后保持全黑（holdTicks）；
 * 若 returnToTitle 为 true，黑屏完成后断开世界并退出到主标题画面（"叙事层打击将玩家踢出游戏"）。</p>
 */
public record BadEndingBlackoutS2CPacket(int fadeTicks, int holdTicks, boolean returnToTitle) {

    public static void encode(BadEndingBlackoutS2CPacket pkt, FriendlyByteBuf buf) {
        buf.writeVarInt(pkt.fadeTicks);
        buf.writeVarInt(pkt.holdTicks);
        buf.writeBoolean(pkt.returnToTitle);
    }

    public static BadEndingBlackoutS2CPacket decode(FriendlyByteBuf buf) {
        return new BadEndingBlackoutS2CPacket(buf.readVarInt(), buf.readVarInt(), buf.readBoolean());
    }

    public static void handle(BadEndingBlackoutS2CPacket pkt, Supplier<NetworkEvent.Context> ctxSupplier) {
        NetworkEvent.Context ctx = ctxSupplier.get();
        // 仅客户端物理端执行，避免专用服务器加载客户端类导致 ClassNotFound
        ctx.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> Hk3BadEndingClientState.startBlackout(pkt.fadeTicks, pkt.holdTicks, pkt.returnToTitle)));
        ctx.setPacketHandled(true);
    }
}
