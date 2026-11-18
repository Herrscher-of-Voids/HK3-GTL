package com.sirin.hk3gtl.common.gaze;

import java.lang.ref.WeakReference;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/**
 * 稳定源的坐标与具体实例登记；弱引用不因维度索引阻止机器及世界释放。
 */
public final class Hk3SuppressionSourceRegistry<K, V> {
    private final Map<K, WeakReference<V>> sources = new HashMap<>();

    public synchronized void register(K key, V source) {
        sources.put(Objects.requireNonNull(key), new WeakReference<>(Objects.requireNonNull(source)));
    }

    /** 只撤销发起注销的实例；旧机器的迟到回调不能删除同坐标的新登记。 */
    public synchronized void unregister(K key, V source) {
        var registered = sources.get(key);
        if (registered != null && registered.get() == source) sources.remove(key);
    }

    /** 调用期间保留强引用，顺手清除已经释放的源；修改返回副本不影响登记。 */
    public synchronized Map<K, V> snapshot() {
        Map<K, V> live = new HashMap<>();
        var entries = sources.entrySet().iterator();
        while (entries.hasNext()) {
            var entry = entries.next();
            V source = entry.getValue().get();
            if (source == null) entries.remove();
            else live.put(entry.getKey(), source);
        }
        return live;
    }
}
