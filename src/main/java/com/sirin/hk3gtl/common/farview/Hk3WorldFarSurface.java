package com.sirin.hk3gtl.common.farview;

import com.mojang.serialization.Codec;
import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.shorts.ShortArrayList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.PalettedContainer;

import java.util.Map;
import java.util.Arrays;
import java.util.TreeMap;
import java.util.function.Supplier;

/** 按列压缩真实方块，保留外墙、岛底与不同高度之间的空气间隙。 */
public record Hk3WorldFarSurface(int[] offsets,short[] starts,short[] ends,int[] states) {
    private static final Codec<PalettedContainer<BlockState>> STATES=PalettedContainer.codecRW(
            Block.BLOCK_STATE_REGISTRY,BlockState.CODEC,PalettedContainer.Strategy.SECTION_STATES,Blocks.AIR.defaultBlockState());

    public int bytes(){return 1120+states.length*8;}
    public boolean empty(){return states.length==0;}
    public boolean same(Hk3WorldFarSurface other){
        return Arrays.equals(offsets,other.offsets)&&Arrays.equals(starts,other.starts)
                &&Arrays.equals(ends,other.ends)&&Arrays.equals(states,other.states);
    }
    public static Hk3WorldFarSurface capture(LevelChunk chunk){
        return snapshot(chunk).get();
    }
    public static Supplier<Hk3WorldFarSurface> snapshot(LevelChunk chunk){
        var capture=new Snapshot(chunk);
        capture.copyUntil(Long.MAX_VALUE,Integer.MAX_VALUE);
        return capture;
    }
    public static final class Snapshot implements Supplier<Hk3WorldFarSurface> {
        private LevelChunk chunk;
        private final int first,min,top;
        private int section;
        private final Map<Integer,PalettedContainer<BlockState>> sections=new TreeMap<>();
        public Snapshot(LevelChunk chunk){
            this.chunk=chunk;first=chunk.getMinSection();min=chunk.getMinBuildHeight();top=chunk.getMaxBuildHeight();
        }
        public boolean copyUntil(long deadline,int limit){
            if(chunk==null)return true;
            var loaded=chunk.getSections();
            while(section<loaded.length&&limit-->0&&System.nanoTime()<deadline){
                var source=loaded[section];
                if(!source.hasOnlyAir())sections.put(first+section,source.getStates().copy());
                section++;
            }
            if(section<loaded.length)return false;
            chunk=null;
            return true;
        }
        @Override public Hk3WorldFarSurface get(){return collect(sections,min,top);}
    }
    public static Hk3WorldFarSurface read(CompoundTag chunk,int min,int height){
        Map<Integer,PalettedContainer<BlockState>> sections=new TreeMap<>();
        for(var element:chunk.getList("sections",10)){
            var section=(CompoundTag)element;int y=section.getByte("Y");
            if(y*16>=min+height||y*16+16<=min||!section.contains("block_states",10))continue;
            var blocks=STATES.parse(NbtOps.INSTANCE,section.getCompound("block_states")).result().orElseThrow();
            if(blocks.maybeHas(state->!state.isAir()))sections.put(y,blocks);
        }
        return collect(sections,min,min+height);
    }
    private static Hk3WorldFarSurface collect(Map<Integer,PalettedContainer<BlockState>> sections,int min,int top){
        int[] offsets=new int[257];var starts=new ShortArrayList();var ends=new ShortArrayList();var states=new IntArrayList();
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){
            if(Thread.currentThread().isInterrupted())return null;
            offsets[x*16+z]=states.size();int previous=0,start=0,end=0;
            for(var section:sections.entrySet()){
                int from=Math.max(min,section.getKey()*16),to=Math.min(top,section.getKey()*16+16);
                for(int y=from;y<to;y++){
                    var state=section.getValue().get(x,y&15,z);int current=state.isAir()?0:Block.getId(state)+1;
                    if(current!=previous||y!=end){
                        if(previous!=0){starts.add((short)start);ends.add((short)end);states.add(previous);}
                        previous=current;start=y;
                    }
                    end=y+1;
                }
            }
            if(previous!=0){starts.add((short)start);ends.add((short)end);states.add(previous);}
        }
        offsets[256]=states.size();
        return new Hk3WorldFarSurface(offsets,starts.toShortArray(),ends.toShortArray(),states.toIntArray());
    }
}
