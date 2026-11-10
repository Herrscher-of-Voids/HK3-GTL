package com.sirin.hk3gtl.common.network;

import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

/** 客户端每秒一次帧耗时反馈；服务端仅给操作者当前任务降速。 */
public record Hk3BuildFramePacket(float millis) {
    public static void encode(Hk3BuildFramePacket p,FriendlyByteBuf b) { b.writeFloat(p.millis); }
    public static Hk3BuildFramePacket decode(FriendlyByteBuf b) { return new Hk3BuildFramePacket(b.readFloat()); }
    public static void handle(Hk3BuildFramePacket p,Supplier<NetworkEvent.Context> supplier) {
        var ctx=supplier.get();ctx.enqueueWork(() -> {
            if(ctx.getSender()!=null) Hk3UniversalTerminalBuilder.clientFrameTime(ctx.getSender(),p.millis);
        });ctx.setPacketHandled(true);
    }
}
