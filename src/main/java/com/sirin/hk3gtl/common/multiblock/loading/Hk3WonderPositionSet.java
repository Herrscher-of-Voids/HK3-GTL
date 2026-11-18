package com.sirin.hk3gtl.common.multiblock.loading;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3WonderPatternSource;
import it.unimi.dsi.fastutil.longs.AbstractLongSet;
import it.unimi.dsi.fastutil.longs.LongArrayList;
import it.unimi.dsi.fastutil.longs.LongIterator;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Rotation;

/** 按蓝图顺序合并连续坐标，保留原生位置集合的查询和遍历。 */
public final class Hk3WonderPositionSet extends AbstractLongSet {
    private final Hk3WonderPatternSource.Header header;
    private final BlockPos origin;
    private final Rotation rotation,inverse;
    private final LongArrayList starts=new LongArrayList(),ends=new LongArrayList();
    private int size;

    Hk3WonderPositionSet(Hk3WonderPatternSource.Header header,BlockPos origin,Rotation rotation,Rotation inverse){
        this.header=header;this.origin=origin;this.rotation=rotation;this.inverse=inverse;
    }
    private long local(BlockPos world){
        var p=world.subtract(origin).rotate(inverse);
        int x=p.getX()+header.cx(),y=p.getY()+header.cy(),z=p.getZ()+header.cz();
        if(x<0||x>=header.width()||y<0||y>=header.height()||z<0||z>=header.depth())return -1;
        return ((long)x*header.height()+y)*header.depth()+z;
    }
    public boolean contains(BlockPos pos){return containsLocal(local(pos));}
    private boolean containsLocal(long position){
        int low=0,high=starts.size()-1;
        while(low<=high){int mid=(low+high)>>>1;if(starts.getLong(mid)<=position)low=mid+1;else high=mid-1;}
        return high>=0&&position<=ends.getLong(high);
    }
    @Override public boolean contains(long pos){return contains(BlockPos.of(pos));}
    @Override public boolean add(long pos){
        long position=local(BlockPos.of(pos));
        int last=starts.size()-1;
        if(last>=0&&position==ends.getLong(last)+1)ends.set(last,position);
        else {starts.add(position);ends.add(position);}
        size++;return true;
    }
    @Override public int size(){return size;}
    @Override public void clear(){starts.clear();ends.clear();size=0;}
    @Override public LongIterator iterator(){
        return new LongIterator(){
            int run;long offset;
            @Override public boolean hasNext(){return run<starts.size();}
            @Override public long nextLong(){
                long position=starts.getLong(run)+offset++;
                if(position==ends.getLong(run)){run++;offset=0;}
                int z=(int)(position%header.depth());long column=position/header.depth();
                int y=(int)(column%header.height()),x=(int)(column/header.height());
                return new BlockPos(x-header.cx(),y-header.cy(),z-header.cz()).rotate(rotation).offset(origin).asLong();
            }
        };
    }
}
