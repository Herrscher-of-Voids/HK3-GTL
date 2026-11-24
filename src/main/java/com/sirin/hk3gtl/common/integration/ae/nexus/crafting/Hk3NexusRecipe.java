package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.crafting.IPatternDetails;
import appeng.api.crafting.PatternDetailsHelper;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.api.stacks.KeyCounter;
import appeng.blockentity.crafting.IMolecularAssemblerSupportedPattern;
import appeng.menu.AutoCraftingMenu;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactBoundPattern;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactPlanner;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.inventory.TransientCraftingContainer;
import net.minecraft.world.level.Level;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;

final class Hk3NexusRecipe {
    final IPatternDetails pattern;
    final KeyCounter[] grouped;
    final Map<AEKey, BigInteger> inputs;
    final Map<AEKey, BigInteger> outputs;

    Hk3NexusRecipe(IPatternDetails selected, Function<AEKey, BigInteger> stock) {
        this(selected, stock, Set.of());
    }

    Hk3NexusRecipe(IPatternDetails selected, Function<AEKey, BigInteger> stock, Set<AEKey> omitted) {
        pattern = Hk3ExactBoundPattern.original(selected);
        var ingredients = selected.getInputs();
        KeyCounter[] counters = new KeyCounter[ingredients.length];
        Map<AEKey, BigInteger> remaining = null;
        outputs = new LinkedHashMap<>();
        for (var output : selected.getOutputs()) if (!omitted.contains(output.what()))
            Hk3NexusLedger.add(outputs, output.what(), BigInteger.valueOf(output.amount()));
        for (int index = 0; index < counters.length; index++) {
            var input = ingredients[index];
            var choices = input.getPossibleInputs();
            GenericStack chosen = choices[0];
            if (choices.length > 1) {
                if (remaining == null) {
                    remaining = new LinkedHashMap<>();
                    for (int i = 0; i < index; i++) for (var used : counters[i]) {
                        remaining.computeIfAbsent(used.getKey(), stock);
                        remaining.merge(used.getKey(), BigInteger.valueOf(used.getLongValue()).negate(), BigInteger::add);
                    }
                }
                for (var choice : choices) {
                    BigInteger available = remaining.computeIfAbsent(choice.what(), stock);
                    if (available.compareTo(BigInteger.valueOf(choice.amount()).multiply(BigInteger.valueOf(input.getMultiplier()))) >= 0) {
                        chosen = choice;
                        break;
                    }
                }
            }
            long amount = Math.multiplyExact(chosen.amount(), input.getMultiplier());
            counters[index] = new KeyCounter();
            counters[index].add(chosen.what(), amount);
            if (remaining != null) {
                remaining.computeIfAbsent(chosen.what(), stock);
                remaining.merge(chosen.what(), BigInteger.valueOf(amount).negate(), BigInteger::add);
            }
            AEKey remainder = input.getRemainingKey(chosen.what());
            if (remainder != null) Hk3NexusLedger.add(outputs, remainder, BigInteger.valueOf(input.getMultiplier()));
        }
        grouped = Hk3ExactBoundPattern.providerInputs(selected, counters);
        inputs = counts(grouped);
    }

    private Hk3NexusRecipe(IPatternDetails pattern, KeyCounter[] grouped, Map<AEKey, BigInteger> inputs, Map<AEKey, BigInteger> outputs) {
        this.pattern = pattern;
        this.grouped = grouped;
        this.inputs = inputs;
        this.outputs = outputs;
    }

    Hk3NexusRecipe bindCounts(Hk3ExactPlanner.Recipe<AEKey, IPatternDetails> recipe) {
        return new Hk3NexusRecipe(pattern, grouped, recipe.inputs(), recipe.outputs());
    }

    boolean molecular() { return pattern instanceof IMolecularAssemblerSupportedPattern; }

    Map<AEKey, BigInteger> assemble(KeyCounter[] contents, Level level) {
        var assembler = (IMolecularAssemblerSupportedPattern) pattern;
        var grid = new TransientCraftingContainer(new AutoCraftingMenu(), 3, 3);
        assembler.fillCraftingGrid(copy(contents), grid::setItem);
        Map<AEKey, BigInteger> result = new LinkedHashMap<>();
        var output = GenericStack.fromItemStack(assembler.assemble(grid, level));
        if (output != null) Hk3NexusLedger.add(result, output.what(), BigInteger.valueOf(output.amount()));
        for (var stack : assembler.getRemainingItems(grid)) {
            var remainder = GenericStack.fromItemStack(stack);
            if (remainder != null) Hk3NexusLedger.add(result, remainder.what(), BigInteger.valueOf(remainder.amount()));
        }
        return result;
    }

    static KeyCounter[] copy(KeyCounter[] contents) {
        return scaledInputs(contents, 1);
    }

    static KeyCounter[] scaledInputs(KeyCounter[] contents, long operations) {
        return Arrays.stream(contents).map(counter -> {
            KeyCounter copy = new KeyCounter();
            for (var entry : counter) copy.add(entry.getKey(), Math.multiplyExact(entry.getLongValue(), operations));
            return copy;
        }).toArray(KeyCounter[]::new);
    }

    private static Map<AEKey, BigInteger> counts(KeyCounter[] contents) {
        Map<AEKey, BigInteger> result = new LinkedHashMap<>();
        for (var counter : contents) for (var entry : counter)
            Hk3NexusLedger.add(result, entry.getKey(), BigInteger.valueOf(entry.getLongValue()));
        return result;
    }

    CompoundTag write() {
        CompoundTag tag = new CompoundTag();
        tag.put("pattern", pattern.getDefinition().toTag());
        ListTag groups = new ListTag();
        for (var counter : grouped) groups.add(Hk3NexusLedger.write(counts(new KeyCounter[]{counter})));
        tag.put("groups", groups);
        tag.put("outputs", Hk3NexusLedger.write(outputs));
        return tag;
    }

    static Hk3NexusRecipe read(CompoundTag tag, Level level) {
        IPatternDetails pattern = PatternDetailsHelper.decodePattern(AEItemKey.fromTag(tag.getCompound("pattern")), level);
        ListTag groups = tag.getList("groups", Tag.TAG_LIST);
        KeyCounter[] counters = new KeyCounter[groups.size()];
        for (int index = 0; index < counters.length; index++) {
            counters[index] = new KeyCounter();
            var counter = counters[index];
            Hk3NexusLedger.read((ListTag) groups.get(index)).forEach((key, count) -> counter.add(key, count.longValueExact()));
        }
        return new Hk3NexusRecipe(pattern, counters, counts(counters), Hk3NexusLedger.read(tag.getList("outputs", Tag.TAG_COMPOUND)));
    }
}
