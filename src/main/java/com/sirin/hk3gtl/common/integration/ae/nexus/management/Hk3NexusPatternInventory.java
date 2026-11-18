package com.sirin.hk3gtl.common.integration.ae.nexus.management;

import appeng.api.crafting.IPatternDetails;
import appeng.api.crafting.PatternDetailsHelper;
import appeng.api.inventories.InternalInventory;
import appeng.api.stacks.AEKey;
import com.glodblock.github.extendedae.util.FCUtil;
import com.lowdragmc.lowdraglib.misc.ItemStackTransfer;
import com.lowdragmc.lowdraglib.side.item.IItemTransfer;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.function.IntSupplier;
import java.util.function.Supplier;

public final class Hk3NexusPatternInventory implements IItemTransfer, InternalInventory {
    private final List<ItemStack> stacks = new ArrayList<>();
    private final Supplier<Level> level;
    private final Runnable changed;
    private List<IPatternDetails> decoded;
    private List<IndexedPattern> indexed;
    private int count;
    private long revision;

    private record IndexedPattern(int slot, IPatternDetails pattern, List<AEKey> inputs, List<AEKey> outputs) {}
    private record SearchEntry(int slot, List<List<String>> inputs, List<List<String>> outputs) {}

    public Hk3NexusPatternInventory(Supplier<Level> level, Runnable changed) {
        this.level = level;
        this.changed = changed;
    }

    @Override public int getSlots() { return stacks.size() + 1; }
    @Override public int size() { return getSlots(); }
    @Override public ItemStack getStackInSlot(int slot) { return slot < stacks.size() ? stacks.get(slot) : ItemStack.EMPTY; }
    @Override public int getSlotLimit(int slot) { return 1; }
    @Override public boolean isItemValid(int slot, ItemStack stack) { return PatternDetailsHelper.isEncodedPattern(stack); }
    @Override public void setItemDirect(int slot, ItemStack stack) { setStackInSlot(slot, stack); }
    @Override public ItemStack insertItem(int slot, ItemStack stack, boolean simulate) {
        return insertItem(slot, stack, simulate, true);
    }
    @Override public ItemStack extractItem(int slot, int amount, boolean simulate) {
        return extractItem(slot, amount, simulate, true);
    }

    @Override public void clear() {
        stacks.clear();
        count = 0;
        onContentsChanged();
    }

    @Override public void setStackInSlot(int slot, ItemStack stack) {
        while (stacks.size() <= slot) stacks.add(ItemStack.EMPTY);
        if (!stacks.get(slot).isEmpty()) count--;
        if (!stack.isEmpty()) count++;
        stacks.set(slot, stack);
        onContentsChanged();
    }

    @Override public ItemStack insertItem(int slot, ItemStack stack, boolean simulate, boolean notifyChanges) {
        if (!isItemValid(slot, stack) || !getStackInSlot(slot).isEmpty()) return stack;
        if (!simulate) setStackInSlot(slot, stack.copyWithCount(1));
        return stack.copyWithCount(stack.getCount() - 1);
    }

    @Override public ItemStack extractItem(int slot, int amount, boolean simulate, boolean notifyChanges) {
        if (amount == 0) return ItemStack.EMPTY;
        ItemStack stack = getStackInSlot(slot);
        if (stack.isEmpty()) return ItemStack.EMPTY;
        ItemStack result = stack.copy();
        if (!simulate) setStackInSlot(slot, ItemStack.EMPTY);
        return result;
    }

    @Override public void onContentsChanged() {
        decoded = null;
        indexed = null;
        revision++;
        changed.run();
    }

    public List<IPatternDetails> patterns() {
        if (decoded == null) decoded = indexedPatterns().stream().map(IndexedPattern::pattern).toList();
        return decoded;
    }

    private List<IndexedPattern> indexedPatterns() {
        if (indexed == null) {
            var result = new ArrayList<IndexedPattern>();
            for (int slot = 0; slot < stacks.size(); slot++) {
                ItemStack stack = stacks.get(slot);
                if (stack.isEmpty()) continue;
                IPatternDetails pattern = PatternDetailsHelper.decodePattern(stack, level.get());
                if (pattern != null) result.add(new IndexedPattern(slot, pattern,
                        Arrays.stream(pattern.getInputs()).map(input -> input.getPossibleInputs()[0].what()).toList(),
                        Arrays.stream(pattern.getOutputs()).map(output -> output.what()).toList()));
            }
            indexed = List.copyOf(result);
        }
        return indexed;
    }

    public List<ItemStack> contents() { return stacks.stream().filter(stack -> !stack.isEmpty()).map(ItemStack::copy).toList(); }
    public int count() { return count; }
    public long revision() { return revision; }

    public ListTag write() {
        var list = new ListTag();
        for (int slot = 0; slot < stacks.size(); slot++) {
            if (stacks.get(slot).isEmpty()) continue;
            var row = new CompoundTag();
            row.putInt("Slot", slot);
            row.put("Stack", stacks.get(slot).save(new CompoundTag()));
            list.add(row);
        }
        return list;
    }

    public void read(ListTag list) {
        stacks.clear();
        count = 0;
        for (Tag value : list) {
            var row = (CompoundTag) value;
            int slot = row.getInt("Slot");
            while (stacks.size() <= slot) stacks.add(ItemStack.EMPTY);
            stacks.set(slot, ItemStack.of(row.getCompound("Stack")));
            count++;
        }
        decoded = null;
        indexed = null;
    }

    @Override public Object createSnapshot() { return write(); }
    @Override public void restoreFromSnapshot(Object snapshot) { read((ListTag) snapshot); onContentsChanged(); }

    public IItemTransfer page(IntSupplier page, int size) {
        return page(page, size, () -> "", () -> "");
    }

    public PatternPage page(IntSupplier page, int size, Supplier<String> inputSearch, Supplier<String> outputSearch) {
        return new PatternPage(page, size, inputSearch, outputSearch);
    }

    public final class PatternPage implements IItemTransfer {
        private final IntSupplier page;
        private final int size;
        private final Supplier<String> inputSearch;
        private final Supplier<String> outputSearch;
        private final boolean client = level.get().isClientSide;
        private final IItemTransfer display;
        private final int[] slots;
        private List<SearchEntry> searchEntries = List.of();
        private List<Integer> matches = List.of();
        private boolean filtering;

        private PatternPage(IntSupplier page, int size, Supplier<String> inputSearch, Supplier<String> outputSearch) {
            this.page = page;
            this.size = size;
            this.inputSearch = inputSearch;
            this.outputSearch = outputSearch;
            display = new ItemStackTransfer(size);
            slots = new int[size];
        }

        public void writeSearchData(FriendlyByteBuf buffer) {
            var rows = indexedPatterns();
            buffer.writeVarInt(rows.size());
            for (var row : rows) {
                buffer.writeVarInt(row.slot());
                buffer.writeCollection(row.inputs(), AEKey::writeKey);
                buffer.writeCollection(row.outputs(), AEKey::writeKey);
            }
        }

        public void readSearchData(FriendlyByteBuf buffer) {
            int count = buffer.readVarInt();
            var rows = new ArrayList<SearchEntry>(count);
            for (int row = 0; row < count; row++) rows.add(new SearchEntry(buffer.readVarInt(),
                    buffer.readList(AEKey::readKey).stream().map(key -> FCUtil.tokenize(key.getDisplayName().getString())).toList(),
                    buffer.readList(AEKey::readKey).stream().map(key -> FCUtil.tokenize(key.getDisplayName().getString())).toList()));
            searchEntries = List.copyOf(rows);
        }

        public void writeFilter(FriendlyByteBuf buffer) {
            var inputs = FCUtil.tokenize(inputSearch.get());
            var outputs = FCUtil.tokenize(outputSearch.get());
            boolean active = !inputs.isEmpty() || !outputs.isEmpty();
            buffer.writeBoolean(active);
            buffer.writeCollection(active ? searchEntries.stream()
                    .filter(row -> matches(inputs, row.inputs()) && matches(outputs, row.outputs()))
                    .map(SearchEntry::slot).toList() : List.<Integer>of(), FriendlyByteBuf::writeVarInt);
        }

        public void readFilter(FriendlyByteBuf buffer) {
            filtering = buffer.readBoolean();
            matches = buffer.readList(FriendlyByteBuf::readVarInt);
            refresh();
        }

        private boolean matches(List<String> query, List<List<String>> values) {
            return query.isEmpty() || values.stream().anyMatch(tokens -> FCUtil.compareTokens(query, tokens));
        }

        public void refresh() {
            if (client || !filtering) return;
            int first = page.getAsInt() * size;
            int empty = 0;
            var reserved = new HashSet<>(matches);
            for (int slot = 0; slot < size; slot++) {
                if (first + slot < matches.size()) slots[slot] = matches.get(first + slot);
                else {
                    while (empty < stacks.size() && (!stacks.get(empty).isEmpty() || reserved.contains(empty))) empty++;
                    slots[slot] = empty++;
                }
            }
        }

        private IItemTransfer inventory() { return client ? display : Hk3NexusPatternInventory.this; }
        private int at(int slot) { return client ? slot : filtering ? slots[slot] : page.getAsInt() * size + slot; }
        @Override public int getSlots() { return size; }
        @Override public ItemStack getStackInSlot(int slot) { return inventory().getStackInSlot(at(slot)); }
        @Override public void setStackInSlot(int slot, ItemStack stack) { inventory().setStackInSlot(at(slot), stack); }
        @Override public ItemStack insertItem(int slot, ItemStack stack, boolean simulate, boolean notify) { return inventory().insertItem(at(slot), stack, simulate, notify); }
        @Override public ItemStack extractItem(int slot, int amount, boolean simulate, boolean notify) { return inventory().extractItem(at(slot), amount, simulate, notify); }
        @Override public int getSlotLimit(int slot) { return 1; }
        @Override public boolean isItemValid(int slot, ItemStack stack) { return Hk3NexusPatternInventory.this.isItemValid(at(slot), stack); }
        @Override public Object createSnapshot() { return inventory().createSnapshot(); }
        @Override public void restoreFromSnapshot(Object snapshot) { inventory().restoreFromSnapshot(snapshot); }
    }
}
