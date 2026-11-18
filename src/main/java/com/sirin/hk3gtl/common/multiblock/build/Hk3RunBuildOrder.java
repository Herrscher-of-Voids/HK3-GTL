package com.sirin.hk3gtl.common.multiblock.build;

import it.unimi.dsi.fastutil.longs.LongArrays;

import java.util.concurrent.CompletableFuture;
import java.util.function.IntUnaryOperator;

/** W11只排列游程，按世界区块边界拆段后继续逐格搭建和核验。 */
final class Hk3RunBuildOrder {
    private final Hk3W11BuildPlan plan;
    private final IntUnaryOperator yAt,phaseAt,chunkAt;
    private final int height,minY,chunkCount;
    private long[] keys,fragments;
    private CompletableFuture<Void> sorting;
    private final ThreadLocal<int[]> lookup=ThreadLocal.withInitial(()->new int[]{0,-1,-1,-1,0});
    private int cursor,fragmentCount,filled,total;
    private Stage stage=Stage.COUNT;

    Hk3RunBuildOrder(Hk3W11BuildPlan plan,int height,int minY,IntUnaryOperator yAt,
                      IntUnaryOperator phaseAt,int chunkCount,IntUnaryOperator chunkAt) {
        this.plan=plan;this.height=height;this.minY=minY;this.yAt=yAt;
        this.phaseAt=phaseAt;this.chunkCount=chunkCount;this.chunkAt=chunkAt;
    }

    boolean step() {
        switch(stage) {
            case COUNT -> {
                int first=plan.runStart(cursor),length=plan.runLength(cursor);
                fragmentCount+=chunkAt.applyAsInt(first)==chunkAt.applyAsInt(first+length-1)?1:2;
                if(++cursor==plan.runCount()) {
                    keys=new long[fragmentCount];fragments=new long[fragmentCount];cursor=0;stage=Stage.FILL;
                }
            }
            case FILL -> {
                int first=plan.runStart(cursor),length=plan.runLength(cursor);
                int chunk=chunkAt.applyAsInt(first),split=length;
                if(chunk!=chunkAt.applyAsInt(first+length-1)) {
                    int low=1,high=length;
                    while(low<high) {
                        int mid=(low+high)>>>1;
                        if(chunkAt.applyAsInt(first+mid)==chunk)low=mid+1;else high=mid;
                    }
                    split=low;
                }
                add(first,split,chunk);
                if(split<length)add(first+split,length-split,chunkAt.applyAsInt(first+split));
                if(++cursor==plan.runCount()) {
                    sorting=CompletableFuture.runAsync(()->LongArrays.quickSort(keys,fragments));
                    cursor=0;stage=Stage.SORT;
                }
            }
            case SORT -> {
                if(!sorting.isDone())return false;
                sorting.join();sorting=null;stage=Stage.PREFIX;
            }
            case PREFIX -> {
                int group=(int)(keys[cursor]/height);
                total+=length(cursor);
                keys[cursor]=((long)total<<32)|Integer.toUnsignedLong(group);
                if(++cursor==fragmentCount)stage=Stage.DONE;
            }
            case DONE -> {}
        }
        return stage==Stage.DONE;
    }

    private void add(int first,int length,int chunk) {
        long group=(long)phaseAt.applyAsInt(first)*chunkCount+chunk;
        keys[filled]=group*height+yAt.applyAsInt(first)-minY;
        fragments[filled++]=((long)first<<5)|(length-1);
    }
    int index(int sortedIndex) {
        int run=fragmentAt(sortedIndex),start=run==0?0:end(run-1);
        return (int)(fragments[run]>>>5)+sortedIndex-start;
    }
    int nextChunkIndex(int sortedIndex) {
        int run=fragmentAt(sortedIndex),group=(int)keys[run],low=run+1,high=fragmentCount;
        int[] cached=lookup.get();
        if(cached[3]==group)return cached[4];
        while(low<high) {
            int mid=(low+high)>>>1;
            if((int)keys[mid]==group)low=mid+1;else high=mid;
        }
        cached[3]=group;cached[4]=end(low-1);
        return cached[4];
    }
    private int fragmentAt(int index) {
        int[] cached=lookup.get();
        if(index>=cached[1]&&index<cached[2])return cached[0];
        int low=0,high=fragmentCount;
        while(low<high) {
            int mid=(low+high)>>>1;
            if(end(mid)<=index)low=mid+1;else high=mid;
        }
        cached[0]=low;cached[1]=low==0?0:end(low-1);cached[2]=end(low);
        return low;
    }
    private int length(int run){return (int)(fragments[run]&31)+1;}
    private int end(int run){return (int)(keys[run]>>>32);}
    private enum Stage {COUNT,FILL,SORT,PREFIX,DONE}
}
