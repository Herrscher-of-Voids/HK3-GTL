package com.sirin.hk3gtl.client.farview;

import java.util.*;
import java.util.function.LongConsumer;

/** 会话内按游程保存实际读过的分区；字节与数量双限额，不持有真实区块。 */
public final class Hk3WorldFarCache {
    public static final int MAX_SECTIONS=2048,MAX_BYTES=8*1024*1024,CELLS=4096;
    public static final class Packed {
        private static final Packed AIR=new Packed(new short[]{4096},new int[]{0});
        private final short[] ends;
        private final int[] states;
        private Packed(short[] ends,int[] states){this.ends=ends;this.states=states;}
        public int state(int index){
            if(index<0||index>=CELLS)throw new IndexOutOfBoundsException(index);
            int at=Arrays.binarySearch(ends,(short)(index+1));
            return states[at>=0?at:-at-1];
        }
        public int bytes(){return 160+ends.length*2+states.length*4;}
        void unpack(int[] cells){
            int from=0;
            for(int run=0;run<ends.length;run++){
                int to=Short.toUnsignedInt(ends[run]);Arrays.fill(cells,from,to,states[run]);from=to;
            }
        }
        public boolean empty(){return states.length==1&&states[0]==0;}
        public boolean same(Packed other){return other!=null&&Arrays.equals(ends,other.ends)&&Arrays.equals(states,other.states);}
        public static Packed air(){return AIR;}
        public static Packed encode(int[] cells){
            if(cells.length!=CELLS)throw new IllegalArgumentException("世界远景分区必须为4096格");
            int runs=1;
            for(int i=0;i<CELLS;i++){
                if(cells[i]<0)throw new IllegalArgumentException("世界远景状态不能为负数");
                if(i>0&&cells[i]!=cells[i-1])runs++;
            }
            short[] ends=new short[runs];int[] states=new int[runs];int at=0;
            for(int i=1;i<=CELLS;i++)if(i==CELLS||cells[i]!=cells[i-1]){
                ends[at]=(short)i;states[at++]=cells[i-1];
            }
            return new Packed(ends,states);
        }
    }
    private final LinkedHashMap<Long,Packed> sections=new LinkedHashMap<>(16,.75f,true);
    private final int byteLimit,sectionLimit;
    private int bytes,nonempty;
    public Hk3WorldFarCache(){this(MAX_BYTES,MAX_SECTIONS);}
    public Hk3WorldFarCache(int byteLimit,int sectionLimit){
        if(byteLimit<1||sectionLimit<1)throw new IllegalArgumentException("世界远景限额必须为正数");
        this.byteLimit=byteLimit;this.sectionLimit=sectionLimit;
    }
    public Packed get(long key){return sections.get(key);}
    public int size(){return sections.size();}
    public int bytes(){return bytes;}
    public void put(long key,Packed value,LongConsumer removed){
        var previous=sections.remove(key);
        if(previous!=null){bytes-=previous.bytes();if(!previous.empty())nonempty--;}
        if(value.bytes()<=byteLimit){sections.put(key,value);bytes+=value.bytes();if(!value.empty())nonempty++;}
        else removed.accept(key);
        while(bytes>byteLimit||nonempty>sectionLimit){
            var iterator=sections.entrySet().iterator();var oldest=iterator.next();
            bytes-=oldest.getValue().bytes();if(!oldest.getValue().empty())nonempty--;
            long evicted=oldest.getKey();iterator.remove();removed.accept(evicted);
        }
    }
    public void clear(){sections.clear();bytes=nonempty=0;}
}
