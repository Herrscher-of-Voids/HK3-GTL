package com.sirin.hk3gtl.common.farview;

import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.PrimitiveIterator;
import java.util.function.BooleanSupplier;
import java.util.function.LongSupplier;
import java.util.function.Predicate;

/** 所有机器共用预算；缺区块只暂停当前任务，不在同一tick忙等。 */
public final class Hk3FarViewCaptureQueue {
    public enum Step { CONTINUE, WAIT, DONE }
    public interface Task {
        boolean valid();
        Step step();
        default void close() {}
        default void failed(RuntimeException failure) {}
    }
    @FunctionalInterface public interface Reader<S> { S read(long position); }
    @FunctionalInterface public interface Sink<S> { void observe(long position, S actual); }

    private static final class Entry {
        final Object key;
        final Task task;
        long waiting = Long.MIN_VALUE;
        Entry(Object key, Task task) { this.key = key; this.task = task; }
    }
    private final Map<Object, Entry> tasks = new HashMap<>();
    private final ArrayDeque<Entry> order = new ArrayDeque<>();
    private long tick;

    /** 同一控制器的新成型代替旧游标；只保留每个已加载控制器的一项轻量任务。 */
    public boolean add(Object key, Task task) {
        var old = tasks.get(key);
        if (old != null && old.task == task) return false;
        cancel(key);
        var entry = new Entry(key, task);
        tasks.put(key, entry); order.addLast(entry);
        return true;
    }

    public int size() { return tasks.size(); }
    public void cancel(Object key) {
        var entry = tasks.remove(key);
        if (entry != null) { order.remove(entry); close(entry, null); }
    }
    public void cancelIf(Predicate<Object> keys) {
        for (Object key : tasks.keySet().toArray()) if (keys.test(key)) cancel(key);
    }
    public void clear() {
        while (!order.isEmpty()) {
            var entry = order.removeFirst(); tasks.remove(entry.key); close(entry, null);
        }
    }

    public void tick(long deadline, int maxSteps, LongSupplier clock) {
        long currentTick = ++tick;
        int runnable = order.size();
        for (int steps = 0; runnable > 0 && steps < maxSteps && clock.getAsLong() < deadline;) {
            var entry = order.removeFirst();
            if (entry.waiting == currentTick) { order.addLast(entry); continue; }
            steps++;
            try {
                if (!entry.task.valid()) {
                    tasks.remove(entry.key); runnable--; close(entry, null); continue;
                }
                Step result = Objects.requireNonNull(entry.task.step());
                if (result == Step.DONE) {
                    tasks.remove(entry.key); runnable--; close(entry, null);
                } else {
                    if (result == Step.WAIT) { entry.waiting = currentTick; runnable--; }
                    order.addLast(entry);
                }
            } catch (RuntimeException failure) {
                tasks.remove(entry.key); runnable--; close(entry, failure);
            }
        }
    }

    private static void close(Entry entry, RuntimeException failure) {
        if (failure != null) try { entry.task.failed(failure); } catch (RuntimeException ignored) {}
        try { entry.task.close(); } catch (RuntimeException cleanup) {
            if (failure == null) try { entry.task.failed(cleanup); } catch (RuntimeException ignored) {}
        }
    }

    /** reader只返回已加载区块的实际状态；null保留同一坐标，不能当成空气或蓝图状态。 */
    public static <S> Task capture(BooleanSupplier valid, PrimitiveIterator.OfLong positions,
                                   Reader<S> reader, Sink<S> sink) {
        return new Task() {
            private long position;
            private boolean pending;
            @Override public boolean valid() { return valid.getAsBoolean(); }
            @Override public Step step() {
                if (!pending) {
                    if (!positions.hasNext()) return Step.DONE;
                    position = positions.nextLong(); pending = true;
                }
                S actual = reader.read(position);
                if (actual == null) return Step.WAIT;
                sink.observe(position, actual); pending = false;
                return positions.hasNext() ? Step.CONTINUE : Step.DONE;
            }
        };
    }
}
