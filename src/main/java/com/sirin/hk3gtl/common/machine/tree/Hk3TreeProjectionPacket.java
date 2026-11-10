package com.sirin.hk3gtl.common.machine.tree;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

/** 服务端只同步已加载I34的真实场状态，不接受客户端成型声明。 */
public record Hk3TreeProjectionPacket(ResourceLocation dimension,BlockPos pos,Direction facing,int mode,boolean paused,long clock){
    public static void encode(Hk3TreeProjectionPacket p,FriendlyByteBuf b){b.writeResourceLocation(p.dimension);b.writeBlockPos(p.pos);b.writeEnum(p.facing);b.writeByte(p.mode);b.writeBoolean(p.paused);b.writeLong(p.clock);}
    public static Hk3TreeProjectionPacket decode(FriendlyByteBuf b){return new Hk3TreeProjectionPacket(b.readResourceLocation(),b.readBlockPos(),b.readEnum(Direction.class),b.readUnsignedByte(),b.readBoolean(),b.readLong());}
    public static void handle(Hk3TreeProjectionPacket p,Supplier<NetworkEvent.Context> supplier){var c=supplier.get();c.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->com.sirin.hk3gtl.client.tree.Hk3TreeProjectionScenes.accept(p)));c.setPacketHandled(true);}
}
