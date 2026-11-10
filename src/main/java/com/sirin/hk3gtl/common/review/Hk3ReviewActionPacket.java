package com.sirin.hk3gtl.common.review;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

/** 【变更记录 #1】2026-10-01 18:42:57（修订140）：删除无；新增正式审查选择/暂停包；修改服务端校验玩家、团队、页面及令牌；用途：不复用正文预览结算，不接受客户端目标节点或资格。 */
public record Hk3ReviewActionPacket(String dialogue,String segment,int nonce,int choice) {
    public static void encode(Hk3ReviewActionPacket p,FriendlyByteBuf b){b.writeUtf(p.dialogue,128);b.writeUtf(p.segment,128);b.writeInt(p.nonce);b.writeInt(p.choice);}
    public static Hk3ReviewActionPacket decode(FriendlyByteBuf b){return new Hk3ReviewActionPacket(b.readUtf(128),b.readUtf(128),b.readInt(),b.readInt());}
    public static void handle(Hk3ReviewActionPacket p,Supplier<NetworkEvent.Context> ctx){
        ctx.get().enqueueWork(()->{var player=ctx.get().getSender();if(player!=null)Hk3ReviewSessions.action(player,p);});ctx.get().setPacketHandled(true);
    }
}
