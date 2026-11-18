package com.sirin.hk3gtl.common.integration.ae.nexus.network;

import appeng.api.networking.IGrid;
import appeng.api.stacks.AEKey;
import appeng.api.storage.MEStorage;
import org.gtlcore.gtlcore.integration.ae2.storage.TerminalDisplayRead;

import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.NavigableMap;
import java.util.WeakHashMap;

public final class Hk3NexusStock {
    public interface Mounts { NavigableMap<Integer, List<MEStorage>> hk3gtl$mountedInventories(); }
    private record Cached(int tick, Map<AEKey, BigInteger> stock) {}
    private static final Map<IGrid, Cached> CACHE = new WeakHashMap<>();

    private Hk3NexusStock() {}

    public static Map<AEKey, BigInteger> snapshot(IGrid grid) {
        int tick = grid.getPivot().getLevel().getServer().getTickCount();
        Cached cached = CACHE.get(grid);
        if (cached != null && cached.tick() == tick) return cached.stock();
        var inventory = grid.getStorageService().getInventory();
        var read = TerminalDisplayRead.collect(inventory::getAvailableStacks);
        Map<AEKey, BigInteger> result = new LinkedHashMap<>();
        for (var entry : read.available()) result.put(entry.getKey(), BigInteger.valueOf(entry.getLongValue()));
        result.putAll(read.exact());
        Map<AEKey, BigInteger> stock = Map.copyOf(result);
        CACHE.put(grid, new Cached(tick, stock));
        return stock;
    }
}
