package com.sirin.hk3gtl.common.phone;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

public record Hk3SocialPacket(String action,String contact,String text,boolean preview){
    public static void encode(Hk3SocialPacket p,FriendlyByteBuf b){b.writeUtf(p.action,16);b.writeUtf(p.contact,40);b.writeUtf(p.text,512);b.writeBoolean(p.preview);}
    public static Hk3SocialPacket decode(FriendlyByteBuf b){return new Hk3SocialPacket(b.readUtf(16),b.readUtf(40),b.readUtf(512),b.readBoolean());}
    public static void handle(Hk3SocialPacket p,Supplier<NetworkEvent.Context> ctx){ctx.get().enqueueWork(()->{var player=ctx.get().getSender();if(player!=null)Hk3SocialService.handle(player,p);});ctx.get().setPacketHandled(true);}
}
