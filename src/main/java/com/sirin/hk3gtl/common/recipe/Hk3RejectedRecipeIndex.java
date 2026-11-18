package com.sirin.hk3gtl.common.recipe;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;

/** 保留原生树完全漏索引的HK命名空间配方，交回原生候选过滤与执行流程。 */
public final class Hk3RejectedRecipeIndex<R> {
    private final ConcurrentHashMap<String, R> rejected = new ConcurrentHashMap<>();

    public void record(String id, R recipe, boolean indexed) {
        if (!id.startsWith("hk3gtl:")) return;
        if (indexed) rejected.remove(id);
        else rejected.put(id, recipe);
    }

    public void clear() { rejected.clear(); }

    public boolean isEmpty() { return rejected.isEmpty(); }

    public List<R> appendTo(List<R> existing, Function<R, String> id) {
        List<R> merged = new ArrayList<>(existing == null ? List.of() : existing);
        for (var entry : rejected.entrySet()) {
            if (merged.stream().noneMatch(recipe -> entry.getKey().equals(id.apply(recipe))))
                merged.add(entry.getValue());
        }
        return merged;
    }
}
