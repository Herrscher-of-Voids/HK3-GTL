package com.sirin.hk3gtl.common.easter;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.*;
import java.util.function.Supplier;
/** 【变更记录 #1】2026-10-01 04:19:02（修订128）：删除无；新增有界逐页阅读交互包；修改无；用途：携带已显示片段和当前会话令牌，无彩蛋ID、无研究权限、无任意文件访问。 */
public record Hk3EggReadPacket(UUID token,int offset,String piece){
    public static void encode(Hk3EggReadPacket p,FriendlyByteBuf b){b.writeUUID(p.token);b.writeInt(p.offset);b.writeUtf(p.piece,4096);}
    public static Hk3EggReadPacket decode(FriendlyByteBuf b){return new Hk3EggReadPacket(b.readUUID(),b.readInt(),b.readUtf(4096));}
    public static void handle(Hk3EggReadPacket p,Supplier<NetworkEvent.Context> supplier){var c=supplier.get();c.enqueueWork(()->{var user=c.getSender();if(user!=null)Hk3EggReading.accept(user,p.token,p.offset,p.piece);});c.setPacketHandled(true);}
}
