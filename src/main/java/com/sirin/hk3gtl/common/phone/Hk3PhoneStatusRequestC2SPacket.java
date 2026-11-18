package com.sirin.hk3gtl.common.phone;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

 






public record Hk3PhoneStatusRequestC2SPacket() {
    public static void encode(Hk3PhoneStatusRequestC2SPacket packet, FriendlyByteBuf buffer) {}
    public static Hk3PhoneStatusRequestC2SPacket decode(FriendlyByteBuf buffer) {
        return new Hk3PhoneStatusRequestC2SPacket();
    }
    public static void handle(Hk3PhoneStatusRequestC2SPacket packet, Supplier<NetworkEvent.Context> supplier) {
        var context = supplier.get();
        var sender = context.getSender();
        if (context.getDirection() == NetworkDirection.PLAY_TO_SERVER && sender != null) {
            context.enqueueWork(() -> Hk3PhoneRuntime.poll(sender));
        }
        context.setPacketHandled(true);
    }
}
