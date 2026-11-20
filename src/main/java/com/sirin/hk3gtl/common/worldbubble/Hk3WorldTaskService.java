package com.sirin.hk3gtl.common.worldbubble;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient;
import com.sirin.hk3gtl.common.machine.ParallelData;
import com.sirin.hk3gtl.common.machine.research.Hk3LateIndustrialMachine;
import com.sirin.hk3gtl.common.research.Hk3ProcessReceipts;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.common.crafting.StrictNBTIngredient;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.NotifiableMERecipeHandlerTrait;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.function.BooleanSupplier;
import java.util.stream.Collectors;

public final class Hk3WorldTaskService {
    private static final String OPERATION = "hk3gtlWorldOperation";
    public static final String BUBBLE = "located_real_world_bubble";
    private static final String BUBBLE_CONSUMED = "BubbleConsumed";
    private static final String OPERATIONS = "hk3gtlWorldOperations";
    private static final String BATCHES = "hk3gtlWorldBatches";
    private static final String OWNER = "hk3gtlWorldOwner", TEAM = "hk3gtlWorldTeam";
    private static final String COMPLETION_TICK = "hk3gtlWorldCompletionTick";
    private static final Set<String> ROLES = Set.of("I25", "I26", "I27", "I28", "I29", "I30", "I31");

    private Hk3WorldTaskService() {}
    private static Hk3WorldBubbleData data(Hk3LateIndustrialMachine machine) {
        return Hk3WorldBubbleData.get(machine.getLevel().getServer());
    }
    private static Hk3WorldBubbleLedger.Domain domain(String role) {
        return role.equals("I30") || role.equals("I31")
                ? Hk3WorldBubbleLedger.Domain.SIMULATED : Hk3WorldBubbleLedger.Domain.REAL;
    }
    private static Hk3WorldBubbleLedger.Action action(String role) {
        return switch (role) {
            case "I26" -> Hk3WorldBubbleLedger.Action.MINE;
            case "I27" -> Hk3WorldBubbleLedger.Action.CAPTURE;
            case "I28" -> Hk3WorldBubbleLedger.Action.TERMINATE_REAL;
            case "I30" -> Hk3WorldBubbleLedger.Action.STABILIZE_SIMULATION;
            case "I31" -> Hk3WorldBubbleLedger.Action.TERMINATE_SIMULATION;
            default -> throw new IllegalArgumentException("非目标操作：" + role);
        };
    }
    public static boolean creates(String role) { return role.equals("I25") || role.equals("I29"); }

    private static void addBubble(Map<UUID, ItemStack> inputs, Object value) {
        if (value instanceof ItemStack stack && stack.is(Hk3IndustrialContent.items().get(BUBBLE).get())
                && stack.hasTag() && stack.getTag().hasUUID("Source")) inputs.putIfAbsent(stack.getTag().getUUID("Source"), stack);
    }

    private static Map<UUID, ItemStack> miningInputs(Hk3LateIndustrialMachine machine) {
        var inputs = new LinkedHashMap<UUID, ItemStack>();
        for (var io : List.of(IO.IN, IO.BOTH)) {
            for (var handler : machine.getCapabilitiesProxy().row(io).getOrDefault(ItemRecipeCapability.CAP, List.of())) {
                for (var stack : handler.getContents()) addBubble(inputs, stack);
            }
        }
        for (var part : machine.getParts()) {
            if (!(part instanceof MetaMachine meta)) continue;
            for (var trait : meta.getTraits()) {
                if (!(trait instanceof NotifiableMERecipeHandlerTrait<?, ?> handler)
                        || handler.getCapability() != ItemRecipeCapability.CAP
                        || handler.getIo() != IO.IN && handler.getIo() != IO.BOTH) continue;
                for (int slot : handler.getActiveSlots()) {
                    for (var stack : handler.getSingleSlotStackMap(slot).keySet()) addBubble(inputs, stack);
                }
            }
        }
        return inputs;
    }

    private static List<UUID> targets(Hk3LateIndustrialMachine machine) {
        var world = data(machine); var ledger = world.ledger(); String role = machine.researchRole();
        if (domain(role) == Hk3WorldBubbleLedger.Domain.SIMULATED) {
            var state = role.equals("I30") ? Hk3WorldBubbleLedger.SimulationState.CREATED : Hk3WorldBubbleLedger.SimulationState.STABLE;
            return ledger.simulations().stream().filter(s -> s.state() == state
                            && s.creationReceipt().hasUUID("Team")
                            && machine.getResearchTeamUUID().equals(s.creationReceipt().getUUID("Team"))
                            && !ledger.reserved(domain(role), s.id()))
                    .map(Hk3WorldBubbleLedger.SimulationSnapshot::id).toList();
        }
        var captured = role.equals("I28") ? ledger.settledTransactions().stream()
                .filter(tx -> tx.action() == Hk3WorldBubbleLedger.Action.CAPTURE
                        && tx.receipt().hasUUID("Team")
                        && machine.getResearchTeamUUID().equals(tx.receipt().getUUID("Team")))
                .map(Hk3WorldBubbleLedger.Transaction::target).collect(Collectors.toSet()) : Set.<UUID>of();
        var routes = world.routes(machine.getResearchTeamUUID());
        boolean mining = role.equals("I26");
        var inputs = mining ? miningInputs(machine).keySet() : Set.<UUID>of();
        var result = new ArrayList<UUID>();
        for (UUID id : routes) {
            if (mining && !inputs.contains(id)) continue;
            var snapshot = ledger.real(id);
            boolean eligible = role.equals("I28") ? snapshot.state() == Hk3WorldBubbleLedger.RealState.CAPTURED
                    && captured.contains(id)
                    : snapshot.state() == Hk3WorldBubbleLedger.RealState.AVAILABLE
                    && (!mining || snapshot.miningCount() < Hk3WorldBubbleLedger.MAX_MINING);
            if (eligible && !ledger.reserved(domain(role), id)) result.add(id);
        }
        return result;
    }
    public static long maxParallel(Hk3LateIndustrialMachine machine) {
        if (machine.getOwnerUUID() == null || machine.getResearchTeamUUID() == null) return 0;
        return creates(machine.researchRole()) ? Integer.MAX_VALUE : targets(machine).size();
    }
    private static CompoundTag batch(GTRecipe original, long count) {
        var result = new CompoundTag(); result.putLong("Count", count);
        result.put("Receipt", Hk3ProcessReceipts.snapshot(original)); return result;
    }
    public static void planned(GTRecipe running, GTRecipe original) {
        var batches = new ListTag(); batches.add(batch(original, 1));
        running.data = running.data.copy(); running.data.put(BATCHES, batches);
    }
    public static void planned(GTRecipe running, ParallelData plan) {
        var batches = new ListTag();
        for (int i = 0; i < plan.getOriginRecipeList().size(); i++) {
            long count = plan.getParallels()[i];
            if (count > 0) batches.add(batch(plan.getOriginRecipeList().get(i), count));
        }
        running.data = running.data.copy(); running.data.put(BATCHES, batches);
    }
    public static void reset(GTRecipe recipe) {
        recipe.data.remove(OPERATION); recipe.data.remove(OPERATIONS);
        recipe.data.remove(OWNER); recipe.data.remove(TEAM); recipe.data.remove(COMPLETION_TICK);
    }
    private static ListTag batches(GTRecipe recipe) {
        if (recipe.data.contains(BATCHES, Tag.TAG_LIST)) return recipe.data.getList(BATCHES, Tag.TAG_COMPOUND);
        var result = new ListTag(); result.add(batch(recipe, 1)); return result;
    }
    private static ListTag operations(GTRecipe recipe) {
        if (recipe.data.contains(OPERATIONS, Tag.TAG_LIST)) return recipe.data.getList(OPERATIONS, Tag.TAG_COMPOUND);
        var result = new ListTag();
        if (recipe.data.hasUUID(OPERATION)) {
            var legacy = batch(recipe, 1); legacy.putUUID(OPERATION, recipe.data.getUUID(OPERATION)); result.add(legacy);
        }
        return result;
    }
    private static UUID operation(CompoundTag batch, long index) {
        UUID group = batch.getUUID(OPERATION);
        return index == 0 ? group : UUID.nameUUIDFromBytes((group + "/" + index).getBytes(StandardCharsets.UTF_8));
    }
    public static boolean ready(Hk3LateIndustrialMachine machine) { return ready(machine, null); }
    public static boolean ready(Hk3LateIndustrialMachine machine, GTRecipe recipe) {
        String role = machine.researchRole();
        if (!ROLES.contains(role)) return true;
        if (machine.getOwnerUUID() == null || machine.getResearchTeamUUID() == null) return false;
        if (recipe != null && (recipe.data.contains(OPERATIONS) || recipe.data.hasUUID(OPERATION))) {
            if (recipe.data.contains(OPERATIONS) && (!machine.getOwnerUUID().equals(recipe.data.getUUID(OWNER))
                    || !machine.getResearchTeamUUID().equals(recipe.data.getUUID(TEAM)))) return false;
            if (creates(role)) return true;
            var ledger = data(machine).ledger();
            for (var raw : operations(recipe)) {
                var batch = (CompoundTag) raw;
                for (long i = 0; i < batch.getLong("Count"); i++) {
                    var tx = ledger.transaction(operation(batch, i));
                    if (tx == null || !tx.actor().equals(machine.getOwnerUUID())
                            || tx.phase() == Hk3WorldBubbleLedger.Phase.CANCELLED) return false;
                }
            }
            return true;
        }
        long count = recipe == null ? 1 : batches(recipe).stream().mapToLong(raw -> ((CompoundTag) raw).getLong("Count")).sum();
        return count <= maxParallel(machine);
    }
    private static boolean consumeMiningInputs(Hk3LateIndustrialMachine machine, GTRecipe recipe,
            List<UUID> targets, long count, BooleanSupplier consume) {
        var contents = recipe.getInputContents(ItemRecipeCapability.CAP);
        var original = List.copyOf(contents);
        var item = Hk3IndustrialContent.items().get(BUBBLE).get();
        var stacks = miningInputs(machine);
        contents.removeIf(content -> Arrays.stream(((Ingredient) content.getContent()).getItems()).anyMatch(stack -> stack.is(item)));
        for (int i = 0; i < count; i++) {
            var exact = SizedIngredient.create(StrictNBTIngredient.of(stacks.get(targets.get(i))), 1);
            contents.add(new Content(exact, 10_000, 10_000, 0, null, null));
        }
        boolean consumed = consume.getAsBoolean();
        contents.clear(); contents.addAll(original);
        return consumed;
    }

    private static CompoundTag token(String item, UUID target) {
        var token = new CompoundTag(); token.putString("id", "hk3gtl:" + item);
        token.putInt("Count", 1); token.putUUID("Source", target);
        return token;
    }

    public static boolean start(Hk3LateIndustrialMachine machine, GTRecipe recipe, BooleanSupplier consume) {
        if (!ready(machine, recipe)) return false;
        if (recipe.data.contains(OPERATIONS) || recipe.data.hasUUID(OPERATION)) return consume.getAsBoolean();
        String role = machine.researchRole();
        var targets = creates(role) ? List.<UUID>of() : targets(machine);
        var groups = batches(recipe).copy();
        boolean mining = role.equals("I26");
        long planned = groups.stream().mapToLong(raw -> ((CompoundTag) raw).getLong("Count")).sum();
        if (!(mining ? consumeMiningInputs(machine, recipe, targets, planned, consume) : consume.getAsBoolean())) return false;
        int targetIndex = 0; long count = 0;
        for (var raw : groups) {
            var batch = (CompoundTag) raw; batch.putUUID(OPERATION, UUID.randomUUID());
            count += batch.getLong("Count");
            if (mining) batch.putBoolean(BUBBLE_CONSUMED, true);
            if (creates(role)) continue;
            for (long i = 0; i < batch.getLong("Count"); i++)
                data(machine).ledger().begin(operation(batch, i), machine.getOwnerUUID(), domain(role), targets.get(targetIndex++), action(role));
        }
        recipe.data.put(OPERATIONS, groups);
        recipe.data.putUUID(OWNER, machine.getOwnerUUID()); recipe.data.putUUID(TEAM, machine.getResearchTeamUUID());
        com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(machine.getLevel().getServer())
                .produced(machine.getOwnerUUID(), "receipt:167", count);
        machine.markDirty();
        return true;
    }
    public static void completed(Hk3LateIndustrialMachine machine, GTRecipe recipe) {
        String role = machine.researchRole();
        if (!ROLES.contains(role)) return;
        if (!ready(machine, recipe)) throw new IllegalStateException("世界泡批次归属或任务状态已改变");
        var level = machine.getLevel(); var server = level.getServer(); var world = data(machine);
        var scope = machine.getResearchTeamUUID();
        if (!recipe.data.contains(COMPLETION_TICK)) {
            recipe.data.putLong(COMPLETION_TICK, level.getGameTime()); machine.markDirty();
        }
        try {
            for (var raw : operations(recipe)) {
                var batch = (CompoundTag) raw;
                for (long i = 0; i < batch.getLong("Count"); i++) {
                    UUID operation = operation(batch, i);
                    var receipt = Hk3ProcessReceipts.settle(batch.getCompound("Receipt"),
                            level.dimension().location() + "@" + machine.getPos(), recipe.data.getLong(COMPLETION_TICK));
                    receipt.putUUID("Batch", operation); receipt.putUUID("Team", scope); receipt.putString("Role", role);
                    if (role.equals("I25")) {
                        world.discoverRoute(server, scope, receipt);
                    } else if (role.equals("I29")) {
                        world.createCompleted(server, operation, machine.getOwnerUUID(), scope, receipt.getString("Facility"), receipt, false);
                    } else {
                        var tx = world.ledger().transaction(operation);
                        if (tx.phase() == Hk3WorldBubbleLedger.Phase.SETTLED) continue;
                        var tokens = new ListTag();
                        if (role.equals("I27")) tokens.add(token("sealed_real_world_bubble", tx.target()));
                        if (!tokens.isEmpty()) receipt.getCompound("Outputs").put("Tokens", tokens);
                        world.completeWithResources(server, operation, machine.getOwnerUUID(), scope, receipt, Hk3WorldRuntimeCatalog.get(server), false);
                    }
                }
            }
        } finally {
            if (!role.equals("I25")) world.projectCompleted(server, scope);
        }
    }
    public static void cancel(Hk3LateIndustrialMachine machine, GTRecipe recipe) {
        if (recipe == null || machine.isRemote()) return;
        var ledger = data(machine).ledger();
        for (var raw : operations(recipe)) {
            var batch = (CompoundTag) raw;
            for (long i = 0; i < batch.getLong("Count"); i++) {
                var tx = ledger.transaction(operation(batch, i));
                if (tx != null && tx.phase() == Hk3WorldBubbleLedger.Phase.RESERVED) {
                    ledger.cancel(tx.id(), tx.actor());
                    if (batch.getBoolean(BUBBLE_CONSUMED)) {
                        var stack = new ItemStack(Hk3IndustrialContent.items().get(BUBBLE).get());
                        stack.getOrCreateTag().putUUID("Source", tx.target());
                        Block.popResource(machine.getLevel(), machine.getPos(), stack);
                    }
                }
            }
        }
    }
}
