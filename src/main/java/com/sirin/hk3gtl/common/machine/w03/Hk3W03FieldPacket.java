package com.sirin.hk3gtl.common.machine.w03;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

/** 服务器成型凭据与动画时钟同步；客户端不能自行授予场调试状态。 */
public record Hk3W03FieldPacket(ResourceLocation dimension,BlockPos pos,Direction facing,boolean formed,boolean running,long elapsed,long epoch){
    public static void encode(Hk3W03FieldPacket p,FriendlyByteBuf b){b.writeResourceLocation(p.dimension);b.writeBlockPos(p.pos);b.writeEnum(p.facing);b.writeBoolean(p.formed);b.writeBoolean(p.running);b.writeLong(p.elapsed);b.writeLong(p.epoch);}
    public static Hk3W03FieldPacket decode(FriendlyByteBuf b){return new Hk3W03FieldPacket(b.readResourceLocation(),b.readBlockPos(),b.readEnum(Direction.class),b.readBoolean(),b.readBoolean(),b.readLong(),b.readLong());}
    public static void handle(Hk3W03FieldPacket p,Supplier<NetworkEvent.Context> supplier){
        var ctx=supplier.get();ctx.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->com.sirin.hk3gtl.client.wonder.Hk3W03FieldScenes.accept(p)));ctx.setPacketHandled(true);
    }
}
