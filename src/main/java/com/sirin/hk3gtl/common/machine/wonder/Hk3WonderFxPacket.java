package com.sirin.hk3gtl.common.machine.wonder;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

public record Hk3WonderFxPacket(String role,ResourceLocation dimension,BlockPos pos,Direction facing,boolean formed,
        boolean running,double idle,double work,long epoch,long age,double seed,int[] ports){
    public static void encode(Hk3WonderFxPacket p,FriendlyByteBuf b){
        b.writeUtf(p.role);b.writeResourceLocation(p.dimension);b.writeBlockPos(p.pos);b.writeEnum(p.facing);b.writeBoolean(p.formed);
        b.writeBoolean(p.running);b.writeDouble(p.idle);b.writeDouble(p.work);b.writeLong(p.epoch);b.writeLong(p.age);b.writeDouble(p.seed);b.writeVarIntArray(p.ports);
    }
    public static Hk3WonderFxPacket decode(FriendlyByteBuf b){
        return new Hk3WonderFxPacket(b.readUtf(),b.readResourceLocation(),b.readBlockPos(),b.readEnum(Direction.class),b.readBoolean(),
                b.readBoolean(),b.readDouble(),b.readDouble(),b.readLong(),b.readLong(),b.readDouble(),b.readVarIntArray());
    }
    public static void handle(Hk3WonderFxPacket p,Supplier<NetworkEvent.Context> supplier){
        var context=supplier.get();context.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->{
            if(p.role.equals("W11"))com.sirin.hk3gtl.client.wonder.Hk3W11FieldScenes.accept(
                    new com.sirin.hk3gtl.client.wonder.Hk3W11FieldScenes.State(p.dimension,p.pos,p.facing,p.formed,p.running,p.work,p.epoch,p.ports));
            else if(p.role.equals("W13"))com.sirin.hk3gtl.client.wonder.Hk3W13FieldScenes.accept(
                    new com.sirin.hk3gtl.client.wonder.Hk3W13FieldScenes.State(p.dimension,p.pos,p.facing,p.formed,p.running,p.work,p.epoch,p.ports));
            else if(p.role.equals("W14"))com.sirin.hk3gtl.client.wonder.Hk3W14FieldScenes.accept(p);
            else if(p.role.equals("W15"))com.sirin.hk3gtl.client.wonder.Hk3W15FieldScenes.accept(p);
            else if(p.role.equals("W07"))com.sirin.hk3gtl.client.wonder.Hk3W07FieldScenes.accept(p);
            else com.sirin.hk3gtl.client.wonder.Hk3WonderFxScenes.accept(p);
        }));context.setPacketHandled(true);
    }
}
