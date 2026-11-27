package com.sirin.hk3gtl.common.worldbubble;

import com.gregtechceu.gtceu.api.machine.trait.NotifiableFluidTank;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableItemStackHandler;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient;
import com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient;
import com.sirin.hk3gtl.common.item.Hk3StackableWorldItem;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;
import org.gtlcore.gtlcore.api.machine.trait.MEPart.IMEIOPartMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.MEPatternBufferProxyPartMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.NotifiableMERecipeHandlerTrait;

import java.util.LinkedHashMap;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** 冻结收据的剩余输出与事务共存档；外部仓和本账本之间没有跨文件崩溃原子保证。 */
public final class Hk3WorldResourceOutput {
    private record Destination(UUID team, String role, String facility) {}
    private final Map<UUID, CompoundTag> pending = new LinkedHashMap<>();
    private final Map<Destination, Set<UUID>> destinations = new LinkedHashMap<>();
    private boolean delivering;

    public boolean stage(Hk3WorldBubbleLedger.Transaction tx) {
        if (tx.delivered() || pending.containsKey(tx.id())) return false;
        pending.put(tx.id(), contents(tx.receipt()));
        destinations.computeIfAbsent(destination(tx.receipt()), key -> new LinkedHashSet<>()).add(tx.id());
        return true;
    }

    public List<UUID> operations(UUID team, String role, String facility) {
        return List.copyOf(destinations.getOrDefault(new Destination(team, role, facility), Set.of()));
    }

    public CompoundTag remaining(UUID operation) {
        return pending.get(operation).copy();
    }

    public boolean deliver(Hk3WorldBubbleLedger ledger, Hk3WorldBubbleLedger.Transaction tx,
            Hk3WorldOutputPorts ports, Runnable changed) {
        if (delivering) return false;
        delivering = true;
        try { return deliverRemaining(ledger, tx, ports, changed); }
        finally { delivering = false; }
    }

    private boolean deliverRemaining(Hk3WorldBubbleLedger ledger, Hk3WorldBubbleLedger.Transaction tx,
            Hk3WorldOutputPorts ports, Runnable changed) {
        var output = pending.get(tx.id());
        for (var raw : output.getList("Items", Tag.TAG_COMPOUND)) deliverItem((CompoundTag) raw, ports, changed);
        for (var raw : output.getList("Fluids", Tag.TAG_COMPOUND)) {
            var fluid = (CompoundTag) raw;
            int amount = fluid.getInt("Amount");
            if (amount == 0) continue;
            var id = new ResourceLocation(fluid.getString("id"));
            if (!ForgeRegistries.FLUIDS.containsKey(id)) continue;
            var saved = fluid.getCompound("StackData").copy();
            saved.putString("FluidName", id.toString()); saved.putLong("Amount", amount);
            var stack = FluidStack.loadFromTag(saved);
            for (var target : ports.fluids()) {
                fill(target, stack, fluid, changed);
                stack.setAmount(fluid.getInt("Amount"));
                if (stack.isEmpty()) break;
            }
            for (var target : ports.aeFluids()) {
                if (stack.isEmpty()) break;
                var left = target.meHandleRecipeOutputInner(new ArrayList<>(List.of(FluidIngredient.of(stack))), false);
                long remaining = left == null ? 0 : left.stream().mapToLong(FluidIngredient::getAmount).sum();
                fluid.putInt("Amount", (int) remaining); stack.setAmount(remaining);
                changedME(target, changed);
            }
        }
        if (empty(output, "Items", "Count") && empty(output, "Fluids", "Amount")) {
            pending.remove(tx.id());
            destinations.computeIfPresent(destination(tx.receipt()), (key, operations) -> {
                operations.remove(tx.id()); return operations.isEmpty() ? null : operations;
            });
            ledger.acknowledge(tx.id(), tx.actor()); changed.run();
            return true;
        }
        return false;
    }

    static void deliverItem(CompoundTag item, Hk3WorldOutputPorts ports, Runnable changed) {
        int count = item.getInt("Count");
        if (count == 0) return;
        var id = new ResourceLocation(item.getString("id"));
        if (!ForgeRegistries.ITEMS.containsKey(id)) return;
        var saved = item.getCompound("StackData").copy();
        saved.putString("id", id.toString()); saved.putByte("Count", (byte) 1);
        var stack = ItemStack.of(saved); stack.setCount(count);
        if (stack.getItem() instanceof Hk3StackableWorldItem) stack.removeTagKey("Source");
        else if (item.hasUUID("Source")) stack.getOrCreateTag().putUUID("Source", item.getUUID("Source"));
        for (var target : ports.items()) {
            for (int slot = 0; slot < target.getSlots(); slot++) {
                insert(target, slot, stack, item, changed);
                stack.setCount(item.getInt("Count"));
                if (stack.isEmpty()) return;
            }
        }
        for (var target : ports.aeItems()) {
            var left = target.meHandleRecipeOutputInner(new ArrayList<>(List.of(SizedIngredient.create(stack))), false);
            int remaining = left == null ? 0 : left.stream().mapToInt(value -> value.getItems()[0].getCount()).sum();
            item.putInt("Count", remaining); stack.setCount(remaining);
            changedME(target, changed);
            if (stack.isEmpty()) return;
        }
    }

    private static void changedME(NotifiableMERecipeHandlerTrait<?, ?> target, Runnable changed) {
        var machine = target.getMachine();
        if (machine instanceof MEPatternBufferProxyPartMachine proxy) machine = proxy.getBuffer();
        machine.getHolder().getSelf().setChanged(); changed.run();
        ((IMEIOPartMachine) machine).getMETrait().notifySelfIO();
    }

    private static void insert(NotifiableItemStackHandler target, int slot, ItemStack stack,
            CompoundTag remaining, Runnable changed) {
        int before = itemCount(target.getStackInSlot(slot), stack);
        int accepted = 0;
        boolean returned = false;
        try {
            accepted = stack.getCount() - target.insertItemInternal(slot, stack.copy(), false).getCount();
            returned = true;
        } finally {
            // 外部仓通知可能在写入后抛错，仍扣除本次可观察到的真实入仓量。
            if (!returned) accepted = Math.min(stack.getCount(), Math.max(0, itemCount(target.getStackInSlot(slot), stack) - before));
            if (accepted > 0) {
                remaining.putInt("Count", remaining.getInt("Count") - accepted); changed.run();
            }
        }
    }

    private static int itemCount(ItemStack actual, ItemStack expected) {
        return ItemStack.isSameItemSameTags(actual, expected) ? actual.getCount() : 0;
    }

    private static void fill(NotifiableFluidTank target, FluidStack stack, CompoundTag remaining, Runnable changed) {
        long before = fluidAmount(target, stack);
        long accepted = 0;
        boolean returned = false;
        try {
            accepted = target.fillInternal(stack.copy(), false);
            returned = true;
        } finally {
            if (!returned) accepted = Math.min(stack.getAmount(), Math.max(0, fluidAmount(target, stack) - before));
            if (accepted > 0) {
                remaining.putInt("Amount", remaining.getInt("Amount") - (int) accepted); changed.run();
            }
        }
    }

    private static long fluidAmount(NotifiableFluidTank target, FluidStack expected) {
        long amount = 0;
        for (int i = 0; i < target.getTanks(); i++) {
            var actual = target.getFluidInTank(i);
            if (actual.isFluidEqual(expected)) amount += actual.getAmount();
        }
        return amount;
    }

    private static Destination destination(CompoundTag receipt) {
        return new Destination(receipt.hasUUID("Team") ? receipt.getUUID("Team") : null,
                receipt.getString("Role"), receipt.getString("Facility"));
    }

    private static boolean empty(CompoundTag output, String list, String amount) {
        return output.getList(list, Tag.TAG_COMPOUND).stream().allMatch(raw -> ((CompoundTag) raw).getInt(amount) == 0);
    }

    private static CompoundTag contents(CompoundTag receipt) {
        var outputs = receipt.getCompound("Outputs");
        var items = new ListTag(); var fluids = new ListTag();
        for (var raw : outputs.getList("ResourcePackages", Tag.TAG_COMPOUND)) {
            var pack = (CompoundTag) raw;
            for (var item : pack.getList("Items", Tag.TAG_COMPOUND)) items.add(item.copy());
            for (var fluid : pack.getList("Fluids", Tag.TAG_COMPOUND)) fluids.add(fluid.copy());
        }
        for (var reward : outputs.getList("MissionRewards", Tag.TAG_COMPOUND)) items.add(reward.copy());
        for (var token : outputs.getList("Tokens", Tag.TAG_COMPOUND)) items.add(token.copy());
        var result = new CompoundTag(); result.put("Items", items); result.put("Fluids", fluids); return result;
    }

    public CompoundTag save() {
        var result = new CompoundTag(); result.putInt("Version", 2); var entries = new ListTag();
        pending.forEach((id, output) -> {
            var entry = output.copy(); entry.putUUID("Operation", id); entries.add(entry);
        });
        result.put("Entries", entries); return result;
    }

    public static Hk3WorldResourceOutput load(CompoundTag tag, Hk3WorldBubbleLedger ledger) {
        if (!tag.contains("Version", Tag.TAG_INT) || tag.getInt("Version") < 1 || tag.getInt("Version") > 2
                || !tag.contains("Entries", Tag.TAG_LIST)) throw new IllegalArgumentException("Invalid world output buffer");
        var result = new Hk3WorldResourceOutput(); var entries = tag.getList("Entries", Tag.TAG_COMPOUND);
        if (entries.size() != ((ListTag) tag.get("Entries")).size()) throw new IllegalArgumentException("Invalid world output entries");
        for (var raw : entries) {
            var entry = (CompoundTag) raw;
            if (!entry.hasUUID("Operation")) throw new IllegalArgumentException("Missing output operation");
            UUID id = entry.getUUID("Operation"); var tx = ledger.transaction(id);
            if (tx == null || tx.phase() != Hk3WorldBubbleLedger.Phase.SETTLED || tx.delivered()
                    || result.pending.containsKey(id)) throw new IllegalArgumentException("Invalid pending output transaction");
            var expected = contents(tx.receipt());
            validate(entry, expected, "Items", "Count"); validate(entry, expected, "Fluids", "Amount");
            var output = new CompoundTag(); output.put("Items", entry.getList("Items", Tag.TAG_COMPOUND).copy());
            output.put("Fluids", entry.getList("Fluids", Tag.TAG_COMPOUND).copy()); result.pending.put(id, output);
            result.destinations.computeIfAbsent(destination(tx.receipt()), key -> new LinkedHashSet<>()).add(id);
        }
        for (var tx : ledger.settledTransactions()) {
            if (tx.delivered()) continue;
            if (tag.getInt("Version") == 2 && !result.pending.containsKey(tx.id()))
                throw new IllegalArgumentException("已结算世界泡批次缺少待交付余量");
            result.stage(tx);
        }
        return result;
    }

    private static void validate(CompoundTag saved, CompoundTag expected, String name, String quantity) {
        if (!saved.contains(name, Tag.TAG_LIST)) throw new IllegalArgumentException("Missing remaining " + name);
        var actual = saved.getList(name, Tag.TAG_COMPOUND); var source = expected.getList(name, Tag.TAG_COMPOUND);
        if (actual.size() != ((ListTag) saved.get(name)).size() || actual.size() != source.size())
            throw new IllegalArgumentException("Changed world output entries");
        for (int i = 0; i < actual.size(); i++) {
            var row = actual.getCompound(i); var original = source.getCompound(i);
            if (!row.contains(quantity, Tag.TAG_INT) || row.getInt(quantity) < 0 || row.getInt(quantity) > original.getInt(quantity))
                throw new IllegalArgumentException("Invalid remaining world output");
            var identity = row.copy(); identity.putInt(quantity, original.getInt(quantity));
            if (!identity.equals(original)) throw new IllegalArgumentException("Changed world output identity");
        }
    }
}
