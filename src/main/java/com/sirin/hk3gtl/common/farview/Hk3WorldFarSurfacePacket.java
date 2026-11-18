package com.sirin.hk3gtl.common.farview;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.shorts.ShortArrayList;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

public record Hk3WorldFarSurfacePacket(ResourceLocation dimension,long session,List<Entry> entries) {
    public static final int MAX_PACKET_BYTES=512*1024;
    public static final int HEADER_BYTES=256;
    private static final int ENTRY_BYTES=16,COLUMN_BYTES=3,RUN_BYTES=9;
    private static final int MAX_COLUMNS=256,MAX_RUNS_PER_COLUMN=4096;
    public record Entry(long chunk,int firstColumn,int columnCount,Hk3WorldFarSurface surface){}

    public static int bytes(Hk3WorldFarSurface surface,int firstColumn,int columnCount){
        return ENTRY_BYTES+COLUMN_BYTES*columnCount+RUN_BYTES*(surface.offsets()[firstColumn+columnCount]-surface.offsets()[firstColumn]);
    }
    public static int columns(Hk3WorldFarSurface surface,int firstColumn,int budget){
        int used=HEADER_BYTES+ENTRY_BYTES,count=0;
        while(firstColumn+count<MAX_COLUMNS){
            int at=firstColumn+count, runs=surface.offsets()[at+1]-surface.offsets()[at];
            int next=COLUMN_BYTES+RUN_BYTES*runs;
            if(used+next>budget)break;
            used+=next;count++;
        }
        return count;
    }

    public static void encode(Hk3WorldFarSurfacePacket packet,FriendlyByteBuf buffer){
        buffer.writeResourceLocation(packet.dimension);buffer.writeLong(packet.session);buffer.writeVarInt(packet.entries.size());
        for(var entry:packet.entries){
            buffer.writeLong(entry.chunk);buffer.writeVarInt(entry.firstColumn);buffer.writeVarInt(entry.columnCount);
            var surface=entry.surface;
            for(int column=0;column<entry.columnCount;column++){
                int at=surface.offsets()[entry.firstColumn+column],end=surface.offsets()[entry.firstColumn+column+1];buffer.writeVarInt(end-at);
                for(int run=at;run<end;run++){
                    buffer.writeShort(surface.starts()[run]);buffer.writeShort(surface.ends()[run]);buffer.writeVarInt(surface.states()[run]);
                }
            }
        }
        if(buffer.writerIndex()>MAX_PACKET_BYTES)throw new IllegalArgumentException("世界远景包超过大小上限");
    }
    public static Hk3WorldFarSurfacePacket decode(FriendlyByteBuf buffer){
        if(buffer.readableBytes()>MAX_PACKET_BYTES)throw new IllegalArgumentException("世界远景包超过大小上限");
        var dimension=buffer.readResourceLocation();long session=buffer.readLong();int count=buffer.readVarInt();
        if(count<0||count>MAX_COLUMNS)throw new IllegalArgumentException("世界远景包数量越界");
        List<Entry> entries=new ArrayList<>(count);
        for(int n=0;n<count;n++){
            long chunk=buffer.readLong();int first=buffer.readVarInt(),columns=buffer.readVarInt();
            if(first<0||first>=MAX_COLUMNS||columns<1||columns>MAX_COLUMNS-first)throw new IllegalArgumentException("世界远景列范围越界");
            int[] offsets=new int[257];var starts=new ShortArrayList();var ends=new ShortArrayList();var states=new IntArrayList();
            for(int column=0;column<columns;column++){
                offsets[first+column]=states.size();int runs=buffer.readVarInt();
                if(runs<0||runs>MAX_RUNS_PER_COLUMN||states.size()+runs>MAX_PACKET_BYTES/5)throw new IllegalArgumentException("世界远景游程数量越界");
                int previousEnd=-2032;
                for(int run=0;run<runs;run++){
                    short start=buffer.readShort(),end=buffer.readShort();int state=buffer.readVarInt();
                    if(start<previousEnd||start>=end||end>2032||state<1||state>Block.BLOCK_STATE_REGISTRY.size())throw new IllegalArgumentException("世界远景游程越界");
                    starts.add(start);ends.add(end);states.add(state);previousEnd=end;
                }
                offsets[first+column+1]=states.size();
            }
            for(int i=0;i<first;i++)offsets[i]=0;
            for(int i=first+columns+1;i<offsets.length;i++)offsets[i]=states.size();
            entries.add(new Entry(chunk,first,columns,new Hk3WorldFarSurface(offsets,starts.toShortArray(),ends.toShortArray(),states.toIntArray())));
        }
        return new Hk3WorldFarSurfacePacket(dimension,session,List.copyOf(entries));
    }
    public static void handle(Hk3WorldFarSurfacePacket packet,Supplier<NetworkEvent.Context> supplier){
        var context=supplier.get();context.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                ()->()->com.sirin.hk3gtl.client.farview.Hk3WorldFarTerrain.accept(packet)));context.setPacketHandled(true);
    }
}
