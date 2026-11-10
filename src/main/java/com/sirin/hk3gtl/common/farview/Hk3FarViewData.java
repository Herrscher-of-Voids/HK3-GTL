package com.sirin.hk3gtl.common.farview;

import it.unimi.dsi.fastutil.longs.Long2ObjectLinkedOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** 只缓存实际读过的方块；旧版粗采样留档但不再作为几何读取，不强加载或模拟远处区块。 */
public final class Hk3FarViewData extends SavedData {
    public static final int MAX_TILES=8192;
    public static final class Tile {
        public final Hk3FarSection section=new Hk3FarSection();
        public long version;
    }
    private static final Map<ServerLevel,Hk3FarViewData> LOADED=new WeakHashMap<>();
    final Long2ObjectLinkedOpenHashMap<Tile> tiles=new Long2ObjectLinkedOpenHashMap<>();
    private long revision=1;
    private long[] legacy=new long[0];
    private final BitSet captured=new BitSet();
    private int captureCursor;
    Hk3FarViewData() {}
    void putTile(long key,Tile tile) {
        // 达到内存上限后淘汰最久未实读的分区，不能永久拒收后来搭建的建筑。
        if(!tiles.containsKey(key)&&tiles.size()>=MAX_TILES)tiles.removeFirst();
        tiles.putAndMoveToLast(key,tile);
    }
    public static Hk3FarViewData get(ServerLevel level) {
        return LOADED.computeIfAbsent(level,l->{
            var data=l.getDataStorage().computeIfAbsent(Hk3FarViewData::load,Hk3FarViewData::new,"hk3gtl_farview_v2");
            var old=l.getDataStorage().get(Hk3FarViewLegacy::load,"hk3gtl_farview_v1");
            if(old!=null)data.legacy=old.areas;
            return data;
        });
    }
    public static void clear(){LOADED.clear();}
    public static long key(BlockPos pos){return BlockPos.asLong(pos.getX()>>4,pos.getY()>>4,pos.getZ()>>4);}
    private static int index(BlockPos pos){return Hk3FarMesh.index(pos.getX()&15,pos.getY()&15,pos.getZ()&15);}
    public static void observe(ServerLevel level,BlockPos pos,BlockState actual) {
        if(actual.isAir())return;
        var data=get(level);long key=key(pos);var tile=data.tiles.getAndMoveToLast(key);
        if(tile==null){tile=new Tile();data.putTile(key,tile);}
        data.update(tile,index(pos),Block.getId(actual)+1);
    }
    public static void changed(ServerLevel level,BlockPos pos,BlockState actual) {
        var data=LOADED.get(level);if(data==null)return;
        var tile=data.tiles.getAndMoveToLast(key(pos));if(tile==null)return;
        data.update(tile,index(pos),actual.isAir()?0:Block.getId(actual)+1);
    }
    private void update(Tile tile,int index,int state) {
        if(tile.section.set(index,state)){tile.version=++revision;setDirty();}
    }
    /** 每tick至多重读一个已加载16³分区，自动替换旧图范围内的缓存；不要求玩家拆除或重建。 */
    public void refresh(ServerLevel level) {
        int count=legacy.length*64;if(count==0)return;
        long deadline=System.nanoTime()+500_000L;
        for(int n=0;n<256&&System.nanoTime()<deadline;n++) {
            int at=captureCursor;captureCursor=(captureCursor+1)%count;if(captured.get(at))continue;
            long area=legacy[at/64];int cell=at%64;
            int x=BlockPos.getX(area)*4+cell/16,y=BlockPos.getY(area)*4+cell/4%4,z=BlockPos.getZ(area)*4+cell%4;
            var chunk=level.getChunkSource().getChunkNow(x,z);if(chunk==null)continue;
            long key=BlockPos.asLong(x,y,z);
            var tile=new Tile();var pos=new BlockPos.MutableBlockPos();boolean any=false;
            for(int i=0;i<Hk3FarMesh.COUNT;i++) {
                var state=chunk.getBlockState(pos.set(x*16+i/256,y*16+i/16%16,z*16+i%16));
                if(!state.isAir()){tile.section.set(i,Block.getId(state)+1);any=true;}
            }
            captured.set(at);
            if(any||tiles.containsKey(key)){tile.version=++revision;putTile(key,tile);setDirty();}
            return;
        }
    }
    private static Hk3FarViewData load(CompoundTag root) {
        var data=new Hk3FarViewData();var paletteTag=root.getList("palette",Tag.TAG_COMPOUND);
        int[] palette=new int[paletteTag.size()+1];
        for(int i=0;i<paletteTag.size();i++) {
            var state=NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(),paletteTag.getCompound(i));
            palette[i+1]=state.isAir()?0:Block.getId(state)+1;
        }
        var tiles=root.getList("tiles",Tag.TAG_COMPOUND);
        for(int i=0;i<Math.min(MAX_TILES,tiles.size());i++) {
            var raw=tiles.getCompound(i);int[] local=raw.getIntArray("palette");byte[] cells=raw.getByteArray("cells");
            if(local.length<1||local.length>Hk3FarMesh.COUNT+1||local[0]!=0||cells.length!=Hk3FarMesh.COUNT*2)continue;
            var tile=new Tile();boolean valid=true;
            for(int at=0;at<Hk3FarMesh.COUNT;at++) {
                int id=(cells[at*2]&255)|(cells[at*2+1]&255)<<8;
                if(id>=local.length||local[id]<0||local[id]>=palette.length){valid=false;break;}
                tile.section.set(at,palette[local[id]]);
            }
            if(valid){tile.version=++data.revision;data.tiles.put(raw.getLong("key"),tile);}
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag root) {
        var palette=new IntSummary();var list=new ListTag();
        for(var entry:tiles.long2ObjectEntrySet()) {
            var raw=new CompoundTag();raw.putLong("key",entry.getLongKey());var snapshot=entry.getValue().section.snapshot();
            int[] local=Arrays.stream(snapshot.palette()).map(palette::index).toArray();byte[] cells=new byte[Hk3FarMesh.COUNT*2];
            for(int i=0;i<snapshot.cells().length;i++){int id=Short.toUnsignedInt(snapshot.cells()[i]);cells[i*2]=(byte)id;cells[i*2+1]=(byte)(id>>8);}
            raw.putIntArray("palette",local);raw.putByteArray("cells",cells);list.add(raw);
        }
        root.put("palette",palette.tags);root.put("tiles",list);return root;
    }
    private static final class IntSummary {
        final Map<Integer,Integer> ids=new HashMap<>();final ListTag tags=new ListTag();
        int index(int state){
            if(state==0)return 0;
            return ids.computeIfAbsent(state,s->{tags.add(NbtUtils.writeBlockState(Block.stateById(s-1)));return tags.size();});
        }
    }
}
