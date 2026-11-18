package com.sirin.hk3gtl.common.phone;

import java.util.function.Supplier;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;

public record Hk3PhonePacket(CompoundTag view) {
    public static void encode(Hk3PhonePacket p,FriendlyByteBuf b){b.writeNbt(p.view);}
    public static Hk3PhonePacket decode(FriendlyByteBuf b){var n=b.readNbt();return new Hk3PhonePacket(n==null?new CompoundTag():n);}
    public static void handle(Hk3PhonePacket p,Supplier<NetworkEvent.Context> context){
        context.get().enqueueWork(()->net.minecraftforge.fml.DistExecutor.unsafeRunWhenOn(net.minecraftforge.api.distmarker.Dist.CLIENT,
                ()->()->{
                    if(p.view.getString("Mode").equals("codex_progress"))com.sirin.hk3gtl.client.narrative.Hk3NarrativeCodexScreen.openProgress(p.view);
                    else com.sirin.hk3gtl.client.phone.Hk3PhoneScreen.open(p.view);
                }));
        context.get().setPacketHandled(true);
    }
}
