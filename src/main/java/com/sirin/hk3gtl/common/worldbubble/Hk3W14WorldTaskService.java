package com.sirin.hk3gtl.common.worldbubble;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.machine.Hk3RecipeCalculationHelper;
import com.sirin.hk3gtl.common.machine.ParallelData;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchProcessMachine;
import com.sirin.hk3gtl.common.research.Hk3ProcessReceipts;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.UUID;
import java.util.function.Function;

/** W14跨配方逐泡预留、完成结算和同目标生命周期。 */
public final class Hk3W14WorldTaskService {
    private static final String BATCHES = "hk3gtlW14Batches", OPERATIONS = "hk3gtlW14Operations";
    private static final String OWNER = "hk3gtlW14Owner", TEAM = "hk3gtlW14Team", TICK = "hk3gtlW14CompletionTick";
    private static final String OPERATION = "Operation";
    private Hk3W14WorldTaskService() {}

    private static Hk3WorldBubbleData data(Hk3ResearchProcessMachine machine) {
        return Hk3WorldBubbleData.get(machine.getLevel().getServer());
    }
    private static List<UUID> targets(Hk3ResearchProcessMachine machine, Hk3WorldBubbleLedger.SimulationState state) {
        var ledger = data(machine).ledger();
        return ledger.simulations().stream().filter(simulation -> simulation.state() == state
                        && simulation.creationReceipt().hasUUID("Team")
                        && machine.getResearchTeamUUID().equals(simulation.creationReceipt().getUUID("Team"))
                        && !ledger.reserved(Hk3WorldBubbleLedger.Domain.SIMULATED, simulation.id()))
                .map(Hk3WorldBubbleLedger.SimulationSnapshot::id).toList();
    }
    private static CompoundTag batch(GTRecipe recipe, long parallel) {
        var receipt = Hk3ProcessReceipts.snapshot(recipe);
        var process = Hk3W14WorldProcesses.of(receipt);
        var batch = new CompoundTag();
        batch.putLong("Count", Math.multiplyExact(parallel, process.bubbles()));
        batch.put("Receipt", receipt);
        return batch;
    }
    public static void planned(GTRecipe running, GTRecipe original) {
        var list = new ListTag(); var batch = batch(original, 1);
        if (batch.getLong("Count") > 0) list.add(batch);
        running.data = running.data.copy(); running.data.put(BATCHES, list);
    }
    public static void planned(GTRecipe running, ParallelData plan) {
        var list = new ListTag();
        for (int i = 0; i < plan.getOriginRecipeList().size(); i++) {
            var batch = batch(plan.getOriginRecipeList().get(i), plan.getParallels()[i]);
            if (batch.getLong("Count") > 0) list.add(batch);
        }
        running.data = running.data.copy(); running.data.put(BATCHES, list);
    }
    public static ParallelData limit(Hk3ResearchProcessMachine machine, ParallelData plan, Function<GTRecipe, GTRecipe> modifier) {
        var available = new EnumMap<Hk3WorldBubbleLedger.SimulationState, Long>(Hk3WorldBubbleLedger.SimulationState.class);
        for (var state : List.of(Hk3WorldBubbleLedger.SimulationState.CREATED, Hk3WorldBubbleLedger.SimulationState.STABLE))
            available.put(state, (long) targets(machine, state).size());
        var originals = new ArrayList<GTRecipe>(); var processed = new ArrayList<GTRecipe>(); var parallels = new ArrayList<Long>();
        for (int i = 0; i < plan.getOriginRecipeList().size(); i++) {
            var original = plan.getOriginRecipeList().get(i);
            var process = Hk3W14WorldProcesses.of(Hk3ProcessReceipts.snapshot(original));
            long count = plan.getParallels()[i]; var state = process.inputState();
            if (state != null) {
                count = Math.min(count, available.get(state) / process.bubbles());
                available.put(state, available.get(state) - count * process.bubbles());
            }
            if (count == 0) continue;
            originals.add(original); parallels.add(count);
            processed.add(count == plan.getParallels()[i] ? plan.getProcessedRecipeList().get(i)
                    : Hk3RecipeCalculationHelper.multipleRecipe(modifier.apply(original.copy()), count));
        }
        return originals.isEmpty() ? null : new ParallelData(originals, parallels.stream().mapToLong(Long::longValue).toArray(), false, processed);
    }
    public static void reset(GTRecipe recipe) {
        recipe.data.remove(OPERATIONS); recipe.data.remove(OWNER); recipe.data.remove(TEAM); recipe.data.remove(TICK);
    }
    private static ListTag batches(GTRecipe recipe) {
        if (recipe.data.contains(BATCHES, Tag.TAG_LIST)) return recipe.data.getList(BATCHES, Tag.TAG_COMPOUND);
        var list = new ListTag(); var batch = batch(recipe, 1);
        if (batch.getLong("Count") > 0) list.add(batch);
        return list;
    }
    private static UUID operation(CompoundTag batch, long index) {
        var group = batch.getUUID(OPERATION);
        return index == 0 ? group : derived(group, Long.toString(index));
    }
    private static UUID derived(UUID operation, String step) {
        return UUID.nameUUIDFromBytes((operation + "/" + step).getBytes(StandardCharsets.UTF_8));
    }
    public static boolean ready(Hk3ResearchProcessMachine machine, GTRecipe recipe) {
        var groups = batches(recipe);
        if (groups.isEmpty()) return true;
        if (machine.getOwnerUUID() == null || machine.getResearchTeamUUID() == null) return false;
        if (recipe.data.contains(OPERATIONS)) {
            if (!machine.getOwnerUUID().equals(recipe.data.getUUID(OWNER))
                    || !machine.getResearchTeamUUID().equals(recipe.data.getUUID(TEAM))) return false;
            var ledger = data(machine).ledger();
            for (var raw : recipe.data.getList(OPERATIONS, Tag.TAG_COMPOUND)) {
                var group = (CompoundTag) raw;
                if (Hk3W14WorldProcesses.of(group.getCompound("Receipt")).creates()) continue;
                for (long i = 0; i < group.getLong("Count"); i++) {
                    var tx = ledger.transaction(operation(group, i));
                    if (tx == null || !tx.actor().equals(machine.getOwnerUUID())
                            || tx.phase() == Hk3WorldBubbleLedger.Phase.CANCELLED) return false;
                }
            }
            return true;
        }
        var required = new EnumMap<Hk3WorldBubbleLedger.SimulationState, Long>(Hk3WorldBubbleLedger.SimulationState.class);
        for (var raw : groups) {
            var group = (CompoundTag) raw;
            var state = Hk3W14WorldProcesses.of(group.getCompound("Receipt")).inputState();
            if (state != null) required.merge(state, group.getLong("Count"), Long::sum);
        }
        return required.entrySet().stream().allMatch(entry -> entry.getValue() <= targets(machine, entry.getKey()).size());
    }
    public static void started(Hk3ResearchProcessMachine machine, GTRecipe recipe) {
        if (recipe.data.contains(OPERATIONS)) return;
        var groups = batches(recipe).copy();
        if (groups.isEmpty()) return;
        var ledger = data(machine).ledger();
        var candidates = new EnumMap<Hk3WorldBubbleLedger.SimulationState, List<UUID>>(Hk3WorldBubbleLedger.SimulationState.class);
        var offsets = new EnumMap<Hk3WorldBubbleLedger.SimulationState, Integer>(Hk3WorldBubbleLedger.SimulationState.class);
        for (var state : List.of(Hk3WorldBubbleLedger.SimulationState.CREATED, Hk3WorldBubbleLedger.SimulationState.STABLE)) {
            candidates.put(state, targets(machine, state)); offsets.put(state, 0);
        }
        long count = 0;
        for (var raw : groups) {
            var group = (CompoundTag) raw; group.putUUID(OPERATION, UUID.randomUUID());
            var process = Hk3W14WorldProcesses.of(group.getCompound("Receipt")); count += group.getLong("Count");
            if (process.creates()) continue;
            var state = process.inputState(); int offset = offsets.get(state);
            var action = switch (process.stage()) {
                case TERMINATE -> Hk3WorldBubbleLedger.Action.TERMINATE_SIMULATION;
                case DISCARD -> Hk3WorldBubbleLedger.Action.DISCARD_SIMULATION;
                default -> Hk3WorldBubbleLedger.Action.STABILIZE_SIMULATION;
            };
            for (long i = 0; i < group.getLong("Count"); i++)
                ledger.begin(operation(group, i), machine.getOwnerUUID(), Hk3WorldBubbleLedger.Domain.SIMULATED,
                        candidates.get(state).get(offset++), action);
            offsets.put(state, offset);
        }
        recipe.data.put(OPERATIONS, groups);
        recipe.data.putUUID(OWNER, machine.getOwnerUUID()); recipe.data.putUUID(TEAM, machine.getResearchTeamUUID());
        com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(machine.getLevel().getServer())
                .produced(machine.getOwnerUUID(), "receipt:167", count);
    }
    public static void completed(Hk3ResearchProcessMachine machine, GTRecipe recipe) {
        if (!recipe.data.contains(OPERATIONS)) return;
        if (!ready(machine, recipe)) throw new IllegalStateException("W14世界泡批次归属或任务状态已改变");
        var level = machine.getLevel(); var server = level.getServer(); var world = data(machine);
        if (!recipe.data.contains(TICK)) { recipe.data.putLong(TICK, level.getGameTime()); machine.markDirty(); }
        try {
            for (var raw : recipe.data.getList(OPERATIONS, Tag.TAG_COMPOUND)) {
                var group = (CompoundTag) raw; var process = Hk3W14WorldProcesses.of(group.getCompound("Receipt"));
                for (long i = 0; i < group.getLong("Count"); i++) {
                    UUID operation = operation(group, i);
                    UUID target = process.creates() ? operation : world.ledger().transaction(operation).target();
                    var receipt = Hk3ProcessReceipts.settle(group.getCompound("Receipt"),
                            level.dimension().location() + "@" + machine.getPos(), recipe.data.getLong(TICK));
                    receipt.putUUID("Team", machine.getResearchTeamUUID()); receipt.putString("Role", "W14");
                    receipt.putUUID("WorldTarget", target); receipt.putLong("WorldBubbleIndex", i);
                    if (process.creates()) {
                        var creation = receipt.copy(); creation.putUUID("Batch", target); creation.putString("WorldStage", "CREATE");
                        world.createCompleted(server, target, machine.getOwnerUUID(), machine.getResearchTeamUUID(),
                                creation.getString("Facility"), creation, false);
                    }
                    switch (process.stage()) {
                        case CREATE_STABLE -> settle(machine, derived(operation, "stabilize"), target,
                                Hk3WorldBubbleLedger.Action.STABILIZE_SIMULATION, receipt);
                        case STABILIZE -> settle(machine, operation, target, Hk3WorldBubbleLedger.Action.STABILIZE_SIMULATION, receipt);
                        case TERMINATE -> settle(machine, operation, target, Hk3WorldBubbleLedger.Action.TERMINATE_SIMULATION, receipt);
                        case STABILIZE_TERMINATE -> {
                            settle(machine, operation, target, Hk3WorldBubbleLedger.Action.STABILIZE_SIMULATION, receipt);
                            settle(machine, derived(operation, "terminate"), target, Hk3WorldBubbleLedger.Action.TERMINATE_SIMULATION, receipt);
                        }
                        case DISCARD -> settle(machine, operation, target, Hk3WorldBubbleLedger.Action.DISCARD_SIMULATION, receipt);
                        default -> {}
                    }
                }
            }
        } finally { world.projectCompleted(server, machine.getResearchTeamUUID()); }
    }
    private static void settle(Hk3ResearchProcessMachine machine, UUID operation, UUID target,
            Hk3WorldBubbleLedger.Action action, CompoundTag source) {
        var world = data(machine); var ledger = world.ledger(); var tx = ledger.transaction(operation);
        if (tx != null && tx.phase() == Hk3WorldBubbleLedger.Phase.SETTLED) return;
        ledger.begin(operation, machine.getOwnerUUID(), Hk3WorldBubbleLedger.Domain.SIMULATED, target, action);
        var receipt = source.copy(); receipt.putUUID("Batch", operation);
        receipt.putString("WorldStage", switch (action) {
            case STABILIZE_SIMULATION -> "STABILIZE";
            case TERMINATE_SIMULATION -> "TERMINATE";
            case DISCARD_SIMULATION -> "DISCARD";
            default -> throw new IllegalArgumentException("非模拟世界工序");
        });
        world.completeWithResources(machine.getLevel().getServer(), operation, machine.getOwnerUUID(), machine.getResearchTeamUUID(),
                receipt, Hk3WorldRuntimeCatalog.get(machine.getLevel().getServer()), false);
    }
    public static void cancel(Hk3ResearchProcessMachine machine, GTRecipe recipe) {
        if (recipe == null || machine.isRemote()) return;
        var ledger = data(machine).ledger();
        for (var raw : recipe.data.getList(OPERATIONS, Tag.TAG_COMPOUND)) {
            var group = (CompoundTag) raw;
            for (long i = 0; i < group.getLong("Count"); i++) {
                var operation = operation(group, i);
                for (var id : List.of(operation, derived(operation, "stabilize"), derived(operation, "terminate"))) {
                    var tx = ledger.transaction(id);
                    if (tx != null && tx.phase() == Hk3WorldBubbleLedger.Phase.RESERVED) ledger.cancel(id, tx.actor());
                }
            }
        }
    }
}
