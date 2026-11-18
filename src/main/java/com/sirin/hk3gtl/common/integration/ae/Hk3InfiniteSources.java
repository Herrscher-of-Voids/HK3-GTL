package com.sirin.hk3gtl.common.integration.ae;

import appeng.api.config.Actionable;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.api.storage.MEStorage;
import org.gtlcore.gtlcore.integration.ae2.throughput.ThroughputStorageView;
import org.gtlcore.gtlcore.mixin.ae2.storage.MEInventoryHandlerDisplayAccessor;

import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Set;

public final class Hk3InfiniteSources {
    private Hk3InfiniteSources() {}

    public static Set<AEKey> collect(MEStorage storage, IActionSource source) {
        return Set.copyOf(collect(storage, source, new IdentityHashMap<>()));
    }

    private static Set<AEKey> collect(MEStorage storage, IActionSource source,
                                      Map<MEStorage, Set<AEKey>> visited) {
        var known = visited.get(storage);
        if (known != null) return known;
        var keys = new HashSet<AEKey>();
        visited.put(storage, keys);
        String type = storage.getClass().getName();
        if (type.equals("appeng.me.cells.CreativeCellInventory")
                || type.equals("com.glodblock.github.extendedae.common.inventory.InfinityCellInventory")) {
            keys.addAll(storage.getAvailableStacks().keySet());
            keys.removeIf(key -> storage.extract(key, 1, Actionable.SIMULATE, source) != 1);
        } else if (storage instanceof ThroughputStorageView view) {
            for (var child : view.gtlcore$getChildStorages())
                keys.addAll(collect(child, source, visited));
        }
        if (storage instanceof MEInventoryHandlerDisplayAccessor filter) {
            if (!filter.gtlcore$allowsDisplayExtraction()) keys.clear();
            else if (filter.gtlcore$filtersDisplayExtraction() || filter.gtlcore$filtersDisplayContents())
                keys.removeIf(key -> !filter.gtlcore$canDisplay(key));
        }
        return keys;
    }
}
