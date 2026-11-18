package com.sirin.hk3gtl.common.util;

import java.util.LinkedHashMap;
import java.util.function.Function;
import java.util.function.ToLongFunction;

public final class Hk3WeightedCache<K, V> {
    private record Entry<V>(V value, long bytes) {}
    private final long limit;
    private final ToLongFunction<V> weight;
    private final LinkedHashMap<K, Entry<V>> entries = new LinkedHashMap<>(16, 0.75f, true);
    private long retainedBytes;

    public Hk3WeightedCache(long limit, ToLongFunction<V> weight) {
        if (limit < 0) throw new IllegalArgumentException("缓存容量不能为负");
        this.limit = limit;
        this.weight = weight;
    }

    public synchronized V get(K key, Function<K, V> loader) {
        Entry<V> existing = entries.get(key);
        if (existing != null) return existing.value();
        V value = loader.apply(key);
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
