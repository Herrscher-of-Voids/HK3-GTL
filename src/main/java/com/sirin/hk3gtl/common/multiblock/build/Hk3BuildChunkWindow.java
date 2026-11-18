package com.sirin.hk3gtl.common.multiblock.build;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import java.util.LinkedHashSet;
import java.util.function.IntToLongFunction;
import java.util.function.IntUnaryOperator;

/** 低端四个、高端最多八个FULL区块票据，不提升到实体tick。 */
public final class Hk3BuildChunkWindow implements AutoCloseable {
    private static final TicketType<Long> TYPE = TicketType.create("hk3gtl_build_window", Long::compare);
    private static final int MAX_WINDOW = Runtime.getRuntime().availableProcessors() >= 8 ? 8 : 4;
    private final ServerLevel level;
    private final long owner;
    private final LinkedHashSet<Long> held = new LinkedHashSet<>();
    private int ahead;
    private long readyTick=Long.MIN_VALUE,readyChunk=Long.MIN_VALUE;
    public Hk3BuildChunkWindow(ServerLevel level, long owner) { this.level=level; this.owner=owner; }

    public boolean ready(int cursor, int size, IntToLongFunction chunkAt, IntUnaryOperator nextChunk) {
        long current=chunkAt.applyAsLong(cursor);
        if(readyTick==level.getGameTime() && readyChunk==current)return true;
        if(!held.contains(current))ahead=nextChunk.applyAsInt(cursor);
        while (!held.isEmpty() && held.iterator().next()!=current) {
            long first=held.iterator().next(); held.remove(first); remove(first);
        }
        add(current);
        ahead=Math.max(ahead,nextChunk.applyAsInt(cursor));
        int window=level.getServer().getAverageTickTime()<30 ? MAX_WINDOW : 4;
        while(ahead<size && held.size()<window) {
            add(chunkAt.applyAsLong(ahead));
            ahead=nextChunk.applyAsInt(ahead);
        }
        boolean ready=level.getChunkSource().getChunkNow(ChunkPos.getX(current),ChunkPos.getZ(current))!=null;
        if(ready){readyTick=level.getGameTime();readyChunk=current;}
        return ready;
    }
    private void add(long chunk) {
        if(held.add(chunk)) level.getChunkSource().addRegionTicket(TYPE,new ChunkPos(chunk),0,owner);
    }
    private void remove(long chunk) { level.getChunkSource().removeRegionTicket(TYPE,new ChunkPos(chunk),0,owner); }
    public int size() { return held.size(); }
    @Override public void close() { for(long chunk:held) remove(chunk);held.clear();ahead=0;readyTick=Long.MIN_VALUE; }
}
