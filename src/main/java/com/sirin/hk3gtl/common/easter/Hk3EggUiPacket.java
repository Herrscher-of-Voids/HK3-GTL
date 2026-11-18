package com.sirin.hk3gtl.common.easter;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;
public record Hk3EggUiPacket(String action,String value){
    public static void encode(Hk3EggUiPacket p,FriendlyByteBuf b){b.writeUtf(p.action,24);b.writeUtf(p.value,512);}
    public static Hk3EggUiPacket decode(FriendlyByteBuf b){return new Hk3EggUiPacket(b.readUtf(24),b.readUtf(512));}
    public static void handle(Hk3EggUiPacket p,Supplier<NetworkEvent.Context> supplier){var c=supplier.get();c.enqueueWork(()->{var user=c.getSender();if(user!=null){if(p.action.equals("dialogue"))Hk3EggDialogueActions.input(user,p.value);else if(p.action.startsWith("egg_"))Hk3EggUiReceipts.input(user,p.action,p.value);else if(p.action.equals("inventory")||p.action.equals("map_view"))Hk3EggViews.input(user,p.action);else Hk3EggPhone.input(user,p.action,p.value);}});c.setPacketHandled(true);}
}
