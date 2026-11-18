package com.sirin.hk3gtl.common.integration.ae;

import java.util.Set;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Future;
import java.util.concurrent.FutureTask;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/** 只限制同时规划的资源；计划、投料和执行仍由AE及底包处理。 */
public final class Hk3AePlanningQueue implements AutoCloseable {
    public record Limits(int workers, int queued) {}

    private final Object lifecycle = new Object();
    private final Set<PlanningTask<?>> pending = ConcurrentHashMap.newKeySet();
    private final ThreadPoolExecutor executor;
    private final int maxPending;
    private boolean accepting = true;

    public Hk3AePlanningQueue(int workers, int queued) {
        if (workers < 1 || queued < 1) throw new IllegalArgumentException("AE规划容量必须为正数");
        maxPending = workers + queued;
        AtomicInteger sequence = new AtomicInteger();
        executor = new ThreadPoolExecutor(workers, workers, 30, TimeUnit.SECONDS,
                new ArrayBlockingQueue<>(queued), task -> {
                    Thread thread = new Thread(task, "HK3-AE-Planning-" + sequence.incrementAndGet());
                    thread.setDaemon(true);
                    return thread;
                }, new ThreadPoolExecutor.AbortPolicy());
        executor.allowCoreThreadTimeOut(true);
    }

    /** 保守准入启发式，不是单任务或JVM总内存硬限制。 */
    public static Limits limits(int processors, long heapBytes) {
        int cpu = Math.max(1, processors / 2);
        int memory = (int) Math.max(1L, Math.min(4L, heapBytes / (1024L * 1024 * 1024)));
        int workers = Math.min(4, Math.min(cpu, memory));
        return new Limits(workers, workers * 2);
    }

    public <T> Future<T> submit(Callable<T> calculation) {
        PlanningTask<T> task = new PlanningTask<>(calculation);
        // 登记与入队必须和停机互斥，防止取消后又把旧任务放回队列。
        synchronized (lifecycle) {
            if (!accepting) {
                task.fail(new RejectedExecutionException("AE规划服务已停止"));
                return task;
            }
            pending.add(task);
            try {
                executor.execute(task);
            } catch (RejectedExecutionException busy) {
                task.fail(new RejectedExecutionException("AE规划队列已满，请稍后重试", busy));
            }
        }
        return task;
    }

    public boolean hasCapacity() {
        return hasCapacity(0);
    }

    public boolean hasCapacity(int collecting) {
        synchronized (lifecycle) {
            return accepting && pending.size() + collecting < maxPending;
        }
    }

    @Override
    public void close() {
        synchronized (lifecycle) {
            if (!accepting) return;
            accepting = false;
            for (PlanningTask<?> task : pending.toArray(PlanningTask<?>[]::new)) task.cancel(true);
            executor.shutdownNow();
        }
    }

    int queuedTasks() { return executor.getQueue().size(); }
    int pendingTasks() { return pending.size(); }

    private final class PlanningTask<T> extends FutureTask<T> {
        private PlanningTask(Callable<T> calculation) { super(calculation); }
        private void fail(Throwable failure) { setException(failure); }

        @Override
        protected void done() {
            // FutureTask清理Callable；同时解除我们新增的队列和登记引用。
            executor.remove(this);
            pending.remove(this);
        }
    }
}
