package com.sirin.hk3gtl.common.easter;
import java.util.*;
import java.util.function.Supplier;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;

public record Hk3EggDialoguePacket(String dialogue,String segment,UUID token){
    public static void encode(Hk3EggDialoguePacket p,FriendlyByteBuf b){b.writeUtf(p.dialogue,128);b.writeUtf(p.segment,128);b.writeUUID(p.token);}
    public static Hk3EggDialoguePacket decode(FriendlyByteBuf b){return new Hk3EggDialoguePacket(b.readUtf(128),b.readUtf(128),b.readUUID());}
    public static void handle(Hk3EggDialoguePacket p,Supplier<NetworkEvent.Context> supplier){var c=supplier.get();c.enqueueWork(()->net.minecraftforge.fml.DistExecutor.unsafeRunWhenOn(net.minecraftforge.api.distmarker.Dist.CLIENT,()->()->com.sirin.hk3gtl.client.dialogue.Hk3EggDialogueClient.begin(p)));c.setPacketHandled(true);}
}
