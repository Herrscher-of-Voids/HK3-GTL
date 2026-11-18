package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.stacks.AEKey;
import appeng.api.stacks.AEItemKey;
import com.sirin.hk3gtl.common.research.Hk3ResearchPaymentJournal;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.SharedConstants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.storage.LevelResource;

import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public final class Hk3ProbabilityOrderData extends SavedData {
    private static final String NAME = "hk3gtl_ae_probability_orders_v1";
    final Map<UUID, Entry> entries = new LinkedHashMap<>();
    final Map<UUID, Group> groups = new LinkedHashMap<>();
    final Map<Location, Entry> controllers = new HashMap<>();
    final Map<Location, Entry> assemblies = new HashMap<>();

    record Location(String dimension, long position) {}

    enum Phase { IDLE, TRANSFERRING, LOADED, STARTING, RUNNING, ROLLING, DELIVERING, COMPLETED, STOPPED, UNKNOWN }

    static final class Group {
        UUID id, owner;
        BigInteger attemptLimit;
        final List<UUID> routes = new ArrayList<>();
        final Map<AEKey, BigInteger> goals = new LinkedHashMap<>();
        boolean paused, cancelled;
    }

    static final class Entry {
        UUID id, owner, team, machineIdentity, assemblyIdentity, group, supplyOrder;
        String dimension, recipeId;
        long controller, assembly;
        int slot;
        AEKey target;
        CompoundTag recipe, pattern;
        Hk3ExactProbabilityLedger<AEKey> ledger;
        final Map<AEKey, Long> inputs = new LinkedHashMap<>();
        final Map<AEKey, Long> machineInputs = new LinkedHashMap<>();
        final Map<AEItemKey, Long> containerInputs = new LinkedHashMap<>();
        final Map<AEKey, Long> returnedContainers = new LinkedHashMap<>();
        final Map<AEKey, BigInteger> goals = new LinkedHashMap<>();
        final Map<AEKey, BigInteger> actualOutputs = new LinkedHashMap<>();
        final Map<AEKey, BigInteger> escrow = new LinkedHashMap<>();
        Phase phase = Phase.IDLE;
        boolean paused, released;
        String note = "等待真实投料";

        boolean satisfied() {
            return goals.entrySet().stream().allMatch(goal ->
                    actualOutputs.getOrDefault(goal.getKey(), BigInteger.ZERO).compareTo(goal.getValue()) >= 0);
        }

        Hk3ExactProbabilityLedger.Status status() {
            return ledger.status(satisfied());
        }
    }

    static Hk3ProbabilityOrderData get(MinecraftServer server) {
        return Hk3SavedDataGuard.get(server, NAME, Hk3ProbabilityOrderData::load, Hk3ProbabilityOrderData::new);
    }

    void add(Entry entry) {
        entries.put(entry.id, entry);
        setReleased(entry, entry.released);
    }

    void setReleased(Entry entry, boolean released) {
        entry.released = released;
        var controller = new Location(entry.dimension, entry.controller);
        var assembly = new Location(entry.dimension, entry.assembly);
        if (released) {
            controllers.remove(controller, entry);
            assemblies.remove(assembly, entry);
        } else {
            controllers.put(controller, entry);
            assemblies.put(assembly, entry);
        }
    }

    void remove(UUID id) {
        var entry = entries.remove(id);
        controllers.remove(new Location(entry.dimension, entry.controller), entry);
        assemblies.remove(new Location(entry.dimension, entry.assembly), entry);
    }

    private static Hk3ProbabilityOrderData load(CompoundTag root) {
        Hk3ProbabilityOrderData data = new Hk3ProbabilityOrderData();
        for (Tag element : root.getList("Orders", Tag.TAG_COMPOUND)) {
            CompoundTag tag = (CompoundTag) element;
            Entry entry = new Entry();
            entry.id = tag.getUUID("Id");
            if (tag.hasUUID("Group")) entry.group = tag.getUUID("Group");
            if (tag.hasUUID("SupplyOrder")) entry.supplyOrder = tag.getUUID("SupplyOrder");
            entry.owner = tag.getUUID("Owner");
            entry.team = tag.getUUID("Team");
            entry.machineIdentity = tag.getUUID("MachineIdentity");
            entry.assemblyIdentity = tag.getUUID("AssemblyIdentity");
            entry.dimension = tag.getString("Dimension");
            entry.controller = tag.getLong("Controller");
            entry.assembly = tag.getLong("Assembly");
            entry.slot = tag.getInt("Slot");
            entry.recipeId = tag.getString("RecipeId");
            entry.recipe = tag.getCompound("Recipe");
            entry.pattern = tag.getCompound("Pattern");
            entry.target = AEKey.fromTagGeneric(tag.getCompound("TargetKey"));
            for (Tag input : tag.getList("Inputs", Tag.TAG_COMPOUND)) {
                CompoundTag row = (CompoundTag) input;
                entry.inputs.put(AEKey.fromTagGeneric(row.getCompound("Key")), row.getLong("Amount"));
            }
            if (tag.contains("MachineInputs")) {
                for (Tag input : tag.getList("MachineInputs", Tag.TAG_COMPOUND)) {
                    CompoundTag row = (CompoundTag) input;
                    entry.machineInputs.put(AEKey.fromTagGeneric(row.getCompound("Key")), row.getLong("Amount"));
                }
                for (Tag input : tag.getList("ContainerInputs", Tag.TAG_COMPOUND)) {
                    CompoundTag row = (CompoundTag) input;
                    entry.containerInputs.put((AEItemKey) AEKey.fromTagGeneric(row.getCompound("Key")), row.getLong("Amount"));
                }
                for (Tag output : tag.getList("ReturnedContainers", Tag.TAG_COMPOUND)) {
                    CompoundTag row = (CompoundTag) output;
                    entry.returnedContainers.put(AEKey.fromTagGeneric(row.getCompound("Key")), row.getLong("Amount"));
                }
            } else entry.machineInputs.putAll(entry.inputs);
            Map<AEKey, BigInteger> costs = new LinkedHashMap<>(), caps = new LinkedHashMap<>();
            BigInteger limit = attemptCount(tag, "AttemptLimit");
            BigInteger capacity = tag.contains("Capacity") ? integer(tag, "Capacity") : limit;
            entry.inputs.forEach((key, amount) -> {
                costs.put(key, BigInteger.valueOf(amount));
                caps.put(key, BigInteger.valueOf(amount).multiply(capacity));
            });
            var plan = new Hk3ExactProbabilityPlan<>(tag.getString("Metadata"), integer(tag, "Target"),
                    integer(tag, "Chance"), integer(tag, "ChanceScale"), integer(tag, "Yield"), costs, caps, limit, 1);
            Hk3ExactProbabilityLedger.Pending pending = tag.hasUUID("Pending")
                    ? new Hk3ExactProbabilityLedger.Pending(tag.getUUID("Pending"), plan.metadataId(), 1) : null;
            Hk3ExactProbabilityLedger.Receipt receipt = tag.hasUUID("Receipt")
                    ? new Hk3ExactProbabilityLedger.Receipt(tag.getUUID("Receipt"), plan.metadataId(), 1,
                            integer(tag, "ReceiptOutput")) : null;
            entry.ledger = Hk3ExactProbabilityLedger.restore(new Hk3ExactProbabilityLedger.Snapshot<>(
                    plan, attemptCount(tag, "Allocated"), integer(tag, "Actual"), pending, receipt, tag.getBoolean("Cancelled")));
            if (tag.contains("Goals")) {
                for (Tag goal : tag.getList("Goals", Tag.TAG_COMPOUND)) {
                    CompoundTag row = (CompoundTag) goal;
                    AEKey key = AEKey.fromTagGeneric(row.getCompound("Key"));
                    entry.goals.put(key, integer(row, "Amount"));
                    entry.actualOutputs.put(key, integer(row, "Actual"));
                }
            } else {
                entry.goals.put(entry.target, plan.target());
                entry.actualOutputs.put(entry.target, integer(tag, "Actual"));
            }
            for (Tag output : tag.getList("Escrow", Tag.TAG_COMPOUND)) {
                CompoundTag row = (CompoundTag) output;
                entry.escrow.put(AEKey.fromTagGeneric(row.getCompound("Key")), integer(row, "Amount"));
            }
            entry.phase = Phase.valueOf(tag.getString("Phase"));
            entry.released = tag.getBoolean("Released");
            entry.paused = true;
            entry.note = "重载后暂停；需以原机器令牌及独占槽位证据恢复，未知事务不得重投";
            data.add(entry);
        }
        for (Tag element : root.getList("Groups", Tag.TAG_COMPOUND)) {
            CompoundTag tag = (CompoundTag) element;
            Group group = new Group();
            group.id = tag.getUUID("Id");
            group.owner = tag.getUUID("Owner");
            group.attemptLimit = integer(tag, "AttemptLimit");
            group.cancelled = tag.getBoolean("Cancelled");
            group.paused = true;
            for (Tag route : tag.getList("Routes", Tag.TAG_COMPOUND))
                group.routes.add(((CompoundTag) route).getUUID("Id"));
            for (Tag goal : tag.getList("Goals", Tag.TAG_COMPOUND)) {
                CompoundTag row = (CompoundTag) goal;
                group.goals.put(AEKey.fromTagGeneric(row.getCompound("Key")), integer(row, "Amount"));
            }
            data.groups.put(group.id, group);
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag root) {
        ListTag orders = new ListTag();
        for (Entry entry : entries.values()) {
            CompoundTag tag = new CompoundTag();
            tag.putUUID("Id", entry.id);
            if (entry.group != null) tag.putUUID("Group", entry.group);
            if (entry.supplyOrder != null) tag.putUUID("SupplyOrder", entry.supplyOrder);
            tag.putUUID("Owner", entry.owner);
            tag.putUUID("Team", entry.team);
            tag.putUUID("MachineIdentity", entry.machineIdentity);
            tag.putUUID("AssemblyIdentity", entry.assemblyIdentity);
            tag.putString("Dimension", entry.dimension);
            tag.putLong("Controller", entry.controller);
            tag.putLong("Assembly", entry.assembly);
            tag.putInt("Slot", entry.slot);
            tag.putString("RecipeId", entry.recipeId);
            tag.put("Recipe", entry.recipe);
            tag.put("Pattern", entry.pattern);
            tag.put("TargetKey", entry.target.toTagGeneric());
            ListTag inputs = new ListTag();
            entry.inputs.forEach((key, amount) -> {
                CompoundTag row = new CompoundTag();
                row.put("Key", key.toTagGeneric());
                row.putLong("Amount", amount);
                inputs.add(row);
            });
            tag.put("Inputs", inputs);
            tag.put("MachineInputs", quantities(entry.machineInputs));
            tag.put("ContainerInputs", quantities(entry.containerInputs));
            tag.put("ReturnedContainers", quantities(entry.returnedContainers));
            ListTag goals = new ListTag();
            entry.goals.forEach((key, amount) -> {
                CompoundTag row = new CompoundTag();
                row.put("Key", key.toTagGeneric());
                number(row, "Amount", amount);
                number(row, "Actual", entry.actualOutputs.getOrDefault(key, BigInteger.ZERO));
                goals.add(row);
            });
            tag.put("Goals", goals);
            var snapshot = entry.ledger.snapshot();
            var plan = snapshot.plan();
            tag.putString("Metadata", plan.metadataId());
            number(tag, "Target", plan.target());
            number(tag, "Chance", plan.chance());
            number(tag, "ChanceScale", plan.chanceScale());
            number(tag, "Yield", plan.successYield());
            number(tag, "AttemptLimit", plan.attemptLimit());
            number(tag, "Capacity", plan.attemptCapacity());
            number(tag, "Allocated", snapshot.allocatedAttempts());
            number(tag, "Actual", snapshot.actualOutput());
            if (snapshot.pending() != null) tag.putUUID("Pending", snapshot.pending().token());
            if (snapshot.lastReceipt() != null) {
                tag.putUUID("Receipt", snapshot.lastReceipt().token());
                number(tag, "ReceiptOutput", snapshot.lastReceipt().actualOutput());
            }
            tag.putBoolean("Cancelled", snapshot.cancelled());
            ListTag escrow = new ListTag();
            entry.escrow.forEach((key, amount) -> {
                CompoundTag row = new CompoundTag();
                row.put("Key", key.toTagGeneric());
                number(row, "Amount", amount);
                escrow.add(row);
            });
            tag.put("Escrow", escrow);
            tag.putString("Phase", entry.phase.name());
            tag.putBoolean("Released", entry.released);
            orders.add(tag);
        }
        root.put("Orders", orders);
        ListTag groups = new ListTag();
        for (Group group : this.groups.values()) {
            CompoundTag tag = new CompoundTag();
            tag.putUUID("Id", group.id);
            tag.putUUID("Owner", group.owner);
            number(tag, "AttemptLimit", group.attemptLimit);
            tag.putBoolean("Cancelled", group.cancelled);
            ListTag routes = new ListTag();
            group.routes.forEach(id -> {
                CompoundTag route = new CompoundTag();
                route.putUUID("Id", id);
                routes.add(route);
            });
            tag.put("Routes", routes);
            ListTag goals = new ListTag();
            group.goals.forEach((key, amount) -> {
                CompoundTag goal = new CompoundTag();
                goal.put("Key", key.toTagGeneric());
                number(goal, "Amount", amount);
                goals.add(goal);
            });
            tag.put("Goals", goals);
            groups.add(tag);
        }
        root.put("Groups", groups);
        return root;
    }

    void checkpoint(MinecraftServer server) throws IOException {
        setDirty();
        CompoundTag envelope = new CompoundTag();
        envelope.put("data", save(new CompoundTag()));
        envelope.putInt("DataVersion", SharedConstants.getCurrentVersion().getDataVersion().getVersion());
        Hk3ResearchPaymentJournal.write(server.getWorldPath(LevelResource.ROOT).resolve("data").resolve(NAME + ".dat"), envelope);
    }

    private static BigInteger attemptCount(CompoundTag tag, String key) {
        return tag.contains(key, Tag.TAG_LONG) ? BigInteger.valueOf(tag.getLong(key)) : integer(tag, key);
    }

    private static BigInteger integer(CompoundTag tag, String key) {
        return new BigInteger(tag.getByteArray(key));
    }

    private static void number(CompoundTag tag, String key, BigInteger value) {
        tag.putByteArray(key, value.toByteArray());
    }

    private static ListTag quantities(Map<? extends AEKey, Long> values) {
        ListTag list = new ListTag();
        values.forEach((key, amount) -> {
            CompoundTag row = new CompoundTag();
            row.put("Key", key.toTagGeneric());
            row.putLong("Amount", amount);
            list.add(row);
        });
        return list;
    }
}
