package com.sirin.hk3gtl.common.multiblock.build;

import java.util.ArrayDeque;
import java.util.concurrent.*;
import java.util.function.IntFunction;

/** 有界并行准备批次；读取器只能使用已发布的蓝图，不能读取世界、库存或区块。 */
final class Hk3BuildPipeline<T> implements AutoCloseable {
    static final int BATCH_SIZE = 2048;
    static final int WORKER_COUNT = Math.max(1, Math.min(3, Runtime.getRuntime().availableProcessors() / 4));
    private static final ExecutorService WORKERS = new ThreadPoolExecutor(WORKER_COUNT, WORKER_COUNT,
            30, TimeUnit.SECONDS, new ArrayBlockingQueue<>(8), task -> {
                Thread thread = new Thread(task, "hk3gtl-build-batch");
                thread.setDaemon(true); thread.setPriority(Thread.NORM_PRIORITY - 1); return thread;
            }, new ThreadPoolExecutor.AbortPolicy());
    private final ArrayDeque<Future<Object[]>> pending = new ArrayDeque<>();
    private final IntFunction<T> read;
    private final ExecutorService workers;
    private final int size, window;
    private int scheduled, consumed, offset;
    private Object[] current;
    private boolean closed;

    Hk3BuildPipeline(int size, IntFunction<T> read) { this(size, read, WORKERS, WORKER_COUNT + 1); }
    Hk3BuildPipeline(int size, IntFunction<T> read, ExecutorService workers, int window) {
        if (size < 1 || window < 1) throw new IllegalArgumentException("并行批次数或实体数量无效");
        this.size=size; this.read=read; this.workers=workers; this.window=window;
    }
    private void refill() {
        while (!closed && scheduled < size && pending.size() < window) {
            int start=scheduled, count=Math.min(BATCH_SIZE,size-start);
            pending.add(workers.submit(() -> {
                Object[] batch=new Object[count];
                for(int i=0;i<count;i++) {
                    if(Thread.currentThread().isInterrupted()) throw new CancellationException("并行批次已取消");
                    batch[i]=java.util.Objects.requireNonNull(read.apply(start+i),"蓝图批次包含空实体");
                }
                return batch;
            }));
            scheduled+=count;
        }
    }
    @SuppressWarnings("unchecked") T peek() {
        if(closed || consumed==size) return null;
        refill();
        if(current==null) {
            Future<Object[]> head=pending.peek();
            if(head==null || !head.isDone()) return null;
            try { current=head.get(); }
            catch(InterruptedException failure) { Thread.currentThread().interrupt(); throw new CancellationException("批次交接被中断"); }
            catch(ExecutionException failure) { throw new CompletionException(failure.getCause()); }
            pending.remove(); offset=0; refill();
        }
        return (T)current[offset];
    }
    void advance() {
        if(current==null)throw new IllegalStateException("尚未收到可提交批次");
        current[offset++]=null; consumed++;
        if(offset==current.length)current=null;
    }
    int bufferedLimit() { return (window+1)*BATCH_SIZE; }
    @Override public void close() {
        closed=true; pending.forEach(task->task.cancel(true)); pending.clear(); current=null;
    }
}
