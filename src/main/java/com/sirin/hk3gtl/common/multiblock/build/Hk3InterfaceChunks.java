package com.sirin.hk3gtl.common.multiblock.build;

import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import it.unimi.dsi.fastutil.longs.LongSet;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;

/** 接口区块保持方块tick，周边FULL按原版票据传播；随核验凭据移交与释放。 */
public final class Hk3InterfaceChunks implements AutoCloseable {
    private static final TicketType<Long> TYPE=TicketType.create("hk3gtl_interfaces",Long::compare);
    private final ServerLevel level;
    private final long owner;
    private final LongOpenHashSet held=new LongOpenHashSet();

    public Hk3InterfaceChunks(ServerLevel level,BlockPos controller) {
        this.level=level;owner=controller.asLong();
    }
    public void retain(BlockPos pos) {
        long chunk=ChunkPos.asLong(pos.getX()>>4,pos.getZ()>>4);
        if(held.add(chunk))level.getChunkSource().addRegionTicket(TYPE,new ChunkPos(chunk),1,owner);
    }
    public void keepOnly(LongSet required) {
        var iterator=held.iterator();
        while(iterator.hasNext()) {
            long chunk=iterator.nextLong();
            if(!required.contains(chunk)) {
                level.getChunkSource().removeRegionTicket(TYPE,new ChunkPos(chunk),1,owner);
                iterator.remove();
            }
        }
    }
    @Override public void close() {
        for(long chunk:held)level.getChunkSource().removeRegionTicket(TYPE,new ChunkPos(chunk),1,owner);
        held.clear();
    }
}
