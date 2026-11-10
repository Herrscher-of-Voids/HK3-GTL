package com.sirin.hk3gtl.common.multiblock.build;

import java.util.concurrent.*;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;

/** 后台仅解码不可变蓝图并排序；交接完成前独占蓝图，取消时由工作线程关闭输入。 */
final class Hk3BuildPreparation implements AutoCloseable {
    private static final ExecutorService WORKERS = new ThreadPoolExecutor(2, 2, 30, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(4), task -> {
                Thread thread = new Thread(task, "hk3gtl-blueprint");
                thread.setDaemon(true);
                thread.setPriority(Thread.NORM_PRIORITY - 1);
                return thread;
            }, new ThreadPoolExecutor.AbortPolicy());
    private final CompletableFuture<Hk3BuildOrder> result = new CompletableFuture<>();
    private volatile boolean cancelled, sorting;
    private volatile int decoded;

    Hk3BuildPreparation(BooleanSupplier prepare, Supplier<Hk3BuildOrder> order, Runnable cleanup) {
        WORKERS.execute(() -> run(prepare, order, cleanup));
    }

    private void run(BooleanSupplier prepare, Supplier<Hk3BuildOrder> factory, Runnable cleanup) {
        Hk3BuildOrder order = null;
        Throwable failure = null;
        try {
            boolean ready = false;
            while (!ready) {
                checkCancelled();
                ready = prepare.getAsBoolean();
                decoded++;
            }
            checkCancelled();
            sorting = true;
            order = factory.get();
            while (!order.step()) checkCancelled();
            checkCancelled();
        } catch (Throwable error) { failure = error; }
        finally {
            try { cleanup.run(); }
            catch (Throwable error) { if (failure == null) failure = error; else failure.addSuppressed(error); }
        }
        if (failure == null) result.complete(order); else result.completeExceptionally(failure);
    }

    private void checkCancelled() { if (cancelled) throw new CancellationException("蓝图准备已取消"); }
    boolean done() { return result.isDone(); }
    Hk3BuildOrder finish() { return result.join(); }
    String progress(int size) { return sorting ? "后台排序" : "后台解码 " + Math.min(decoded, size) + "/" + size; }
    @Override public void close() { cancelled = true; }
}
