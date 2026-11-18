package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.api.stacks.KeyCounter;
import appeng.blockentity.crafting.IMolecularAssemblerSupportedPattern;
import appeng.crafting.pattern.AECraftingPattern;
import appeng.crafting.pattern.AESmithingTablePattern;
import appeng.crafting.pattern.AEStonecuttingPattern;
import appeng.menu.AutoCraftingMenu;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.inventory.TransientCraftingContainer;
import net.minecraft.world.level.Level;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.ToLongFunction;

/** 将替代输入固定到规划选中的真实资源；外部投料仍使用原生样板。 */
public final class Hk3ExactBoundPattern implements IPatternDetails {
    static final String MARKER = "hk3BoundPattern";
    private static final String INPUTS = "hk3BoundInputs";
    private static final String OUTPUTS = "hk3BoundOutputs";
    private static final String FORMAT = "hk3BoundSelectionVersion";
    private static final String SOURCE = "hk3BoundSource";
    private final IMolecularAssemblerSupportedPattern source;
    private final List<List<Allocation>> selected;
    private final BoundInput[] inputs;

    private record Allocation(GenericStack stack, long units) {}
    private record BoundInput(int group, GenericStack stack, long multiplier, AEKey remainder) implements IInput {
        @Override public GenericStack[] getPossibleInputs() { return new GenericStack[]{stack}; }
        @Override public long getMultiplier() { return multiplier; }
        @Override public boolean isValid(AEKey key, Level level) { return stack.what().equals(key); }
        @Override public AEKey getRemainingKey(AEKey key) { return remainder; }
    }

    private Hk3ExactBoundPattern(IMolecularAssemblerSupportedPattern source, List<List<Allocation>> selected) {
        this.source = source;
        this.selected = List.copyOf(selected);
        List<BoundInput> parts = new ArrayList<>();
        var original = source.getInputs();
        for (int group = 0; group < selected.size(); group++) {
            for (var allocation : selected.get(group)) {
                var stack = allocation.stack();
                parts.add(new BoundInput(group, stack, allocation.units(),
                        original[group].getRemainingKey(stack.what())));
            }
        }
        inputs = parts.toArray(BoundInput[]::new);
    }

    static boolean supports(IPatternDetails pattern) {
        return pattern.getClass() == AECraftingPattern.class
                || pattern.getClass() == AESmithingTablePattern.class
                || pattern.getClass() == AEStonecuttingPattern.class;
    }

    static boolean requiresBinding(IPatternDetails pattern) {
        return !(pattern instanceof AECraftingPattern crafting)
                || crafting.canSubstitute() || crafting.canSubstituteFluids();
    }

    static Iterator<IPatternDetails> alternativeCandidates(IMolecularAssemblerSupportedPattern source, Level level, int budget,
            ToLongFunction<AEKey> available) {
        if (budget <= 0) return Collections.emptyIterator();
        List<List<GenericStack>> candidates = new ArrayList<>();
        Map<AEKey, Long> stock = new LinkedHashMap<>();
        for (var input : source.getInputs()) {
            var choices = new LinkedHashSet<GenericStack>();
            for (var candidate : input.getPossibleInputs()) {
                if (candidate != null && candidate.amount() > 0 && input.isValid(candidate.what(), level)) {
                    choices.add(candidate);
                    stock.computeIfAbsent(candidate.what(), available::applyAsLong);
                }
            }
            if (choices.isEmpty()) return Collections.emptyIterator();
            candidates.add(List.copyOf(choices));
        }
        LinkedHashSet<List<List<Allocation>>> combinations = new LinkedHashSet<>();
        int starts = candidates.stream().mapToInt(List::size).max().orElse(1);
        for (int start = 0; start < Math.min(starts, budget); start++) {
            Map<AEKey, Long> remainingStock = new LinkedHashMap<>(stock);
            List<List<Allocation>> selection = new ArrayList<>();
            for (int group = 0; group < candidates.size(); group++) {
                var choices = candidates.get(group);
                long remaining = source.getInputs()[group].getMultiplier();
                long[] counts = new long[choices.size()];
                for (int i = 0; i < choices.size() && remaining > 0; i++) {
                    int index = (start + i) % choices.size();
                    var stack = choices.get(index);
                    long units = Math.min(remaining, remainingStock.get(stack.what()) / stack.amount());
                    counts[index] = units;
                    remainingStock.merge(stack.what(), -Math.multiplyExact(units, stack.amount()), Long::sum);
                    remaining -= units;
                }
                counts[start % choices.size()] += remaining;
                List<Allocation> groupSelection = new ArrayList<>();
                for (int i = 0; i < choices.size(); i++)
                    if (counts[i] > 0) groupSelection.add(new Allocation(choices.get(i), counts[i]));
                selection.add(List.copyOf(groupSelection));
            }
            combinations.add(List.copyOf(selection));
        }
        List<List<List<Allocation>>> uniform = new ArrayList<>(), mixed = new ArrayList<>();
        for (int group = 0; group < candidates.size(); group++) {
            long units = source.getInputs()[group].getMultiplier();
            List<List<Allocation>> groupUniform = new ArrayList<>();
            for (var candidate : candidates.get(group)) groupUniform.add(List.of(new Allocation(candidate, units)));
            uniform.add(List.copyOf(groupUniform));
            var groupMixed = new LinkedHashSet<>(groupUniform);
            enumerateAllocations(candidates.get(group), 0, units, new ArrayList<>(), groupMixed, budget);
            mixed.add(List.copyOf(groupMixed));
        }
        enumerateSelections(uniform, 0, new ArrayList<>(), combinations, budget);
        enumerateSelections(mixed, 0, new ArrayList<>(), combinations, budget);
        return combinations.stream().<IPatternDetails>map(selection ->
                new Hk3ExactBoundPattern(source, selection)).iterator();
    }

    private static void enumerateAllocations(List<GenericStack> choices, int start, long remaining,
            List<Allocation> prefix, LinkedHashSet<List<Allocation>> result, int budget) {
        if (result.size() >= budget) return;
        if (remaining == 0) { result.add(List.copyOf(prefix)); return; }
        for (int index = start; index < choices.size() && result.size() < budget; index++) {
            long minimum = index == choices.size() - 1 ? remaining : 1;
            for (long units = remaining; units >= minimum && result.size() < budget; units--) {
                prefix.add(new Allocation(choices.get(index), units));
                enumerateAllocations(choices, index + 1, remaining - units, prefix, result, budget);
                prefix.remove(prefix.size() - 1);
            }
        }
    }

    private static void enumerateSelections(List<List<List<Allocation>>> groups, int group,
            List<List<Allocation>> prefix, LinkedHashSet<List<List<Allocation>>> result, int budget) {
        if (result.size() >= budget) return;
        if (group == groups.size()) { result.add(List.copyOf(prefix)); return; }
        for (var selection : groups.get(group)) {
            prefix.add(selection);
            enumerateSelections(groups, group + 1, prefix, result, budget);
            prefix.remove(prefix.size() - 1);
            if (result.size() >= budget) return;
        }
    }

    boolean sameResult(Level level) {
        var grid = new TransientCraftingContainer(new AutoCraftingMenu(), 3, 3);
        KeyCounter[] contents = new KeyCounter[inputs.length];
        Map<AEKey, Long> expected = new LinkedHashMap<>();
        for (int slot = 0; slot < inputs.length; slot++) {
            var input = inputs[slot];
            contents[slot] = new KeyCounter();
            contents[slot].add(input.stack().what(), Math.multiplyExact(input.stack().amount(), input.multiplier()));
            if (input.remainder() != null) expected.merge(input.remainder(), input.multiplier(), Math::addExact);
        }
        var grouped = providerInputs(this, contents);
        source.fillCraftingGrid(grouped, grid::setItem);
        for (var counter : grouped) {
            counter.removeZeros();
            if (!counter.isEmpty()) return false;
        }
        if (!Objects.equals(GenericStack.fromItemStack(source.assemble(grid, level)), source.getPrimaryOutput()))
            return false;
        Map<AEKey, Long> returned = new LinkedHashMap<>();
        for (var stack : source.getRemainingItems(grid)) {
            var remainder = GenericStack.fromItemStack(stack);
            if (remainder != null) returned.merge(remainder.what(), remainder.amount(), Math::addExact);
        }
        return expected.equals(returned);
    }

    public static KeyCounter[] providerInputs(IPatternDetails pattern, KeyCounter[] contents) {
        if (!(pattern instanceof Hk3ExactBoundPattern bound)) return contents;
        KeyCounter[] grouped = new KeyCounter[bound.source.getInputs().length];
        Arrays.setAll(grouped, ignored -> new KeyCounter());
        for (int part = 0; part < contents.length; part++) {
            for (var entry : contents[part])
                grouped[bound.inputs[part].group()].add(entry.getKey(), entry.getLongValue());
        }
        return grouped;
    }

    public static IPatternDetails original(IPatternDetails pattern) {
        if (pattern instanceof Hk3ExactScaledPattern scaled) return scaled.source();
        return pattern instanceof Hk3ExactBoundPattern bound ? bound.source : pattern;
    }

    static Map<IPatternDetails, BigInteger> nativeCounts(Map<IPatternDetails, BigInteger> counts) {
        Map<IPatternDetails, BigInteger> result = new LinkedHashMap<>();
        counts.forEach((pattern, amount) -> result.merge(original(pattern),
                amount.multiply(BigInteger.valueOf(Hk3ExactScaledPattern.operations(pattern))), BigInteger::add));
        return result;
    }

    void writeSelection(CompoundTag tag) {
        tag.putInt(FORMAT, 2);
        tag.putString(SOURCE, source.getClass().getName());
        ListTag choices = new ListTag();
        for (var input : inputs) {
            CompoundTag choice = GenericStack.writeTag(input.stack());
            choice.putInt("group", input.group());
            choice.putLong("multiplier", input.multiplier());
            choice.putLong("sourceMultiplier", source.getInputs()[input.group()].getMultiplier());
            if (input.remainder() != null) choice.put("remainder", input.remainder().toTagGeneric());
            choices.add(choice);
        }
        tag.put(INPUTS, choices);
        ListTag outputs = new ListTag();
        Arrays.stream(getOutputs()).forEach(output -> outputs.add(GenericStack.writeTag(output)));
        tag.put(OUTPUTS, outputs);
    }

    static IPatternDetails readSelection(IPatternDetails pattern, CompoundTag tag, Level level) {
        if (!tag.getBoolean(MARKER)) {
            if (tag.contains(INPUTS) || tag.contains(OUTPUTS) || tag.contains(FORMAT) || tag.contains(SOURCE))
                throw new IllegalArgumentException("替代样板绑定标记缺失");
            return pattern;
        }
        if (!tag.contains(INPUTS, Tag.TAG_LIST) || !tag.contains(OUTPUTS, Tag.TAG_LIST))
            throw new IllegalArgumentException("替代样板选材或产物签名缺失");
        if (!supports(pattern) || !requiresBinding(pattern)
                || (tag.contains(SOURCE)
                    ? !pattern.getClass().getName().equals(tag.getString(SOURCE))
                    : pattern.getClass() != AECraftingPattern.class))
            throw new IllegalArgumentException("持久化替代样板身份已改变");
        var crafting = (IMolecularAssemblerSupportedPattern) pattern;
        ListTag choices = tag.getList(INPUTS, Tag.TAG_COMPOUND);
        var original = crafting.getInputs();
        boolean mixed = tag.contains(FORMAT, Tag.TAG_INT);
        if (mixed ? tag.getInt(FORMAT) != 2 : choices.size() != original.length)
            throw new IllegalArgumentException("持久化替代槽位或格式已改变");
        List<List<Allocation>> selected = new ArrayList<>();
        for (int group = 0; group < original.length; group++) selected.add(new ArrayList<>());
        long[] totals = new long[original.length];
        for (int part = 0; part < choices.size(); part++) {
            CompoundTag choice = choices.getCompound(part);
            int group = mixed ? choice.getInt("group") : part;
            long units = choice.getLong("multiplier");
            if (group < 0 || group >= original.length || units <= 0
                    || mixed && (!choice.contains("group", Tag.TAG_INT)
                        || !choice.contains("sourceMultiplier", Tag.TAG_LONG)
                        || original[group].getMultiplier() != choice.getLong("sourceMultiplier"))
                    || !mixed && (choice.contains("group") || choice.contains("sourceMultiplier")))
                throw new IllegalArgumentException("持久化混合输入组已改变");
            var stack = GenericStack.readTag(choice);
            if (stack == null || !Arrays.asList(original[group].getPossibleInputs()).contains(stack)
                    || !original[group].isValid(stack.what(), level)
                    || selected.get(group).stream().anyMatch(allocation -> allocation.stack().equals(stack))
                    || !Objects.equals(original[group].getRemainingKey(stack.what()),
                        choice.contains("remainder") ? AEKey.fromTagGeneric(choice.getCompound("remainder")) : null))
                throw new IllegalArgumentException("持久化选材或容器返还已改变");
            selected.get(group).add(new Allocation(stack, units));
            totals[group] = Math.addExact(totals[group], units);
        }
        for (int group = 0; group < original.length; group++) {
            if (totals[group] != original[group].getMultiplier())
                throw new IllegalArgumentException("持久化混合输入数量不守恒");
            selected.set(group, List.copyOf(selected.get(group)));
        }
        ListTag outputs = tag.getList(OUTPUTS, Tag.TAG_COMPOUND);
        if (outputs.size() != pattern.getOutputs().length) throw new IllegalArgumentException("持久化产物已改变");
        for (int index = 0; index < outputs.size(); index++)
            if (!pattern.getOutputs()[index].equals(GenericStack.readTag(outputs.getCompound(index))))
                throw new IllegalArgumentException("持久化产物已改变");
        var bound = new Hk3ExactBoundPattern(crafting, selected);
        if (!bound.sameResult(level)) throw new IllegalArgumentException("持久化替代组合已不满足原生配方");
        return bound;
    }

    @Override public AEItemKey getDefinition() { return source.getDefinition(); }
    @Override public IInput[] getInputs() { return inputs; }
    @Override public GenericStack[] getOutputs() { return source.getOutputs(); }
    @Override public boolean equals(Object other) {
        return other instanceof Hk3ExactBoundPattern bound && source.equals(bound.source) && selected.equals(bound.selected);
    }
    @Override public int hashCode() { return Objects.hash(source, selected); }
}
