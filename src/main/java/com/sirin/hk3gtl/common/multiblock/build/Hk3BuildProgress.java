package com.sirin.hk3gtl.common.multiblock.build;

import java.util.function.IntConsumer;

/** 每项任务只发布10%至100%的十个进度节点；暂停和重试不重置。 */
final class Hk3BuildProgress {
    private int next=10;
    static int percent(int completed,int size) { return (int)Math.min(100,completed*100L/size); }
    void report(int completed,int size,IntConsumer publish) {
        int percent=percent(completed,size);
        while(next<=percent) { int value=next;next+=10;publish.accept(value); }
    }
}
