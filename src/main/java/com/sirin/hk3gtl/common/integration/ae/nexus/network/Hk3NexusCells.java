package com.sirin.hk3gtl.common.integration.ae.nexus.network;

import appeng.api.config.Actionable;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.api.storage.IStorageMounts;
import appeng.api.storage.StorageCells;
import appeng.api.storage.cells.StorageCell;
import com.lowdragmc.lowdraglib.side.item.IItemTransfer;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.item.ItemStack;
import org.gtlcore.gtlcore.integration.ae2.storage.PreciseStorageAmount;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.function.IntSupplier;

final class Hk3NexusCells {
    private record Cell(ItemStack stack, StorageCell inventory, boolean infinite) {}
    private static final Cell EMPTY = new Cell(ItemStack.EMPTY, null, false);
    private final List<Cell> cells = new ArrayList<>();
    private final Runnable changed;
    private final Runnable remount;

    Hk3NexusCells(Runnable changed, Runnable remount) {
        this.changed = changed;
        this.remount = remount;
    }

    int count() {
        return (int) cells.stream().filter(cell -> !cell.stack.isEmpty()).count();
    }

    int slots() { return cells.size() + 1; }

    ItemStack get(int index) {
        if (index >= cells.size()) return ItemStack.EMPTY;
        var cell = cells.get(index);
        if (!cell.stack.isEmpty()) cell.inventory.persist();
        return cell.stack.copy();
    }

    void set(int index, ItemStack stack) {
        while (cells.size() <= index) cells.add(EMPTY);
        var previous = cells.get(index);
        if (!previous.stack.isEmpty()) previous.inventory.persist();
        cells.set(index, stack.isEmpty() ? EMPTY : create(stack.copyWithCount(1)));
        remount.run();
        changed.run();
    }

    ItemStack insert(ItemStack stack) {
        if (!StorageCells.isCellHandled(stack)) return stack;
        int slot = 0;
        while (slot < cells.size() && !cells.get(slot).stack.isEmpty()) slot++;
        set(slot, stack);
        var remainder = stack.copy();
        remainder.shrink(1);
        return remainder;
    }

    ItemStack remove(int index) {
        var stack = get(index);
        if (!stack.isEmpty()) set(index, ItemStack.EMPTY);
        return stack;
    }

    private Cell create(ItemStack stack) {
        var id = BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
        boolean infinite = id.equals("expatternprovider:infinity_cell")
                || id.equals("ae2:creative_item_cell") || id.equals("ae2:creative_fluid_cell");
        return new Cell(stack, StorageCells.getCellInventory(stack, changed::run), infinite);
    }

    void mount(IStorageMounts mounts) {
        for (var cell : cells) if (!cell.stack.isEmpty()) mounts.mount(cell.inventory);
    }

    boolean infinite(AEKey key, IActionSource source) {
        for (var cell : cells)
            if (cell.infinite && cell.inventory.extract(key, 1, Actionable.SIMULATE, source) == 1) return true;
        return false;
    }

    BigInteger stored(AEKey key) {
        var total = BigInteger.ZERO;
        for (var cell : cells)
            if (!cell.stack.isEmpty()) total = total.add(cell.inventory instanceof PreciseStorageAmount precise
                    ? precise.getExactStoredAmount(key)
                    : BigInteger.valueOf(cell.inventory.getAvailableStacks().get(key)));
        return total;
    }

    CompoundTag save() {
        var tag = new CompoundTag();
        var entries = new ListTag();
        for (int slot = 0; slot < cells.size(); slot++) {
            var cell = cells.get(slot);
            if (cell.stack.isEmpty()) continue;
            cell.inventory.persist();
            var entry = new CompoundTag();
            entry.putInt("Slot", slot);
            cell.stack.save(entry);
            entries.add(entry);
        }
        tag.put("Cells", entries);
        return tag;
    }

    void load(CompoundTag tag) {
        cells.clear();
        for (var raw : tag.getList("Cells", Tag.TAG_COMPOUND)) {
            var entry = (CompoundTag) raw;
            int slot = entry.getInt("Slot");
            while (cells.size() <= slot) cells.add(EMPTY);
            cells.set(slot, create(ItemStack.of(entry)));
        }
    }

    IItemTransfer pager(IntSupplier page, int size) {
        return new IItemTransfer() {
            private int index(int slot) { return page.getAsInt() * size + slot; }
            @Override public int getSlots() { return size; }
            @Override public ItemStack getStackInSlot(int slot) { return get(index(slot)); }
            @Override public void setStackInSlot(int slot, ItemStack stack) { set(index(slot), stack); }
            @Override public int getSlotLimit(int slot) { return 1; }
            @Override public boolean isItemValid(int slot, ItemStack stack) { return StorageCells.isCellHandled(stack); }
            @Override public ItemStack insertItem(int slot, ItemStack stack, boolean simulate, boolean notifyChanges) {
                if (!isItemValid(slot, stack) || !getStackInSlot(slot).isEmpty()) return stack;
                if (!simulate) setStackInSlot(slot, stack);
                var remainder = stack.copy();
                remainder.shrink(1);
                return remainder;
            }
            @Override public ItemStack extractItem(int slot, int amount, boolean simulate, boolean notifyChanges) {
                if (amount == 0) return ItemStack.EMPTY;
                return simulate ? getStackInSlot(slot) : remove(index(slot));
            }
            @Override public Object createSnapshot() { return save(); }
            @Override public void restoreFromSnapshot(Object snapshot) { load((CompoundTag) snapshot); remount.run(); changed.run(); }
        };
    }
}
