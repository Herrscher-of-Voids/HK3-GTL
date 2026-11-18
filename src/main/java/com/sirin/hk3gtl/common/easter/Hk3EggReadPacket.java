package com.sirin.hk3gtl.common.easter;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.*;
import java.util.function.Supplier;
 
public record Hk3EggReadPacket(UUID token,int offset,String piece){
    public static void encode(Hk3EggReadPacket p,FriendlyByteBuf b){b.writeUUID(p.token);b.writeInt(p.offset);b.writeUtf(p.piece,4096);}
    public static Hk3EggReadPacket decode(FriendlyByteBuf b){return new Hk3EggReadPacket(b.readUUID(),b.readInt(),b.readUtf(4096));}
    public static void handle(Hk3EggReadPacket p,Supplier<NetworkEvent.Context> supplier){var c=supplier.get();c.enqueueWork(()->{var user=c.getSender();if(user!=null)Hk3EggReading.accept(user,p.token,p.offset,p.piece);});c.setPacketHandled(true);}
}
