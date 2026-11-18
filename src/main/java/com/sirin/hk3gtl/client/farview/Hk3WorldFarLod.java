package com.sirin.hk3gtl.client.farview;

import com.sirin.hk3gtl.common.farview.Hk3WorldFarSurface;
import it.unimi.dsi.fastutil.ints.Int2IntMap;
import it.unimi.dsi.fastutil.ints.Int2IntOpenHashMap;
import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.longs.LongArrayList;
import it.unimi.dsi.fastutil.shorts.ShortArrayList;

import java.util.Arrays;

/** 仅合并完整覆盖且透明性一致的列，保留细条与孔洞的实际轮廓。 */
final class Hk3WorldFarLod {
    static final class Workspace {
        final LongArrayList events=new LongArrayList();
        final Int2IntOpenHashMap active=new Int2IntOpenHashMap();
        final ShortArrayList starts=new ShortArrayList(),ends=new ShortArrayList();
        final IntArrayList states=new IntArrayList();
    }
    private Hk3WorldFarLod() {}

    static Hk3WorldFarSurface merge(Hk3WorldFarShell.Column[][] columns,int x,int z,int width,int depth,
                                    Int2IntMap colors,Workspace workspace) {
        var events=workspace.events;var active=workspace.active;
        events.clear();active.clear();
        int bottom=0,top=0;
        for(int dx=0;dx<width;dx++)for(int dz=0;dz<depth;dz++) {
            if(Thread.currentThread().isInterrupted())return null;
            var column=columns[x+dx+1][z+dz+1];
            if(column==null)return null;
            var surface=column.surface();
            int low=Integer.MAX_VALUE,high=Integer.MIN_VALUE;
            for(int run=column.from();run<column.to();run++) {
                int color=colors.get(surface.states()[run]);
                if(color==0)continue;
                low=Math.min(low,surface.starts()[run]);high=Math.max(high,surface.ends()[run]);
                events.add(event(surface.starts()[run],color,1));
                events.add(event(surface.ends()[run],color,0));
            }
            if(dx==0&&dz==0){bottom=low;top=high;}
            else if(low!=bottom||high!=top)return null;
        }
        long[] ordered=events.elements();int size=events.size();Arrays.sort(ordered,0,size);
        var starts=workspace.starts;var ends=workspace.ends;var states=workspace.states;
        starts.clear();ends.clear();states.clear();
        int at=0,occupied=0,opaque=0,area=width*depth;
        while(at<size) {
            if((at&255)==0&&Thread.currentThread().isInterrupted())return null;
            int y=height(ordered[at]);
            do {
                long event=ordered[at++];int color=(int)(event>>>1),delta=(event&1)==1?1:-1;
                occupied+=delta;if(color>0)opaque+=delta;
                if(active.addTo(color,delta)+delta==0)active.remove(color);
            }while(at<size&&height(ordered[at])==y);
            if(at==size||occupied==0)continue;
            if(occupied!=area||opaque>0&&opaque<occupied)return null;
            int color=0,count=0;
            var entries=active.int2IntEntrySet().fastIterator();
            while(entries.hasNext()) {
                var entry=entries.next();
                int candidate=entry.getIntKey(),amount=entry.getIntValue();
                if(color==0||color<0&&candidate>0||(color>0)==(candidate>0)
                        &&(amount>count||amount==count&&Math.abs(candidate)<Math.abs(color))) {
                    color=candidate;count=amount;
                }
            }
            int end=height(ordered[at]),state=Math.abs(color),last=states.size()-1;
            if(last>=0&&states.getInt(last)==state&&ends.getShort(last)==y)ends.set(last,(short)end);
            else {starts.add((short)y);ends.add((short)end);states.add(state);}
        }
        return new Hk3WorldFarSurface(new int[]{0,states.size()},starts.toShortArray(),ends.toShortArray(),states.toIntArray());
    }

    private static long event(int y,int color,int entering) {
        return (long)(y-Short.MIN_VALUE)<<33|Integer.toUnsignedLong(color)<<1|entering;
    }

    private static int height(long event) {return (int)(event>>>33)+Short.MIN_VALUE;}
}
