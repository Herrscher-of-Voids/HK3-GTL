package com.sirin.hk3gtl.common.util;

import java.util.LinkedHashMap;
import java.util.function.Function;
import java.util.function.ToLongFunction;

/**
 * 【变更记录 #1】2026-09-27 23:52:00（内测5修订91）
 * 删除：无。新增：按估算字节限制的最近使用缓存，超大单项只返回而不常驻。
 * 修改：所有访问在同一锁内，防止重复加载和淘汰竞态；加载异常不写入缓存。
 * 用途：约束建筑数据常驻内存；只持有纯数据，不持有世界、玩家或显卡资源。
 */
public final class Hk3WeightedCache<K, V> {
    private record Entry<V>(V value, long bytes) {}
    private final long limit;
    private final ToLongFunction<V> weight;
    private final LinkedHashMap<K, Entry<V>> entries = new LinkedHashMap<>(16, 0.75f, true);
    private long retainedBytes;

    public Hk3WeightedCache(long limit, ToLongFunction<V> weight) {
        if (limit < 0) throw new IllegalArgumentException("缓存容量不能为负");
        this.limit = limit;
        this.weight = java.util.Objects.requireNonNull(weight);
    }

    public synchronized V get(K key, Function<K, V> loader) {
        Entry<V> existing = entries.get(key);
        if (existing != null) return existing.value();
        V value = java.util.Objects.requireNonNull(loader.apply(key));
        long bytes = weight.applyAsLong(value);
        if (bytes < 0) throw new IllegalArgumentException("缓存权重不能为负");
        // 超大资源可被当前调用使用，但不挤走现有小资源，也不永久占据缓存。
        if (bytes > limit || limit == 0) return value;
        var iterator = entries.entrySet().iterator();
        while (retainedBytes > limit - bytes && iterator.hasNext()) {
            retainedBytes -= iterator.next().getValue().bytes();
            iterator.remove();
        }
        entries.put(key, new Entry<>(value, bytes));
        retainedBytes += bytes;
        return value;
    }

    public synchronized long retainedBytes() { return retainedBytes; }
    public synchronized int size() { return entries.size(); }
    public synchronized void clear() { entries.clear(); retainedBytes = 0; }
}
