package com.sirin.hk3gtl.common.machine;

import java.util.HashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 【变更记录 #1】2026-10-15 03:02:02（第1次备注 · 香港时间 · 内测5修订159）
 * 删除：无。新增：结构锁的真实双线程互斥、异常释放、立即尝试及重入回归。
 * 修改：测试直接调用生产锁边界，以共享非线程安全映射模拟同一控制器匹配缓存。
 * 用途：验证服务器直接匹配与后台尝试匹配不能同时改缓存；不创建游戏、世界或注册表。
 */
public final class Hk3PatternLockTest {
    public static void main(String[] args) throws Exception {
        ExecutorService workers = Executors.newFixedThreadPool(2);
        try {
            concurrentChecks(workers);
            nonBlockingTry(workers);
            exceptionRelease(workers);
            reentrantCalls(workers);
        } finally {
            workers.shutdownNow();
            check(workers.awaitTermination(3, TimeUnit.SECONDS), "测试线程未终止");
        }
        System.out.println("Hk3PatternLockTest passed: mutual exclusion, exception release, nonblocking try and reentrancy");
    }

    /** 两种入口从同一起点竞争，未加互斥时共享映射和同时进入计数会暴露错误。 */
    private static void concurrentChecks(ExecutorService workers) throws Exception {
        ReentrantLock lock = new ReentrantLock();
        CountDownLatch start = new CountDownLatch(1);
        AtomicInteger active = new AtomicInteger(), maximum = new AtomicInteger();
        HashMap<Integer, Integer> cache = new HashMap<>();
        int repeats = 2_000;
        var direct = workers.submit(() -> {
            await(start);
            for (int i = 0; i < repeats; i++) {
                int key = i;
                Hk3PatternLock.withLock(lock, () -> write(cache, active, maximum, key));
            }
        });
        var background = workers.submit(() -> {
            await(start);
            long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
            for (int i = 0; i < repeats;) {
                int key = i + repeats;
                if (Hk3PatternLock.tryCheck(lock, () -> write(cache, active, maximum, key))) i++;
                else {
                    check(System.nanoTime() < deadline, "后台检查一直无法取锁");
                    Thread.yield();
                }
            }
        });
        start.countDown();
        direct.get(6, TimeUnit.SECONDS);
        background.get(6, TimeUnit.SECONDS);
        check(maximum.get() == 1 && active.get() == 0, "同一控制器发生并发缓存写入");
        check(cache.size() == repeats * 2, "匹配缓存丢失写入");
        for (int i = 0; i < repeats * 2; i++) check(Integer.valueOf(i).equals(cache.get(i)), "匹配缓存内容损坏");
        check(!lock.isLocked(), "并发调用结束后残留锁");
    }

    private static boolean write(HashMap<Integer, Integer> cache, AtomicInteger active, AtomicInteger maximum, int key) {
        int simultaneous = active.incrementAndGet();
        maximum.accumulateAndGet(simultaneous, Math::max);
        try {
            Thread.yield();
            cache.put(key, key);
            return true;
        } finally {
            active.decrementAndGet();
        }
    }

    /** 主线程一直持有锁，后台调用必须在解锁前返回且不能执行正文。 */
    private static void nonBlockingTry(ExecutorService workers) throws Exception {
        ReentrantLock lock = new ReentrantLock();
        AtomicBoolean invoked = new AtomicBoolean();
        lock.lock();
        try {
            var attempt = workers.submit(() -> Hk3PatternLock.tryCheck(lock, () -> {
                invoked.set(true);
                return true;
            }));
            check(!attempt.get(1, TimeUnit.SECONDS), "尝试入口在锁竞争时错误返回成功");
            check(!invoked.get() && lock.getHoldCount() == 1, "尝试入口执行正文或改变他人锁归属");
        } finally {
            lock.unlock();
        }
    }

    /** 错误原样传播；随后另一个线程必须能立即取得锁，防止同线程重入掩盖泄漏。 */
    private static void exceptionRelease(ExecutorService workers) throws Exception {
        ReentrantLock lock = new ReentrantLock();
        for (boolean attempt : new boolean[] {false, true}) {
            for (boolean fatal : new boolean[] {false, true}) {
                Throwable expected = fatal ? new AssertionError("模拟匹配错误") : new IllegalStateException("模拟匹配异常");
                try {
                    if (attempt) Hk3PatternLock.tryCheck(lock, () -> fail(expected));
                    else Hk3PatternLock.withLock(lock, () -> fail(expected));
                    throw new AssertionError("匹配异常被吞掉");
                } catch (Throwable actual) {
                    check(actual == expected, "匹配异常未原样传播");
                }
                check(workers.submit(() -> Hk3PatternLock.tryCheck(lock, () -> true)).get(1, TimeUnit.SECONDS),
                        "匹配异常后锁没有释放");
                check(!lock.isLocked(), "异常释放回归残留锁");
            }
        }
    }

    /** 模拟GT已持锁再调用检查，以及朝向更新内部再次检查；只释放每层自有次数。 */
    private static void reentrantCalls(ExecutorService workers) throws Exception {
        ReentrantLock lock = new ReentrantLock();
        lock.lock();
        try {
            boolean result = Hk3PatternLock.withLock(lock, () -> Hk3PatternLock.tryCheck(lock, () ->
                    Hk3PatternLock.withLock(lock, () -> lock.getHoldCount() == 4)));
            check(result && lock.getHoldCount() == 1, "嵌套重入没有保持外层锁归属");
            check(!workers.submit(() -> Hk3PatternLock.tryCheck(lock, () -> true)).get(1, TimeUnit.SECONDS),
                    "嵌套调用错误释放GT外层锁");
        } finally {
            lock.unlock();
        }
        check(workers.submit(() -> Hk3PatternLock.tryCheck(lock, () -> true)).get(1, TimeUnit.SECONDS),
                "外层完成后没有释放锁");
    }

    private static boolean fail(Throwable expected) {
        if (expected instanceof Error error) throw error;
        throw (RuntimeException) expected;
    }

    private static void await(CountDownLatch latch) {
        try {
            check(latch.await(3, TimeUnit.SECONDS), "测试起点超时");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new AssertionError("测试线程中断", e);
        }
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
