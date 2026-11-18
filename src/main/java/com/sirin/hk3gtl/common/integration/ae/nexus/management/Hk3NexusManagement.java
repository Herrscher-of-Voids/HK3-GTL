package com.sirin.hk3gtl.common.integration.ae.nexus.management;

import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.IGrid;
import appeng.api.stacks.AEKey;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusStock;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Predicate;
import java.util.function.Supplier;

public final class Hk3NexusManagement {
    public record StockTarget(AEKey key, BigInteger amount, BigInteger batch, boolean enabled,
                              UUID owner, int priority) {}
    public record StockView(StockTarget target, BigInteger stored, BigInteger inFlight, boolean infinite) {}

    private final Supplier<IGrid> grid;
    private final Hk3NexusCrafting crafting;
    private final Runnable changed;
    private final Hk3NexusPatternInventory patterns;
    private final Hk3NexusPatternCatalog catalog = new Hk3NexusPatternCatalog();
    private final Map<AEKey, StockTarget> targets = new LinkedHashMap<>();
    private Predicate<AEKey> infiniteSource = key -> false;
    private int ticks;

    public Hk3NexusManagement(Supplier<IGrid> grid, Supplier<Level> level,
                             Hk3NexusCrafting crafting, Runnable changed) {
        this.grid = grid;
        this.crafting = crafting;
        this.changed = changed;
        this.patterns = new Hk3NexusPatternInventory(level, this::patternsChanged);
    }

    public void setInfiniteSource(Predicate<AEKey> source) { infiniteSource = source; }
    public Hk3NexusPatternInventory patterns() { return patterns; }
    public List<IPatternDetails> localPatterns() { return patterns.patterns(); }
    public Hk3NexusPatternCatalog catalog() { return catalog; }
    public Hk3NexusCrafting crafting() { return crafting; }
    public Widget widget(Player player) { return new Hk3NexusManagementWidget(this, player); }

    private void patternsChanged() {
        crafting.patternsChanged();
        changed.run();
    }

    public void setTarget(AEKey key, BigInteger amount, BigInteger batch, boolean enabled, UUID owner) {
        StockTarget previous = targets.get(key);
        if (amount.signum() == 0) targets.remove(key);
        else targets.put(key, new StockTarget(key, amount, batch, enabled, owner,
                previous == null ? 0 : previous.priority()));
        changed.run();
    }

    public void removeTarget(AEKey key) { targets.remove(key); changed.run(); }

    public List<StockView> stockTargets() {
        IGrid network = grid.get();
        Map<AEKey, BigInteger> stock = network == null ? Map.of() : Hk3NexusStock.snapshot(network);
        return targets.values().stream().sorted(Comparator.comparingInt(StockTarget::priority).reversed())
                .map(target -> new StockView(target, stock.getOrDefault(target.key(), BigInteger.ZERO),
                        inFlight(network, target.key()), network != null && infiniteSource.test(target.key()))).toList();
    }

    private BigInteger inFlight(IGrid network, AEKey key) {
        if (network == null) return crafting.inFlight(key);
        return Hk3NexusCrafting.forGrid(network).stream().map(host -> host.inFlight(key)).reduce(BigInteger.ZERO, BigInteger::add);
    }

    public void tick() {
        if (++ticks % 20 != 0) return;
        IGrid network = grid.get();
        if (network == null) return;
        catalog.refresh(network, localPatterns());
        for (var view : stockTargets()) {
            if (!view.target().enabled() || view.infinite() || view.inFlight().signum() > 0) continue;
            BigInteger missing = view.target().amount().subtract(view.stored()).subtract(view.inFlight());
            if (missing.signum() > 0 && network.getCraftingService().isCraftable(view.target().key())) {
                var target = view.target();
                crafting.submit(target.key(), target.batch(), target.owner(), target.priority());
            }
        }
    }

    public List<String> statusLines() {
        var lines = new ArrayList<String>();
        lines.add(grid.get() == null ? "AE网络尚未连接" : "AE节点 " + catalog.nodes() + " · 离线 " + catalog.offline());
        lines.add("未供电节点 " + catalog.unpowered() + " · 等待接收的供应器 " + catalog.busyProviders());
        lines.add("全网样板 " + catalog.size() + " · 循环样板 " + catalog.cyclicPatterns());
        lines.add("本机样板 " + patterns.count() + " · 库存目标 " + targets.size());
        var orders = crafting.orders();
        lines.add("订单 " + orders.size() + " · 在途 " + orders.stream().filter(row -> row.remaining().signum() > 0).count());
        for (var order : orders) {
            if (order.missing().isEmpty()) continue;
            var missing = order.missing().entrySet().iterator().next();
            lines.add(order.target().getDisplayName().getString() + "：缺 "
                    + missing.getKey().getDisplayName().getString() + " × " + missing.getValue());
        }
        return lines;
    }

    public void write(CompoundTag tag) {
        tag.put("Patterns", patterns.write());
        var stock = new ListTag();
        for (StockTarget target : targets.values()) {
            var row = new CompoundTag();
            row.put("Key", target.key().toTagGeneric());
            row.putByteArray("Amount", target.amount().toByteArray());
            row.putByteArray("Batch", target.batch().toByteArray());
            row.putBoolean("Enabled", target.enabled());
            row.putUUID("Owner", target.owner());
            row.putInt("Priority", target.priority());
            stock.add(row);
        }
        tag.put("StockTargets", stock);
    }

    public void read(CompoundTag tag) {
        patterns.read(tag.getList("Patterns", Tag.TAG_COMPOUND));
        targets.clear();
        for (Tag value : tag.getList("StockTargets", Tag.TAG_COMPOUND)) {
            var row = (CompoundTag) value;
            AEKey key = AEKey.fromTagGeneric(row.getCompound("Key"));
            targets.put(key, new StockTarget(key, new BigInteger(row.getByteArray("Amount")),
                    row.contains("Batch") ? new BigInteger(row.getByteArray("Batch")) : BigInteger.ONE,
                    !row.contains("Enabled") || row.getBoolean("Enabled"), row.getUUID("Owner"), row.getInt("Priority")));
        }
    }
}
