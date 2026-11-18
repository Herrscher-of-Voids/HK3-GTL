package com.sirin.hk3gtl.common.machine.w12;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

public record Hk3W12FieldPacket(ResourceLocation dimension, BlockPos pos, Direction facing, boolean formed,
        boolean running, double phase, double flow, long epoch, long age, double seed, int[] ports) {
    public static void encode(Hk3W12FieldPacket p, FriendlyByteBuf b) {
        b.writeResourceLocation(p.dimension);b.writeBlockPos(p.pos);b.writeEnum(p.facing);b.writeBoolean(p.formed);
        b.writeBoolean(p.running);b.writeDouble(p.phase);b.writeDouble(p.flow);b.writeLong(p.epoch);b.writeLong(p.age);b.writeDouble(p.seed);
        b.writeVarIntArray(p.ports);
    }
    public static Hk3W12FieldPacket decode(FriendlyByteBuf b) {
        return new Hk3W12FieldPacket(b.readResourceLocation(),b.readBlockPos(),b.readEnum(Direction.class),
                b.readBoolean(),b.readBoolean(),b.readDouble(),b.readDouble(),b.readLong(),b.readLong(),b.readDouble(),b.readVarIntArray());
    }
    public static void handle(Hk3W12FieldPacket p, Supplier<NetworkEvent.Context> supplier) {
        var context=supplier.get();context.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                ()->()->com.sirin.hk3gtl.client.wonder.Hk3W12FieldScenes.accept(p)));context.setPacketHandled(true);
    }
}
