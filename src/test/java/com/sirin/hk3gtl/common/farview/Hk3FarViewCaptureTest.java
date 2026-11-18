package com.sirin.hk3gtl.common.farview;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.LongStream;

/** 实际执行生产捕获队列；世界接线仍须另行实机验收。 */
public final class Hk3FarViewCaptureTest {
    private static int checks;

    public static void main(String[] args) {
        actualReadAndFullDelivery();
        sharedBudgetsAndFairness();
        unloadedPositionResumes();
        duplicateReplacementAndLoadedMachineCount();
        invalidationUnloadAndStop();
        exceptionIsolation();
        System.out.println("原生远景捕获：" + checks + "项检查通过；覆盖实读、完整交付、全局预算、公平轮转、缺块恢复、去重清理与异常隔离，未执行客户端验收。");
    }

    private static void actualReadAndFullDelivery() {
        var queue = new Hk3FarViewCaptureQueue();
        var section = new Hk3FarSection();
        var reads = new AtomicInteger();
        var writes = new AtomicInteger();
        int[] actual = new int[Hk3FarMesh.COUNT];
        for (int i = 0; i < actual.length; i++) actual[i] = i % 19 + 1;
        actual[9] = 0;
        var task = new Watched(Hk3FarViewCaptureQueue.capture(() -> true,
                LongStream.range(0, actual.length).iterator(), pos -> {
                    reads.incrementAndGet();
                    return actual[(int) pos];
                }, (pos, state) -> {
                    writes.incrementAndGet();
                    section.set((int) pos, state);
                }));
        check(queue.add("overworld:actual", task), "真实捕获任务应可登记");
        check(reads.get() == 0 && writes.get() == 0, "登记时不得同步扫描或预填蓝图");
        queue.tick(Long.MAX_VALUE, 1, () -> 0L);
        check(reads.get() == 1 && section.state(0) == 1, "单步必须读取并交付真实状态");
        actual[1] = 71;
        int ticks = 0;
        while (queue.size() != 0 && ticks++ < 100) {
            int before = reads.get();
            queue.tick(Long.MAX_VALUE, 64, () -> 0L);
            check(reads.get() - before <= 64, "每tick不得突破读取预算");
        }
        check(queue.size() == 0 && reads.get() == actual.length && writes.get() == actual.length,
                "跨tick捕获必须逐格完整交付且没有重复读取");
        for (int i = 0; i < actual.length; i++) {
            check(section.state(i) == actual[i], "交付内容必须等于采样时实际方块，不能替换成蓝图");
        }
        check(section.state(1) == 71 && section.state(9) == 0,
                "排队后改变的实际方块及空气必须交付给写入器");
        check(task.closed == 1 && task.failed == 0, "正常结束只释放一次游标");

        var empty = new Watched(Hk3FarViewCaptureQueue.capture(() -> true,
                LongStream.empty().iterator(), pos -> 1, (pos, state) -> {
                    throw new AssertionError("空游标不得写入");
                }));
        check(queue.add("empty", empty), "空捕获可安全排队");
        queue.tick(Long.MAX_VALUE, 1, () -> 0L);
        check(queue.size() == 0 && empty.closed == 1, "空游标必须结束并释放");
    }

    private static void sharedBudgetsAndFairness() {
        var queue = new Hk3FarViewCaptureQueue();
        List<String> order = new ArrayList<>();
        var overworld = new Probe("overworld", 10, order);
        var nether = new Probe("nether", 10, order);
        queue.add("overworld:7", overworld);
        queue.add("nether:7", nether);
        for (int i = 0; i < 4; i++) queue.tick(Long.MAX_VALUE, 1, () -> 0L);
        check(order.equals(List.of("overworld", "nether", "overworld", "nether")),
                "不同维度任务必须共用预算并跨tick公平轮转");
        queue.tick(Long.MAX_VALUE, 3, () -> 0L);
        check(order.size() == 7 && Math.abs(overworld.steps - nether.steps) <= 1,
                "总步数预算不可按任务或维度分别重复分配");
        queue.tick(Long.MAX_VALUE, 0, () -> 0L);
        queue.tick(0, 100, () -> 0L);
        check(order.size() == 7, "零步数或过期时间预算不得执行读取");
        queue.clear();

        var clock = new AtomicLong();
        var timed = new AtomicInteger();
        queue.add("timed", new Hk3FarViewCaptureQueue.Task() {
            public boolean valid() { return true; }
            public Hk3FarViewCaptureQueue.Step step() {
                timed.incrementAndGet();
                clock.addAndGet(5);
                return Hk3FarViewCaptureQueue.Step.CONTINUE;
            }
        });
        queue.tick(7, 100, clock::get);
        check(timed.get() == 2 && clock.get() == 10, "到期后不得启动下一个采样步骤");
        queue.tick(10, 100, clock::get);
        check(timed.get() == 2, "前一tick用尽时间后不得漏做一步");
        queue.clear();
    }

    private static void unloadedPositionResumes() {
        var queue = new Hk3FarViewCaptureQueue();
        Map<Long, Integer> loaded = new HashMap<>();
        loaded.put(2L, 22);
        List<Long> attempted = new ArrayList<>();
        Map<Long, Integer> delivered = new HashMap<>();
        var missing = new Watched(Hk3FarViewCaptureQueue.capture(() -> true,
                LongStream.of(1, 2).iterator(), pos -> {
                    attempted.add(pos);
                    return loaded.get(pos);
                }, delivered::put));
        List<String> order = new ArrayList<>();
        var healthy = new Probe("healthy", 3, order);
        queue.add("overworld:missing", missing);
        queue.add("nether:healthy", healthy);
        queue.tick(Long.MAX_VALUE, 100, () -> 0L);
        check(attempted.equals(List.of(1L)) && delivered.isEmpty(),
                "缺区块同tick只能尝试一次，不能跳格、伪造或写入未加载状态");
        check(healthy.steps == 3 && healthy.closed == 1 && queue.size() == 1,
                "缺区块等待不得阻塞其他机器或维度");
        queue.tick(Long.MAX_VALUE, 100, () -> 0L);
        check(attempted.equals(List.of(1L, 1L)) && queue.size() == 1,
                "持续未加载任务必须保留，并且每tick最多重试一次");
        loaded.put(1L, 81);
        queue.tick(Long.MAX_VALUE, 100, () -> 0L);
        check(delivered.equals(Map.of(1L, 81, 2L, 22)) && queue.size() == 0,
                "区块恢复后必须从原坐标继续，完整交付实际状态");
        check(attempted.equals(List.of(1L, 1L, 1L, 2L)) && missing.closed == 1,
                "恢复不得重读已完成坐标或遗留任务");

        var retries = new AtomicInteger();
        var budgeted = new Probe("budgeted", 2, new ArrayList<>());
        queue.add("waiting", Hk3FarViewCaptureQueue.<Integer>capture(() -> true,
                LongStream.of(7).iterator(), pos -> { retries.incrementAndGet(); return null; },
                (pos, state) -> { throw new AssertionError("缺区块不得写入"); }));
        queue.add("budgeted", budgeted);
        queue.tick(Long.MAX_VALUE, 1, () -> 0L);
        check(retries.get() == 1 && budgeted.steps == 0, "WAIT尝试也必须计入全局步数预算");
        queue.tick(Long.MAX_VALUE, 1, () -> 0L);
        check(retries.get() == 1 && budgeted.steps == 1, "单步预算下等待任务不能饿死其他任务");
        queue.clear();
    }

    private static void duplicateReplacementAndLoadedMachineCount() {
        var queue = new Hk3FarViewCaptureQueue();
        var current = new AtomicBoolean(true);
        List<Long> oldReads = new ArrayList<>();
        var oldGeneration = new Watched(Hk3FarViewCaptureQueue.capture(current::get,
                LongStream.range(0, 5).iterator(), pos -> { oldReads.add(pos); return 11; },
                (pos, state) -> {}));
        check(queue.add("machine", oldGeneration) && !queue.add("machine", oldGeneration),
                "同任务实例重复登记不得重启、移位或释放原游标");
        queue.tick(Long.MAX_VALUE, 1, () -> 0L);
        check(oldReads.equals(List.of(0L)) && oldGeneration.closed == 0,
                "替换前必须真实执行过旧generation，避免只测空队列");
        current.set(false);
        Map<Long, Integer> newData = new HashMap<>();
        var newGeneration = new Watched(Hk3FarViewCaptureQueue.capture(() -> true,
                LongStream.range(100, 105).iterator(), pos -> (int) pos + 700, newData::put));
        check(queue.add("machine", newGeneration) && queue.size() == 1 && oldGeneration.closed == 1,
                "同主控新generation必须替换旧游标，不能被重复key永久丢弃");
        check(!queue.add("machine", newGeneration) && newGeneration.closed == 0,
                "新generation自身重复登记也不可释放或重启");
        queue.tick(Long.MAX_VALUE, 100, () -> 0L);
        check(newData.equals(Map.of(100L, 800, 101L, 801, 102L, 802, 103L, 803, 104L, 804))
                        && oldReads.equals(List.of(0L)) && queue.size() == 0,
                "换cache后的新坐标必须完整采样，旧generation不得继续读取");
        check(oldGeneration.closed == 1 && newGeneration.closed == 1,
                "被替换及完成的generation各释放一次");

        List<Probe> machines = new ArrayList<>();
        List<String> order = new ArrayList<>();
        for (int i = 0; i < 128; i++) {
            var machine = new Probe("machine:" + i, 2, order);
            machines.add(machine);
            check(queue.add("machine:" + i, machine), "第65台及以后的已加载机器不得被静默丢弃");
        }
        check(queue.size() == 128, "登记规模超过旧64台限制时必须全部保留");
        int ticks = 0;
        while (queue.size() != 0 && ticks++ < 100) {
            int before = order.size();
            queue.tick(Long.MAX_VALUE, 7, () -> 0L);
            check(order.size() - before <= 7, "128台机器仍只能共用原单tick预算");
        }
        check(queue.size() == 0 && order.size() == 256, "超过64台的全部任务必须最终交付，不能永久漏采");
        for (var machine : machines) check(machine.steps == 2 && machine.closed == 1,
                "大队列每台机器均须完整执行并释放一次");

        var canceled = new Probe("cancel", 1, new ArrayList<>());
        queue.add("machine", canceled);
        queue.cancel("machine");
        queue.cancel("machine");
        check(queue.size() == 0 && canceled.closed == 1 && canceled.steps == 0,
                "取消与重复取消只释放一次且不能再采样");
    }

    private static void invalidationUnloadAndStop() {
        var queue = new Hk3FarViewCaptureQueue();
        var alive = new AtomicBoolean(true);
        var reads = new AtomicInteger();
        var capture = new Watched(Hk3FarViewCaptureQueue.capture(alive::get,
                LongStream.range(0, 20).iterator(), pos -> reads.incrementAndGet(), (pos, state) -> {}));
        queue.add("formed", capture);
        queue.tick(Long.MAX_VALUE, 1, () -> 0L);
        alive.set(false);
        queue.tick(Long.MAX_VALUE, 100, () -> 0L);
        check(reads.get() == 1 && queue.size() == 0 && capture.closed == 1,
                "有效性回调失效后必须停止后续采样并释放游标");

        var unloaded = new Probe("unloaded", 4, new ArrayList<>());
        var retained = new Probe("retained", 4, new ArrayList<>());
        var sameLevel = new Probe("sameLevel", 4, new ArrayList<>());
        queue.add("overworld:a", unloaded);
        queue.add("nether:b", retained);
        queue.add("overworld:c", sameLevel);
        queue.cancelIf(key -> key.toString().startsWith("overworld:"));
        check(unloaded.closed == 1 && sameLevel.closed == 1 && retained.closed == 0 && queue.size() == 1,
                "维度卸载只清理对应任务，其他维度必须保留");
        queue.cancel("nether:b");
        check(retained.closed == 1 && retained.steps == 0 && queue.size() == 0,
                "主控卸载取消后不可再读取世界");

        var stoppedA = new Probe("a", 20, new ArrayList<>());
        var stoppedB = new Probe("b", 20, new ArrayList<>());
        queue.add("overworld:a", stoppedA);
        queue.add("nether:b", stoppedB);
        queue.clear();
        queue.clear();
        queue.tick(Long.MAX_VALUE, 100, () -> 0L);
        check(queue.size() == 0 && stoppedA.closed == 1 && stoppedB.closed == 1
                        && stoppedA.steps == 0 && stoppedB.steps == 0,
                "服务器停止必须清空所有维度游标，重复停止不得二次释放");
    }

    private static void exceptionIsolation() {
        for (String phase : List.of("valid", "step", "reader", "sink", "failed", "close")) {
            var queue = new Hk3FarViewCaptureQueue();
            var closeCount = new AtomicInteger();
            var failureCount = new AtomicInteger();
            Hk3FarViewCaptureQueue.Task captured = Hk3FarViewCaptureQueue.capture(() -> true,
                    LongStream.of(3).iterator(), pos -> {
                        if (phase.equals("reader")) throw new IllegalStateException("读取异常");
                        return 42;
                    }, (pos, state) -> {
                        if (phase.equals("sink")) throw new IllegalStateException("写入异常");
                    });
            queue.add("bad:" + phase, new Hk3FarViewCaptureQueue.Task() {
                public boolean valid() {
                    if (phase.equals("valid")) throw new IllegalStateException("有效性异常");
                    return true;
                }
                public Hk3FarViewCaptureQueue.Step step() {
                    if (phase.equals("step") || phase.equals("failed")) throw new IllegalStateException("步骤异常");
                    return captured.step();
                }
                public void failed(RuntimeException exception) {
                    failureCount.incrementAndGet();
                    if (phase.equals("failed")) throw new IllegalStateException("异常通知再失败");
                }
                public void close() {
                    closeCount.incrementAndGet();
                    if (phase.equals("close")) throw new IllegalStateException("释放异常");
                }
            });
            var healthy = new Probe("healthy", 3, new ArrayList<>());
            queue.add("healthy", healthy);
            queue.tick(Long.MAX_VALUE, 100, () -> 0L);
            queue.clear();
            check(queue.size() == 0 && healthy.steps == 3 && healthy.closed == 1,
                    phase + "异常不得打断其它机器或遗留失败任务");
            check(closeCount.get() == 1, phase + "异常任务只能释放一次");
            if (!phase.equals("close")) check(failureCount.get() == 1, phase + "失败必须通知一次");
        }

        var queue = new Hk3FarViewCaptureQueue();
        var released = new AtomicInteger();
        queue.add("cancel-close", new Hk3FarViewCaptureQueue.Task() {
            public boolean valid() { return true; }
            public Hk3FarViewCaptureQueue.Step step() { return Hk3FarViewCaptureQueue.Step.CONTINUE; }
            public void close() { released.incrementAndGet(); throw new IllegalStateException("取消释放失败"); }
        });
        queue.cancel("cancel-close");
        queue.clear();
        check(queue.size() == 0 && released.get() == 1, "取消清理异常也必须隔离且不得重复释放");
    }

    private static final class Watched implements Hk3FarViewCaptureQueue.Task {
        private final Hk3FarViewCaptureQueue.Task delegate;
        int closed;
        int failed;
        Watched(Hk3FarViewCaptureQueue.Task delegate) { this.delegate = delegate; }
        public boolean valid() { return delegate.valid(); }
        public Hk3FarViewCaptureQueue.Step step() { return delegate.step(); }
        public void close() { closed++; delegate.close(); }
        public void failed(RuntimeException exception) { failed++; delegate.failed(exception); }
    }

    private static final class Probe implements Hk3FarViewCaptureQueue.Task {
        private final String label;
        private final int limit;
        private final List<String> order;
        int steps;
        int closed;
        Probe(String label, int limit, List<String> order) {
            this.label = label;
            this.limit = limit;
            this.order = order;
        }
        public boolean valid() { return true; }
        public Hk3FarViewCaptureQueue.Step step() {
            order.add(label);
            steps++;
            return steps >= limit ? Hk3FarViewCaptureQueue.Step.DONE : Hk3FarViewCaptureQueue.Step.CONTINUE;
        }
        public void close() { closed++; }
    }

    private static void check(boolean value, String message) {
        checks++;
        if (!value) throw new AssertionError(message);
    }
}
