package com.sirin.hk3gtl.common.farview;

import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.*;
import java.util.function.Supplier;

public record Hk3FarViewPacket(ResourceLocation dimension,long[] members,List<Entry> updates) {
    public record Entry(long key,Hk3FarSection.Snapshot section) {}
    public static void encode(Hk3FarViewPacket p,FriendlyByteBuf b) {
        b.writeResourceLocation(p.dimension);b.writeBoolean(p.members!=null);
        if(p.members!=null)b.writeLongArray(p.members);
        b.writeVarInt(p.updates.size());
        for(var tile:p.updates){
            b.writeLong(tile.key);b.writeVarIntArray(tile.section.palette());
            short[] cells=tile.section.cells();
            for(int at=0;at<cells.length;){
                int end=at+1;while(end<cells.length&&cells[end]==cells[at])end++;
                b.writeVarInt(end-at);b.writeVarInt(Short.toUnsignedInt(cells[at]));at=end;
            }
        }
    }
    public static Hk3FarViewPacket decode(FriendlyByteBuf b) {
        var dimension=b.readResourceLocation();long[] members=b.readBoolean()?b.readLongArray(null,Hk3FarViewData.MAX_TILES):null;
        int count=b.readVarInt();if(count<0||count>4)throw new IllegalArgumentException("远景包数量越界");
        List<Entry> entries=new ArrayList<>(count);
        for(int i=0;i<count;i++){
            long key=b.readLong();int[] palette=b.readVarIntArray(Hk3FarMesh.COUNT+1);short[] cells=new short[Hk3FarMesh.COUNT];
            for(int at=0;at<cells.length;){
                int length=b.readVarInt(),state=b.readVarInt();
                if(length<1||length>cells.length-at||state<0||state>=palette.length)throw new IllegalArgumentException("远景游程越界");
                Arrays.fill(cells,at,at+length,(short)state);at+=length;
            }
            entries.add(new Entry(key,new Hk3FarSection.Snapshot(palette,cells)));
        }
        return new Hk3FarViewPacket(dimension,members,List.copyOf(entries));
    }
    public static void handle(Hk3FarViewPacket p,Supplier<NetworkEvent.Context> supplier) {
        var ctx=supplier.get();ctx.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                ()->()->com.sirin.hk3gtl.client.farview.Hk3FarViewRenderer.accept(p)));ctx.setPacketHandled(true);
    }
    public record Request(boolean enabled,int distance,long session) {
        public static void encode(Request p,FriendlyByteBuf b){b.writeBoolean(p.enabled);b.writeVarInt(p.distance);b.writeLong(p.session);}
        public static Request decode(FriendlyByteBuf b){return new Request(b.readBoolean(),b.readVarInt(),b.readLong());}
        public static void handle(Request p,Supplier<NetworkEvent.Context> supplier){
            var ctx=supplier.get();ctx.enqueueWork(()->{if(ctx.getSender()!=null)Hk3FarViewSync.request(ctx.getSender(),p.enabled,p.distance,p.session);});ctx.setPacketHandled(true);
        }
    }
}
