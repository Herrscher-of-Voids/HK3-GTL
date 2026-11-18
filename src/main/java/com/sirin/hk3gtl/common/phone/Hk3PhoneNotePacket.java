package com.sirin.hk3gtl.common.phone;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;
 




 
public record Hk3PhoneNotePacket(boolean delete,String id,int version,String title,String body,int colors,boolean task) {
    public Hk3PhoneNotePacket(boolean delete,String id,int version,String title,String body){this(delete,id,version,title,body,0,false);}
    public static void encode(Hk3PhoneNotePacket p,FriendlyByteBuf b){b.writeBoolean(p.delete);b.writeUtf(p.id,36);b.writeVarInt(p.version);b.writeUtf(p.title,64);b.writeUtf(p.body,4096);b.writeVarInt(p.colors);b.writeBoolean(p.task);}
    public static Hk3PhoneNotePacket decode(FriendlyByteBuf b){return new Hk3PhoneNotePacket(b.readBoolean(),b.readUtf(36),b.readVarInt(),b.readUtf(64),b.readUtf(4096),b.readVarInt(),b.readBoolean());}
    public static void handle(Hk3PhoneNotePacket p,Supplier<NetworkEvent.Context> ctx){
        ctx.get().enqueueWork(()->{var player=ctx.get().getSender();if(player!=null)Hk3PhoneAppService.writeNote(player,p);});ctx.get().setPacketHandled(true);
    }
}
