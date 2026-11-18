package com.sirin.hk3gtl.common.integration.ae;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BooleanSupplier;

/** 无MC世界的真实线程回归，不代表实际Mixin或FCL性能验收。 */
public final class Hk3AePlanningQueueTest {
    private static int checks;

    public static void main(String[] args) throws Exception {
        limits();
        boundedAndCancelledQueue();
        failedAndInterrupted();
        stopRaces();
        System.out.println("AE规划队列离线核验通过：" + checks + "项；未启动游戏或测量帧率。");
    }

    private static void limits() {
        long gib = 1024L * 1024 * 1024;
        check(Hk3AePlanningQueue.limits(1, gib / 2).equals(new Hk3AePlanningQueue.Limits(1, 2)), "低堆单核边界");
        check(Hk3AePlanningQueue.limits(8, 2 * gib).equals(new Hk3AePlanningQueue.Limits(2, 4)), "堆准入限制");
        check(Hk3AePlanningQueue.limits(4, 8 * gib).equals(new Hk3AePlanningQueue.Limits(2, 4)), "CPU预留");
        check(Hk3AePlanningQueue.limits(Integer.MAX_VALUE, Long.MAX_VALUE).equals(new Hk3AePlanningQueue.Limits(4, 8)), "极端输入不溢出");
    }

    private static void boundedAndCancelledQueue() throws Exception {
        CountDownLatch entered = new CountDownLatch(2), release = new CountDownLatch(1);
        AtomicInteger active = new AtomicInteger(), peak = new AtomicInteger();
        AtomicBoolean ranOnCaller = new AtomicBoolean(), cancelledRan = new AtomicBoolean(), rejectedRan = new AtomicBoolean();
        Thread caller = Thread.currentThread();
        try (var queue = new Hk3AePlanningQueue(2, 2)) {
            List<Future<Integer>> running = new ArrayList<>();
            for (int i = 0; i < 2; i++) running.add(queue.submit(() -> {
                ranOnCaller.compareAndSet(false, Thread.currentThread() == caller);
                int count = active.incrementAndGet();
                peak.accumulateAndGet(count, Math::max);
                entered.countDown();
                try { release.await(); return 7; }
                finally { active.decrementAndGet(); }
            }));
            check(entered.await(5, TimeUnit.SECONDS), "并行任务实际开始");
            var cancelled = queue.submit(() -> { cancelledRan.set(true); return 99; });
            var retained = queue.submit(() -> 11);
            var rejected = queue.submit(() -> { rejectedRan.set(true); return 88; });
            expectFailure(rejected, RejectedExecutionException.class);
            check(queue.queuedTasks() == 2 && queue.pendingTasks() == 4, "队列与在途登记均有界");
            check(cancelled.cancel(true) && cancelled.isCancelled(), "排队任务可取消");
            check(queue.queuedTasks() == 1 && queue.pendingTasks() == 3, "取消立即解除两处引用");
            var replacement = queue.submit(() -> 13);
            check(!replacement.isDone() && queue.queuedTasks() == 2, "释放的队列槽可立即复用");
            release.countDown();
            for (var future : running) check(future.get(5, TimeUnit.SECONDS) == 7, "运行结果未改写");
            check(retained.get(5, TimeUnit.SECONDS) == 11 && replacement.get(5, TimeUnit.SECONDS) == 13, "排队结果完整");
            await(() -> queue.pendingTasks() == 0);
            check(peak.get() == 2 && !ranOnCaller.get(), "并发上限且不回退调用线程");
            check(!cancelledRan.get() && !rejectedRan.get(), "取消和拒绝不执行规划");
        } finally { release.countDown(); }
    }

    private static void failedAndInterrupted() throws Exception {
        CountDownLatch entered = new CountDownLatch(1), interrupted = new CountDownLatch(1);
        AtomicBoolean queuedRan = new AtomicBoolean();
        AtomicReference<Thread> worker = new AtomicReference<>();
        var queue = new Hk3AePlanningQueue(1, 1);
        try {
            var failure = queue.submit(() -> { throw new IllegalStateException("离线异常样本"); });
            expectFailure(failure, IllegalStateException.class);
            await(() -> queue.pendingTasks() == 0);
            var running = queue.submit(() -> {
                worker.set(Thread.currentThread());
                entered.countDown();
                try { new CountDownLatch(1).await(); return 0; }
                catch (InterruptedException stopped) { interrupted.countDown(); throw stopped; }
            });
            check(entered.await(5, TimeUnit.SECONDS), "运行取消样本已开始");
            var waiting = queue.submit(() -> { queuedRan.set(true); return 0; });
            queue.close();
            check(running.isCancelled() && waiting.isCancelled(), "关停同时取消运行和等待Future");
            check(interrupted.await(5, TimeUnit.SECONDS), "运行任务收到中断");
            worker.get().join(5000);
            check(!worker.get().isAlive(), "合作响应中断的工作线程实际退出");
            check(queue.queuedTasks() == 0 && queue.pendingTasks() == 0 && !queuedRan.get(), "关停不留等待引用");
            expectFailure(queue.submit(() -> 0), RejectedExecutionException.class);
            queue.close();
            check(queue.pendingTasks() == 0, "重复关停幂等");
        } finally { queue.close(); }
    }

    private static void stopRaces() throws Exception {
        for (int round = 0; round < 20; round++) {
            var queue = new Hk3AePlanningQueue(1, 2);
            CountDownLatch start = new CountDownLatch(1);
            List<Future<Integer>> futures = new ArrayList<>();
            AtomicReference<Throwable> producerFailure = new AtomicReference<>();
            Thread producer = new Thread(() -> {
                try {
                    start.await();
                    for (int i = 0; i < 16; i++) futures.add(queue.submit(() -> 1));
                } catch (Throwable failure) { producerFailure.set(failure); }
            });
            producer.start();
            start.countDown();
            queue.close();
            producer.join(5000);
            check(!producer.isAlive(), "提交与停机不死锁");
            if (producerFailure.get() != null) throw new AssertionError("提交线程异常", producerFailure.get());
            check(futures.size() == 16, "提交线程完成全部请求");
            for (var future : futures) check(future.isDone(), "竞态下所有Future可终结");
            check(queue.queuedTasks() == 0 && queue.pendingTasks() == 0, "停机后不得重新入队");
        }
    }

    private static void expectFailure(Future<?> future, Class<? extends Throwable> type) throws Exception {
        try { future.get(5, TimeUnit.SECONDS); throw new AssertionError("预期失败Future"); }
        catch (ExecutionException e) { check(type.isInstance(e.getCause()), "失败通过Future传递"); }
    }

    private static void await(BooleanSupplier condition) throws InterruptedException {
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
        while (!condition.getAsBoolean() && System.nanoTime() < deadline) Thread.sleep(1);
        check(condition.getAsBoolean(), "任务登记最终释放");
    }

    private static void check(boolean ok, String reason) {
        if (!ok) throw new AssertionError(reason);
        checks++;
    }
}
