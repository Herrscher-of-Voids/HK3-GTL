package com.sirin.hk3gtl.client.farview;

import java.util.*;
import java.util.function.LongSupplier;

/** 只遍历到达事件登记的脏分区；完成后才发布，取消不撤销已发布快照。 */
public final class Hk3WorldFarSampler {
    public interface Source {
        boolean valid();
        int sections();
        boolean empty(int section);
        int state(int section,int index);
        void publish(int section,Hk3WorldFarCache.Packed snapshot);
    }
    private static final class Pending {
        final Source source;
        final BitSet dirty=new BitSet();
        int next;
        Pending(Source source){this.source=source;}
    }
    private final LinkedHashMap<Long,Pending> pending=new LinkedHashMap<>();
    private final int limit;
    private Pending reading;
    private long readingKey;
    private int section,cursor;
    private int[] cells;
    public Hk3WorldFarSampler(int limit){
        if(limit<1)throw new IllegalArgumentException("世界远景排队限额必须为正数");this.limit=limit;
    }
    public int pending(){return pending.size();}
    public void add(long key,Source source){
        remove(key);var job=new Pending(source);job.dirty.set(0,source.sections());put(key,job);
    }
    public void changed(long key,int section,Source source){
        if(section<0||section>=source.sections())return;
        var job=pending.get(key);if(job==null){job=new Pending(source);put(key,job);}job.dirty.set(section);
    }
    private void put(long key,Pending job){
        pending.put(key,job);
        while(pending.size()>limit)remove(pending.keySet().iterator().next());
    }
    public void remove(long key){pending.remove(key);if(reading!=null&&readingKey==key)discard();}
    public void clear(){pending.clear();discard();}
    private void discard(){reading=null;cells=null;cursor=0;}
    public void tick(long deadline,int maxCells,int maxSections,LongSupplier clock){
        int sampled=0,completed=0;
        while(sampled<maxCells&&completed<maxSections&&clock.getAsLong()<deadline){
            if(reading==null){
                if(pending.isEmpty())return;
                var entry=pending.entrySet().iterator().next();var job=entry.getValue();int next=job.dirty.nextSetBit(job.next);
                if(next<0)next=job.dirty.nextSetBit(0);
                if(!job.source.valid()||next<0){pending.remove(entry.getKey());continue;}
                reading=job;readingKey=entry.getKey();section=next;job.dirty.clear(next);job.next=(next+1)%job.source.sections();cursor=0;
                if(!job.source.empty(section))cells=new int[Hk3WorldFarCache.CELLS];
            }
            if(!reading.source.valid()){remove(readingKey);continue;}
            if(cells!=null){
                int stop=Math.min(Hk3WorldFarCache.CELLS,Math.min(cursor+64,cursor+maxCells-sampled));
                for(;cursor<stop;cursor++,sampled++)cells[cursor]=reading.source.state(section,cursor);
                if(cursor<Hk3WorldFarCache.CELLS)continue;
            }
            var snapshot=cells==null?Hk3WorldFarCache.Packed.air():Hk3WorldFarCache.Packed.encode(cells);
            reading.source.publish(section,snapshot);
            if(pending.get(readingKey)==reading){
                pending.remove(readingKey);if(!reading.dirty.isEmpty())pending.put(readingKey,reading);
            }
            discard();completed++;
        }
    }
}
