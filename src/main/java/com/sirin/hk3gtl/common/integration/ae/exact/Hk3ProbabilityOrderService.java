package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.config.Actionable;
import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.IGrid;
import appeng.api.networking.crafting.ICraftingProvider;
import appeng.api.networking.security.IActionHost;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.*;
import appeng.me.service.CraftingService;
import com.gtlsupb.gtlsupb.api.item.tool.ae2.Ae2PatternHelper;
import com.sirin.hk3gtl.mixin.gtlcore.Hk3ProbabilityPatternSlot;
import com.gregtechceu.gtceu.api.capability.recipe.*;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.GTRecipeSerializer;
import com.gregtechceu.gtceu.api.recipe.chance.logic.ChanceLogic;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient;
import com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.Hk3RecipeLogic;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.research.Hk3ProductionOutput;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import com.sirin.hk3gtl.mixin.gtlcore.Hk3ProbabilitySlotAccess;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.fluids.FluidUtil;
import net.minecraftforge.fluids.capability.IFluidHandler;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.MEPatternBufferPartMachine;

import java.io.IOException;
import java.math.BigInteger;
import java.util.*;

import static com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderData.Phase;

public final class Hk3ProbabilityOrderService {
    private static final String TOKEN = "hk3ProbabilityToken";
    private static final String ORDER = "hk3ProbabilityOrder";
    private static final String SEQUENCE = "hk3ProbabilitySequence";
    private static MEPatternBufferPartMachine authorizedPush;

    private Hk3ProbabilityOrderService() {}

    public record Candidate(BlockPos controller, BlockPos assembly, int slot, String label) {}
    private record Target(AEKey key, int chance, int scale, long successYield, boolean rolled) {}
    private record Inputs(Map<AEKey, Long> costs, Map<AEKey, Long> machine,
                          Map<AEItemKey, Long> containers, Map<AEKey, Long> returned) {}
    private record Drain(AEFluidKey fluid, long amount, Map<AEKey, Long> returned) {}
    private record Selection(Hk3WorkableMultiblockMachine machine, MEPatternBufferPartMachine provider,
                             GTRecipe recipe, Inputs inputs, AEKey target, int chance, int scale, long successYield, boolean rolled) {}

    private static MEPatternBufferPartMachine assembly(Object candidate) {
        return candidate instanceof MEPatternBufferPartMachine provider && provider instanceof Hk3ProbabilityAssemblyAccess
                ? provider : null;
    }

    private static Hk3ProbabilityAssemblyAccess access(MEPatternBufferPartMachine provider) {
        return (Hk3ProbabilityAssemblyAccess) provider;
    }

    private static GTRecipe boundRecipe(MEPatternBufferPartMachine provider, int slot) {
        return Ae2PatternHelper.readBindingRecipe(provider.getPatternInventory().getStackInSlot(slot), provider.getLevel());
    }

    public record PatternOutputs(Set<AEKey> omitted, boolean probabilityPrimary) {
        public static final PatternOutputs FIXED = new PatternOutputs(Set.of(), false);
    }

    public static PatternOutputs patternOutputs(Iterable<?> providers, IPatternDetails pattern) {
        AEKey primary = pattern.getPrimaryOutput().what();
        Set<AEKey> omitted = null;
        boolean probabilityPrimary = false, fixedPrimary = false;
        for (var provider : providers) {
            var rolled = rolledOutputs(provider, pattern);
            if (rolled.contains(primary)) probabilityPrimary = true;
            else fixedPrimary = true;
            if (!rolled.isEmpty()) {
                if (omitted == null) omitted = new HashSet<>();
                omitted.addAll(rolled);
            }
        }
        if (omitted == null) return PatternOutputs.FIXED;
        if (fixedPrimary) omitted.remove(primary);
        return new PatternOutputs(omitted, probabilityPrimary);
    }

    public static Set<AEKey> rolledOutputs(Object provider, IPatternDetails pattern) {
        var assembly = assembly(provider);
        if (assembly == null) return Set.of();
        var slot = ((Hk3ProbabilityPatternSlot) assembly).hk3gtl$slot(pattern);
        if (slot == null) return Set.of();
        var recipe = boundRecipe(assembly, slot);
        return recipe == null ? Set.of() : rolledOutputs(recipe, pattern);
    }

    private static Set<AEKey> rolledOutputs(GTRecipe recipe, IPatternDetails pattern) {
        Set<AEKey> rolled = null;
        var encoded = pattern.getOutputs();
        for (var content : recipe.getOutputContents(ItemRecipeCapability.CAP)) if (content.chance < content.maxChance)
            for (var stack : ItemRecipeCapability.CAP.of(content.content).getItems()) for (var output : encoded)
                if (AEItemKey.matches(output.what(), stack)) {
                    if (rolled == null) rolled = new HashSet<>();
                    rolled.add(output.what());
                }
        for (var content : recipe.getOutputContents(FluidRecipeCapability.CAP)) if (content.chance < content.maxChance)
            for (var stack : FluidRecipeCapability.CAP.of(content.content).getStacks()) {
                var key = AEFluidKey.of(stack.getFluid(), stack.getTag());
                for (var output : encoded) if (key.equals(output.what())) {
                    if (rolled == null) rolled = new HashSet<>();
                    rolled.add(key);
                }
            }
        return rolled == null ? Set.of() : rolled;
    }

    public record NexusQuote(Candidate route, AEKey key, BigInteger amount, CompoundTag binding, String odds,
                             List<NexusQuote> supplies) {
        public void start(ServerPlayer player, IGrid grid, BigInteger attempts, BigInteger demand, UUID child, UUID parent, CompoundTag start) {
            start(player, grid, attempts, demand, child, parent, null, start);
        }

        private void start(ServerPlayer player, IGrid grid, BigInteger attempts, BigInteger demand, UUID child,
                           UUID parent, Hk3ProbabilityOrderData.Entry consumer, CompoundTag start) {
            var data = Hk3ProbabilityOrderData.get(player.server);
            if (data.entries.containsKey(child)) return;
            var level = player.server.getLevel(ResourceKey.create(Registries.DIMENSION, new ResourceLocation(binding.getString("Dimension"))));
            require(level != null, "绑定机器所在维度不可用");
            var selected = inspect(player, level, route.controller(), route.assembly(), route.slot(), key, true);
            require(selected.provider.getGrid() == grid, "总成已离开原网络");
            require(binding.equals(quote(route, selected)),
                    "机器、网络或样板已变化，请重新规划");
            var entry = registerSingle(player, selected, route.slot(), demand, attempts, Map.of(), child);
            entry.nexusParent = parent;
            supplies.forEach(quote -> entry.supplyRoutes.put(quote.key(), quote));
            if (consumer != null) { consumer.probabilitySupply = child; entry.supplyParent = consumer.id; }
            if (start != null) data.rememberStart(start);
            if (!persist(player.server, entry) && start != null) {
                data.startsByHost.get(start.getUUID("Host")).remove(parent);
                data.remove(child);
                throw new IllegalArgumentException("首批订单未能保存");
            }
            selected.machine.getRecipeLogic().updateTickSubscription();
        }

        public CompoundTag save() {
            var tag = new CompoundTag();
            tag.put("Binding", binding);
            tag.putByteArray("Amount", amount.toByteArray());
            if (!supplies.isEmpty()) {
                var list = new ListTag();
                supplies.forEach(quote -> list.add(quote.save()));
                tag.put("Supplies", list);
            }
            return tag;
        }

        public static NexusQuote read(CompoundTag tag) {
            var binding = tag.getCompound("Binding");
            var route = new Candidate(BlockPos.of(binding.getLong("Controller")), BlockPos.of(binding.getLong("Assembly")),
                    binding.getInt("Slot"), "");
            return new NexusQuote(route, AEKey.fromTagGeneric(binding.getCompound("Target")),
                    new BigInteger(tag.getByteArray("Amount")), binding, "", tag.getList("Supplies", net.minecraft.nbt.Tag.TAG_COMPOUND).stream()
                            .map(row -> read((CompoundTag) row)).toList());
        }

        public String description() {
            var text = new StringBuilder(key.getDisplayName().getString()).append("：").append(odds);
            text.append(" @ ").append(route.controller().toShortString());
            supplies.forEach(quote -> text.append('\n').append(quote.description()));
            return text.toString();
        }
    }

    public static List<NexusQuote> nexusQuotes(ServerPlayer player, IGrid grid, Map<AEKey, BigInteger> needs) {
        var search = new QuoteSearch(grid);
        Set<Hk3ProbabilityOrderData.Location> path = new HashSet<>();
        var routes = new ArrayList<NexusQuote>(needs.size());
        needs.forEach((key, amount) -> routes.add(nexusQuote(player, grid, key, amount, path, search, false)));
        return routes;
    }

    private static final class QuoteSearch {
        final CraftingService service;
        final Map<AEKey, Map<AEKey, Boolean>> cachedLeaves = new HashMap<>();
        final Map<AEKey, Inputs> inputs = new HashMap<>();
        record Inputs(boolean conditional, boolean deterministic, Set<AEKey> ingredients) {}
        int routes = 128, edges = 8192;

        QuoteSearch(IGrid grid) { service = (CraftingService) grid.getCraftingService(); }

        void visit() { require(--edges >= 0, "概率前置样板超过规划预算"); }
        boolean exhausted() { return edges < 0 || routes < 0; }

        private Inputs inspectInputs(AEKey key) {
            boolean conditional = false, deterministic = false;
            Set<AEKey> ingredients = new LinkedHashSet<>();
            for (var pattern : service.getCraftingFor(key)) {
                visit();
                boolean fixed = false;
                for (var provider : service.getProviders(pattern)) {
                    visit();
                    if (!rolledOutputs(provider, pattern).contains(key)) fixed = true;
                    else if (key.equals(pattern.getPrimaryOutput().what())) conditional = true;
                    if (fixed && conditional) break;
                }
                if (fixed) {
                    deterministic = true;
                    for (var ingredient : pattern.getInputs()) for (var stack : ingredient.getPossibleInputs()) {
                        visit();
                        ingredients.add(stack.what());
                    }
                }
            }
            return new Inputs(conditional, deterministic, ingredients);
        }

        Map<AEKey, Boolean> leaves(AEKey input) {
            var cached = cachedLeaves.get(input);
            if (cached != null) return cached;
            Map<AEKey, Boolean> leaves = new LinkedHashMap<>();
            Set<AEKey> seen = new HashSet<>();
            var queue = new ArrayDeque<AEKey>();
            queue.add(input);
            seen.add(input);
            while (!queue.isEmpty()) {
                var key = queue.removeFirst();
                var routes = inputs.computeIfAbsent(key, this::inspectInputs);
                if (routes.conditional()) leaves.put(key, !routes.deterministic());
                for (var ingredient : routes.ingredients()) if (seen.add(ingredient)) queue.addLast(ingredient);
            }
            cachedLeaves.put(input, leaves);
            return leaves;
        }
    }

    private static NexusQuote nexusQuote(ServerPlayer player, IGrid grid, AEKey target, BigInteger amount,
                                         Set<Hk3ProbabilityOrderData.Location> path, QuoteSearch search, boolean seed) {
        require(--search.routes >= 0, "概率路线超过可登记的机器数");
        String reason = "当前网络没有可为该产物提供逐批回执的绑定机器";
        for (var pattern : search.service.getCraftingFor(target)) {
            search.visit();
            if (!target.equals(pattern.getPrimaryOutput().what())) continue;
            for (var host : search.service.getProviders(pattern)) {
                search.visit();
                var provider = assembly(host);
                if (provider == null || provider.getControllers().size() != 1 || provider.getGrid() != grid) continue;
                var slot = ((Hk3ProbabilityPatternSlot) provider).hk3gtl$slot(pattern);
                if (slot == null) continue;
                var route = new Candidate(provider.getControllers().iterator().next().self().getPos(), provider.getPos(), slot, "");
                var level = (ServerLevel) provider.getLevel();
                var location = new Hk3ProbabilityOrderData.Location(level.dimension().location().toString(), route.controller().asLong());
                if (!path.add(location)) { reason = "概率路线缺少启动原料，无法重复占用同一控制器"; continue; }
                try {
                    var selected = inspect(player, level, route.controller(), route.assembly(), route.slot(), target, true);
                    if (!selected.rolled || seed && selected.inputs.costs.containsKey(target)) continue;
                    Map<AEKey, NexusQuote> supplies = new LinkedHashMap<>();
                    for (var input : selected.inputs.costs.entrySet()) {
                        long need = input.getValue() - grid.getStorageService().getInventory().extract(input.getKey(),
                                input.getValue(), Actionable.SIMULATE, IActionSource.ofPlayer(player));
                        for (var source : search.leaves(input.getKey()).entrySet()) {
                            var leaf = source.getKey();
                            boolean direct = leaf.equals(input.getKey());
                            if (supplies.containsKey(leaf)) continue;
                            try { supplies.put(leaf, nexusQuote(player, grid, leaf, direct ? BigInteger.valueOf(input.getValue())
                                    : BigInteger.ONE, path, search, direct && leaf.equals(target))); }
                            catch (IllegalArgumentException unavailable) { if (search.exhausted() || direct && need > 0 && source.getValue()) throw unavailable; }
                        }
                    }
                    var odds = "标称产率 " + selected.chance + "/" + selected.scale + "，每份 " + selected.successYield;
                    long recycled = selected.inputs.costs.getOrDefault(target, 0L);
                    if (recycled > 0) odds += "，每次投入同种材料 " + recycled;
                    return new NexusQuote(route, target, amount, quote(route, selected), odds, List.copyOf(supplies.values()));
                } catch (IllegalArgumentException unavailable) {
                    if (search.exhausted()) throw unavailable;
                    reason = unavailable.getMessage();
                }
                finally { path.remove(location); }
            }
        }
        throw new IllegalArgumentException(reason);
    }

    private static boolean onlyConditional(CraftingService service, AEKey target) {
        boolean found = false;
        for (var pattern : service.getCraftingFor(target)) for (var host : service.getProviders(pattern)) {
            if (!rolledOutputs(host, pattern).contains(target)) return false;
            found |= target.equals(pattern.getPrimaryOutput().what());
        }
        return found;
    }

    public static List<Candidate> candidates(ServerPlayer player, IGrid grid, AEKey target) {
        if (!(target instanceof AEItemKey || target instanceof AEFluidKey)) return List.of();
        Set<MEPatternBufferPartMachine> seen = new HashSet<>();
        List<Candidate> result = new ArrayList<>();
        for (var node : grid.getNodes()) {
            var provider = assembly(node.getService(ICraftingProvider.class));
            if (provider == null
                    || !seen.add(provider) || !node.isActive() || provider.getLevel() != player.level()
                    || provider.getControllers().size() != 1) continue;
            var controller = provider.getControllers().iterator().next();
            if (!(controller instanceof Hk3WorkableMultiblockMachine machine)
                    || !supports(machine)
                    || !machine.isFormed() || player.distanceToSqr(machine.getPos().getCenter()) > 4096
                    || !(player.getUUID().equals(machine.getOwnerUUID())
                        || Hk3ResearchTeams.scope(player.server, player.getUUID()).equals(machine.getResearchTeamUUID()))) continue;
            for (var slot : access(provider).getSlotBoundRecipes().int2ObjectEntrySet()) {
                var recipe = slot.getValue();
                if (!Arrays.asList(machine.getRecipeTypes()).contains(recipe.recipeType)) continue;
                var matching = targets(recipe, machine).stream().filter(output -> target.equals(output.key)).toList();
                if (matching.size() == 1 && matching.get(0).chance > 0 && matching.get(0).rolled)
                    result.add(new Candidate(machine.getPos(), provider.getPos(), slot.getIntKey(),
                            recipe.id + " / " + machine.getPos().toShortString() + " / 槽 " + (slot.getIntKey() + 1)));
            }
        }
        return List.copyOf(result);
    }

    public static List<UUID> orders(ServerPlayer player, IGrid grid, AEKey target) {
        var data = Hk3ProbabilityOrderData.get(player.server);
        List<UUID> orders = new ArrayList<>();
        data.entries.values().stream().filter(entry -> entry.group == null && entry.supplyParent == null
                && entry.owner.equals(player.getUUID()) && entry.goals.containsKey(target))
                .forEach(entry -> orders.add(entry.id));
        data.groups.values().stream().filter(group -> group.owner.equals(player.getUUID()) && group.goals.containsKey(target))
                .forEach(group -> orders.add(group.id));
        return List.copyOf(orders);
    }

    public static CompoundTag quote(ServerPlayer player, List<Candidate> candidates, AEKey key) {
        CompoundTag quote = new CompoundTag();
        ListTag routes = new ListTag();
        candidates.forEach(candidate -> routes.add(quote(player, candidate, key)));
        quote.put("Routes", routes);
        return quote;
    }

    public static CompoundTag quote(ServerPlayer player, Candidate candidate, AEKey key) {
        Selection selection = inspect(player, candidate.controller(), candidate.assembly(), candidate.slot(), key);
        return quote(candidate, selection);
    }

    private static CompoundTag quote(Candidate candidate, Selection selection) {
        CompoundTag quote = new CompoundTag();
        quote.putUUID("MachineIdentity", selection.machine.getProbabilityIdentity());
        quote.putUUID("AssemblyIdentity", ((Hk3ProbabilityAssemblyIdentity) selection.provider).hk3gtl$probabilityIdentity());
        quote.putUUID("Team", selection.machine.getResearchTeamUUID());
        quote.putString("Dimension", selection.machine.getLevel().dimension().location().toString());
        quote.putLong("Controller", candidate.controller().asLong());
        quote.putLong("Assembly", candidate.assembly().asLong());
        quote.putInt("Slot", candidate.slot());
        quote.put("Recipe", encode(selection.recipe));
        quote.put("Pattern", selection.provider.getPatternInventory().getStackInSlot(candidate.slot()).save(new CompoundTag()));
        quote.put("Target", selection.target.toTagGeneric());
        if (recipeHasBoost(selection.recipe)) quote.putInt("ChanceTier", selection.machine.getChanceTier());
        quote.put("MachineInputs", quantities(selection.inputs.machine));
        quote.put("ContainerInputs", quantities(selection.inputs.containers));
        quote.put("ReturnedContainers", quantities(selection.inputs.returned));
        return quote;
    }

    public static String preview(ServerPlayer player, Candidate candidate, AEKey key, BigInteger target, BigInteger attempts) {
        return preview(player, candidate, key, target, attempts, Map.of());
    }

    public static List<AEKey> additionalTargets(ServerPlayer player, Candidate candidate, AEKey key) {
        Selection selection = inspect(player, candidate.controller(), candidate.assembly(), candidate.slot(), key);
        var outputs = targets(selection);
        return outputs.stream().filter(output -> !output.key.equals(key) && output.chance > 0
                && outputs.stream().filter(other -> other.key.equals(output.key)).count() == 1)
                .map(Target::key).toList();
    }

    public static List<AEKey> additionalTargets(ServerPlayer player, List<Candidate> candidates, AEKey key) {
        return candidates.stream().flatMap(candidate -> additionalTargets(player, candidate, key).stream()).distinct().toList();
    }

    public static String preview(ServerPlayer player, List<Candidate> candidates, AEKey key, BigInteger target,
            BigInteger attempts, Map<AEKey, BigInteger> additional) {
        if (candidates.size() == 1) return preview(player, candidates.get(0), key, target, attempts, additional);
        StringBuilder text = new StringBuilder("多路线共享最多 ").append(attempts)
                .append(" 次；每次只启动一条路线，全部目标按所有路线的实际产出累计。")
                .append("\n按未完成目标的归一化期望贡献选路，只在当前原料可投时分配一次预算；不保证产出。");
        for (int i = 0; i < candidates.size(); i++) {
            text.append("\n\n路线 ").append(i + 1).append("：").append(candidates.get(i).label()).append('\n')
                    .append(preview(player, candidates.get(i), key, target, attempts,
                            routeGoals(player, candidates.get(i), key, additional)));
        }
        return text.append("\n各路线总预算为独占使用剩余额度时的上界，不相加；实际分配总数不会超过共享上限。").toString();
    }

    private static Map<AEKey, BigInteger> routeGoals(ServerPlayer player, Candidate candidate, AEKey key,
            Map<AEKey, BigInteger> additional) {
        var available = additionalTargets(player, candidate, key);
        Map<AEKey, BigInteger> goals = new LinkedHashMap<>();
        additional.forEach((output, amount) -> { if (available.contains(output)) goals.put(output, amount); });
        return goals;
    }

    public static String preview(ServerPlayer player, Candidate candidate, AEKey key, BigInteger target,
            BigInteger attempts, Map<AEKey, BigInteger> additional) {
        Selection selection = inspect(player, candidate.controller(), candidate.assembly(), candidate.slot(), key);
        require(target.signum() > 0 && attempts.signum() > 0, "目标数量与尝试预算必须为正数");
        Map<AEKey, BigInteger> goals = new LinkedHashMap<>();
        goals.put(selection.target, target);
        goals.putAll(additional);
        BigInteger limit = attempts;
        BigInteger availableAttempts = limit;
        var storage = selection.provider.getGrid().getStorageService().getInventory();
        var source = IActionSource.ofPlayer(player);
        StringBuilder message = new StringBuilder("全部目标满足后停产；共享最多 ").append(attempts).append(" 次，每批1次");
        for (var goal : goals.entrySet()) {
            var output = targets(selection).stream().filter(value -> value.key.equals(goal.getKey())).findFirst().orElseThrow();
            BigInteger expected = goal.getValue().add(BigInteger.valueOf(output.successYield - 1L))
                    .divide(BigInteger.valueOf(output.successYield)).multiply(BigInteger.valueOf(output.scale))
                    .add(BigInteger.valueOf(output.chance - 1L)).divide(BigInteger.valueOf(output.chance));
            message.append('\n').append(output.key.getDisplayName().getString()).append(" × ").append(goal.getValue())
                    .append(unit(output.key)).append("；标称产率 ").append(output.chance).append('/').append(output.scale)
                    .append("，每份 ").append(output.successYield).append(unit(output.key))
                    .append("；该目标期望尝试 ").append(expected).append("（不保证产出）");
        }
        for (var input : selection.inputs.costs.entrySet()) {
            BigInteger amount = BigInteger.valueOf(input.getValue());
            long available = storage.extract(input.getKey(), Long.MAX_VALUE, Actionable.SIMULATE, source);
            availableAttempts = availableAttempts.min(BigInteger.valueOf(available).divide(amount));
            message.append('\n').append(input.getKey().getDisplayName().getString()).append("：每次 ").append(amount)
                    .append(unit(input.getKey())).append("，总预算 ").append(amount.multiply(limit)).append(unit(input.getKey()))
                    .append("，当前可提取 ").append(available).append(unit(input.getKey()));
        }
        selection.inputs.returned.forEach((resource, amount) -> message.append('\n').append("每次实际排空返还：")
                .append(resource.getDisplayName().getString()).append(" × ").append(amount).append(unit(resource)));
        return message.append("\n当前AE库存最多支持 ").append(availableAttempts)
                .append(" 次；预览不扣料，提交后每次按实际投料与真实产出结算").toString();
    }

    public static UUID start(ServerPlayer player, Candidate candidate, AEKey key, BigInteger target, BigInteger attempts) {
        return start(player, candidate.controller(), candidate.assembly(), candidate.slot(), key, target, attempts);
    }

    public static UUID start(ServerPlayer player, Candidate candidate, AEKey key, BigInteger target,
            BigInteger attempts, Map<AEKey, BigInteger> additional) {
        return start(player, candidate.controller(), candidate.assembly(), candidate.slot(), key, target, attempts, additional);
    }

    public static UUID start(ServerPlayer player, BlockPos controllerPos, BlockPos assemblyPos,
            int slot, BigInteger target, BigInteger attempts) {
        return start(player, controllerPos, assemblyPos, slot, null, target, attempts);
    }

    public static UUID start(ServerPlayer player, BlockPos controllerPos, BlockPos assemblyPos,
            int slot, AEKey key, BigInteger target, BigInteger attempts) {
        return start(player, controllerPos, assemblyPos, slot, key, target, attempts, Map.of());
    }

    private static UUID start(ServerPlayer player, BlockPos controllerPos, BlockPos assemblyPos,
            int slot, AEKey key, BigInteger target, BigInteger attempts, Map<AEKey, BigInteger> additional) {
        var selected = inspect(player, controllerPos, assemblyPos, slot, key);
        var entry = registerSingle(player, selected, slot, target, attempts, additional, UUID.randomUUID());
        persist(player.server, entry);
        selected.machine.getRecipeLogic().updateTickSubscription();
        return entry.id;
    }

    private static Hk3ProbabilityOrderData.Entry registerSingle(ServerPlayer player, Selection selection, int slot,
            BigInteger target, BigInteger attempts, Map<AEKey, BigInteger> additional, UUID id) {
        var data = Hk3ProbabilityOrderData.get(player.server);
        checkOrderSlots(data, player.getUUID(), 1);
        var entry = create(player, selection, slot, target, attempts, additional, id);
        data.add(entry);
        return entry;
    }

    public static UUID start(ServerPlayer player, List<Candidate> candidates, AEKey key, BigInteger target,
            BigInteger attempts, Map<AEKey, BigInteger> additional) {
        if (candidates.size() == 1) return start(player, candidates.get(0), key, target, attempts, additional);
        var data = Hk3ProbabilityOrderData.get(player.server);
        checkOrderSlots(data, player.getUUID(), candidates.size());
        require(candidates.stream().map(Candidate::controller).distinct().count() == candidates.size()
                && candidates.stream().map(Candidate::assembly).distinct().count() == candidates.size(),
                "每条路线须使用不同的独占控制器与总成");
        List<Selection> selections = candidates.stream().map(candidate ->
                inspect(player, candidate.controller(), candidate.assembly(), candidate.slot(), key)).toList();
        var group = new Hk3ProbabilityOrderData.Group();
        group.id = UUID.randomUUID();
        group.owner = player.getUUID();
        group.attemptLimit = attempts;
        group.goals.put(key, target);
        group.goals.putAll(additional);
        for (int i = 0; i < candidates.size(); i++) {
            var entry = create(player, selections.get(i), candidates.get(i).slot(), target, BigInteger.ONE, additional, UUID.randomUUID());
            entry.group = group.id;
            entry.ledger = allocation(entry, BigInteger.ZERO);
            data.add(entry);
            group.routes.add(entry.id);
        }
        data.groups.put(group.id, group);
        persist(player.server, data.entries.get(group.routes.get(0)));
        selections.forEach(selection -> selection.machine.getRecipeLogic().updateTickSubscription());
        return group.id;
    }

    private static Hk3ProbabilityOrderData.Entry create(ServerPlayer player, Selection selection, int slot,
            BigInteger target, BigInteger attempts, Map<AEKey, BigInteger> additional, UUID id) {
        var machine = selection.machine;
        var provider = selection.provider;
        var recipe = selection.recipe;
        var inputs = selection.inputs.costs;
        require(target.signum() > 0 && attempts.signum() > 0, "目标数量与尝试预算必须为正数");
        Map<AEKey, BigInteger> costs = new LinkedHashMap<>(), caps = new LinkedHashMap<>();
        inputs.forEach((input, amount) -> {
            costs.put(input, BigInteger.valueOf(amount));
            caps.put(input, BigInteger.valueOf(amount).multiply(attempts));
        });
        var entry = new Hk3ProbabilityOrderData.Entry();
        entry.id = id;
        entry.owner = player.getUUID();
        entry.team = machine.getResearchTeamUUID();
        entry.machineIdentity = machine.getProbabilityIdentity();
        entry.assemblyIdentity = ((Hk3ProbabilityAssemblyIdentity) provider).hk3gtl$probabilityIdentity();
        entry.dimension = machine.getLevel().dimension().location().toString();
        entry.controller = machine.getPos().asLong();
        entry.assembly = provider.getPos().asLong();
        entry.slot = slot;
        entry.target = selection.target;
        entry.recipeId = recipe.id.toString();
        entry.recipe = encode(recipe);
        entry.pattern = provider.getPatternInventory().getStackInSlot(slot).save(new CompoundTag());
        entry.inputs.putAll(inputs);
        entry.machineInputs.putAll(selection.inputs.machine);
        entry.containerInputs.putAll(selection.inputs.containers);
        entry.returnedContainers.putAll(selection.inputs.returned);
        entry.goals.put(selection.target, target);
        entry.goals.putAll(additional);
        entry.ledger = new Hk3ExactProbabilityLedger<>(new Hk3ExactProbabilityPlan<>(entry.recipeId + "@" + entry.id,
                target, BigInteger.valueOf(selection.chance), BigInteger.valueOf(selection.scale),
                BigInteger.valueOf(selection.successYield), costs, caps, attempts, 1));
        return entry;
    }

    private static Selection inspect(ServerPlayer player, BlockPos controllerPos, BlockPos assemblyPos, int slot, AEKey key) {
        require(player.distanceToSqr(controllerPos.getCenter()) <= 4096, "请在控制器64格内下单");
        return inspect(player, player.serverLevel(), controllerPos, assemblyPos, slot, key, false);
    }

    private static Selection inspect(ServerPlayer player, ServerLevel level, BlockPos controllerPos, BlockPos assemblyPos, int slot, AEKey key, boolean nexus) {
        require(level.hasChunkAt(controllerPos) && level.hasChunkAt(assemblyPos), "控制器与总成须处于已加载区块");
        var provider = assembly(MetaMachine.getMachine(level, assemblyPos));
        if (!(MetaMachine.getMachine(level, controllerPos) instanceof Hk3WorkableMultiblockMachine machine)
                || provider == null)
            throw new IllegalArgumentException("需指定HK自有控制器与终极样板总成");
        require(supports(machine), "概率托管支持标准HK工作机器与使用HK配方执行器的采样、光谱、液态及研究工艺宿主");
        require(player.getUUID().equals(machine.getOwnerUUID())
                || Hk3ResearchTeams.scope(player.server, player.getUUID()).equals(machine.getResearchTeamUUID()), "只能使用本人或本队机器");
        require(machine.isFormed() && !machine.getRecipeLogic().isActive(), "机器须成型且无在途普通配方");
        require(locked(machine) == null && !blocksPush(provider), "机器或总成已有专属订单");
        require(provider.getMainNode().isActive() && provider.getGrid() != null, "总成没有有效AE连接");
        require(provider.getControllers().size() == 1 && provider.getControllers().contains(machine), "总成须独占绑定这一台控制器");
        require(provider.getProxies().isEmpty() && provider.getBoundProxyPositions().isEmpty(), "首版独占订单不接总成代理");
        require(access(provider).hk3gtl$hasUnitScale(), "请将总成样板倍率设为1:1");
        require(slot >= 0 && slot < provider.getPatternInventory().getSlots(), "样板槽位越界");
        var pattern = patternAt(provider, slot);
        require(pattern != null, "指定槽位没有已发布到 AE 的样板");
        require(empty(provider) && provider.getBuffer().isEmpty(), "总成槽位及返还缓冲须为空");
        GTRecipe recipe = boundRecipe(provider, slot);
        require(recipe != null && Arrays.asList(machine.getRecipeTypes()).contains(recipe.recipeType), "槽位未绑定本机可执行GT配方");
        validateRecipe(recipe);
        Inputs inputs = inputs(recipe, pattern);
        var outputs = targets(recipe, machine);
        var targetContent = outputs.stream().filter(output -> key == null
                ? output.chance > 0 && output.rolled : key.equals(output.key)).toList();
        require(targetContent.size() == 1, "请选择配方内唯一对应的固定数量概率物品或流体；命令自动选择时仅允许一个概率项");
        var output = targetContent.get(0);
        require(output.chance > 0 && (output.rolled || nexus && !rolledOutputs(recipe, pattern).isEmpty()), "所选目标没有可用的概率样板");
        if (nexus) require(BigInteger.valueOf(output.successYield).multiply(BigInteger.valueOf((output.chance + (long) output.scale - 1) / output.scale))
                .compareTo(BigInteger.valueOf(inputs.costs.getOrDefault(output.key, 0L))) > 0, "该样板即使命中也不能增加目标库存");
        require(outputs.stream().filter(candidate -> candidate.key.equals(output.key)).count() == 1,
                "目标资源不能同时出现在其他产物项");
        require(!inputs.returned.containsKey(output.key), "概率主目标不能同时是实际排空必返的容器");
        return new Selection(machine, provider, recipe, inputs, output.key, output.chance, output.scale, output.successYield, output.rolled);
    }

    private static List<Target> targets(Selection selection) {
        return targets(selection.recipe, selection.machine, selection.inputs.returned);
    }

    private static List<Target> targets(GTRecipe recipe, Hk3WorkableMultiblockMachine machine, Map<AEKey, Long> returned) {
        var outputs = targets(recipe, machine);
        returned.forEach((key, amount) -> outputs.add(new Target(key, 1, 1, amount, false)));
        return outputs;
    }

    private static boolean recipeHasBoost(GTRecipe recipe) {
        return recipe.outputs.values().stream().flatMap(List::stream).anyMatch(content -> content.tierChanceBoost != 0);
    }

    private static Target target(AEKey key, long yield, Content content, GTRecipe recipe, Hk3WorkableMultiblockMachine machine) {
        boolean rolled = content.chance > 0 && content.chance < content.maxChance;
        int chance = rolled ? recipe.getType().getChanceFunction().getBoostedChance(content,
                ((org.gtlcore.gtlcore.api.recipe.IGTRecipe) recipe).getEuTier(), machine.getChanceTier()) : content.chance;
        return new Target(key, Math.max(0, chance), content.maxChance, yield, rolled);
    }

    private static List<Target> targets(GTRecipe recipe, Hk3WorkableMultiblockMachine machine) {
        List<Target> outputs = new ArrayList<>();
        for (var content : recipe.getOutputContents(ItemRecipeCapability.CAP)) {
            var ingredient = ItemRecipeCapability.CAP.of(content.content);
            if (ingredient.getItems().length == 1) {
                var stack = ingredient.getItems()[0];
                outputs.add(target(AEItemKey.of(stack), stack.getCount(), content, recipe, machine));
            }
        }
        for (var content : recipe.getOutputContents(FluidRecipeCapability.CAP)) {
            var ingredient = FluidRecipeCapability.CAP.of(content.content);
            if (ingredient.getStacks().length == 1) {
                var stack = ingredient.getStacks()[0];
                outputs.add(target(AEFluidKey.of(stack.getFluid(), stack.getTag()), ingredient.getAmount(), content, recipe, machine));
            }
        }
        return outputs;
    }

    private static String unit(AEKey key) { return key instanceof AEFluidKey ? " mB" : " 个"; }

    public static String status(ServerPlayer player, UUID id) {
        var data = Hk3ProbabilityOrderData.get(player.server);
        if (data.groups.containsKey(id)) {
            var group = ownedGroup(player, id);
            var routes = routes(data, group);
            var actual = actual(routes);
            String state = group.cancelled ? "已取消" : satisfied(group.goals, actual) ? "全部目标已满足"
                    : allocated(routes).compareTo(group.attemptLimit) >= 0
                        && routes.stream().allMatch(route -> route.ledger.snapshot().pending() == null) ? "尝试预算已耗尽" : "等待／执行真实批次";
            var text = new StringBuilder(id + " / 多路线共享预算" + (group.paused ? " / 已暂停" : "")
                    + " / " + state
                    + " / 已分配尝试 " + allocated(routes) + "/" + group.attemptLimit);
            group.goals.forEach((key, amount) -> text.append('\n').append(key.getDisplayName().getString())
                    .append("：实得 ").append(actual.getOrDefault(key, BigInteger.ZERO)).append('/').append(amount).append(unit(key)));
            routes.forEach(route -> text.append("\n路线 ").append(route.recipeId).append(" / ")
                    .append(BlockPos.of(route.controller).toShortString()).append(" / ").append(route.phase)
                    .append(route.paused ? " / 已暂停" : "").append(" / 已分配 ")
                    .append(route.ledger.snapshot().allocatedAttempts()).append(" / 托管 ").append(route.escrow.size())
                    .append(" / ").append(route.note));
            return text.toString();
        }
        var entry = owned(player, id);
        var snapshot = entry.ledger.snapshot();
        var text = new StringBuilder(id + " / " + entry.phase + (entry.paused ? " / 已暂停" : "") + " / " + entry.status()
                + " / 已分配尝试 " + snapshot.allocatedAttempts() + "/" + snapshot.plan().attemptLimit()
                + " / 托管资源 " + entry.escrow.size() + " / " + entry.note);
        entry.goals.forEach((key, amount) -> text.append('\n').append(key.getDisplayName().getString()).append("：实得 ")
                .append(entry.actualOutputs.getOrDefault(key, BigInteger.ZERO)).append('/').append(amount).append(unit(key)));
        return text.toString();
    }

    public static void cancel(ServerPlayer player, UUID id) {
        var data = Hk3ProbabilityOrderData.get(player.server);
        if (data.groups.containsKey(id)) {
            var group = ownedGroup(player, id);
            group.cancelled = true;
            group.routes.forEach(route -> cancel(player, route));
            return;
        }
        cancel(player.server, owned(player, id));
    }

    private static void checkOrderSlots(Hk3ProbabilityOrderData data, UUID player, int required) {
        int total = required, owned = required;
        for (var entry : data.entries.values()) {
            if (entry.nexusParent != null && entry.released) continue;
            total++;
            if (player.equals(entry.owner)) owned++;
        }
        require(total <= 128 && owned <= 16, "概率订单名额不足：全服 128 条，每人 16 条");
    }

    public record NexusReceipt(boolean settled, boolean satisfied, BigInteger attempts, BigInteger actual, BigInteger delivered, String note) {}

    public static CompoundTag nexusProgress(MinecraftServer server, UUID parent) {
        return Hk3ProbabilityOrderData.get(server).nexusProgress.get(parent);
    }

    public static Collection<CompoundTag> recoverStarts(MinecraftServer server, UUID host, ListTag saved) {
        var data = Hk3ProbabilityOrderData.get(server);
        var starts = data.startsByHost.get(host);
        if (starts == null) return List.of();
        for (Tag row : saved) if (starts.remove(((CompoundTag) row).getUUID("id")) != null) data.setDirty();
        if (starts.isEmpty()) data.startsByHost.remove(host);
        return starts.values();
    }

    public static void forgetNexusProgress(MinecraftServer server, UUID parent) {
        var data = Hk3ProbabilityOrderData.get(server);
        data.nexusProgress.remove(parent);
        data.setDirty();
    }

    public static boolean recordNexusProgress(MinecraftServer server, UUID child, CompoundTag progress) {
        var data = Hk3ProbabilityOrderData.get(server);
        var entry = data.entries.get(child);
        progress.putUUID("Parent", entry.nexusParent);
        var previous = data.nexusProgress.put(entry.nexusParent, progress);
        entry.receiptClaimed = true;
        boolean prune = entry.supplyOrder == null;
        if (prune) data.remove(child);
        try { data.checkpoint(server); }
        catch (IOException failure) {
            entry.receiptClaimed = false;
            if (prune) data.add(entry);
            if (previous == null) data.nexusProgress.remove(entry.nexusParent);
            else data.nexusProgress.put(entry.nexusParent, previous);
            LogUtils.getLogger().error("天枢概率订单回执未保存：{}", child, failure);
            return false;
        }
        return true;
    }

    public static boolean hasNexusChild(MinecraftServer server, UUID parent, UUID child) {
        var entry = Hk3ProbabilityOrderData.get(server).entries.get(child);
        return entry != null && parent.equals(entry.nexusParent);
    }

    public static NexusReceipt nexusReceipt(MinecraftServer server, UUID child) {
        var entry = Hk3ProbabilityOrderData.get(server).entries.get(child);
        if (entry == null) return null;
        var ledger = entry.ledger.snapshot();
        return new NexusReceipt(entry.released && entry.probabilitySupply == null && entry.escrow.isEmpty(),
                entry.status() == Hk3ExactProbabilityLedger.Status.SATISFIED,
                ledger.allocatedAttempts().add(entry.supplyAttempts), ledger.actualOutput(),
                entry.netTarget(ledger).subtract(entry.unclaimedTarget).max(BigInteger.ZERO), entry.note);
    }

    public static void cancelNexus(MinecraftServer server, UUID child) {
        var entry = Hk3ProbabilityOrderData.get(server).entries.get(child);
        if (entry != null) cancel(server, entry);
    }

    private static void cancel(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry) {
        if (entry.released) return;
        var data = Hk3ProbabilityOrderData.get(server);
        entry.ledger.cancel();
        if (entry.probabilitySupply != null) cancelNexus(server, entry.probabilitySupply);
        if (!stopSupply(server, entry, true)) return;
        entry.note = "已停止续批；已开工批次仍按原能源与研究条件完成，未知事务保留令牌";
        if (entry.phase == Phase.IDLE || entry.phase == Phase.COMPLETED) {
            data.setReleased(entry, entry.escrow.isEmpty() && entry.probabilitySupply == null);
            entry.phase = entry.released ? Phase.STOPPED : Phase.COMPLETED;
        } else if (entry.phase == Phase.LOADED) {
            var binding = binding(server, entry);
            if (binding == null || binding.machine.getRecipeLogic().isActive() || !slotMatches(binding.provider, entry)) {
                entry.paused = true;
                entry.note = "已停止续批；须接回原总成后取消，才能退还未开工投料";
                persist(server, entry);
                return;
            }
            entry.phase = Phase.TRANSFERRING;
            if (!persist(server, entry)) return;
            var inventory = slot(binding.provider, entry.slot);
            entry.machineInputs.forEach((key, amount) -> {
                long actual = key instanceof AEItemKey item ? inventory.hk3gtl$items().removeLong(item)
                        : inventory.hk3gtl$fluids().removeLong((AEFluidKey) key);
                entry.escrow.merge(key, BigInteger.valueOf(actual), BigInteger::add);
            });
            inventory.hk3gtl$changed().run();
            binding.provider.getHolder().getSelf().setChanged();
            entry.ledger.withdrawUnstarted(entry.ledger.snapshot().pending().token());
            entry.phase = Phase.COMPLETED;
        }
        persist(server, entry);
    }

    public static void resume(ServerPlayer player, UUID id) throws IOException {
        var data = Hk3ProbabilityOrderData.get(player.server);
        if (data.groups.containsKey(id)) {
            var group = ownedGroup(player, id);
            for (var route : routes(data, group)) if (!route.released) resume(player, route.id);
            group.paused = false;
            persist(player.server, data.entries.get(group.routes.get(0)));
            return;
        }
        var entry = owned(player, id);
        var binding = binding(player.server, entry);
        require(binding != null, "原控制器、总成、团队、样板或AE连接已变化");
        require(entry.nexusParent == null || entry.ledger.snapshot().cancelled() || nexusOnline(binding, entry), "原天枢订单未在线");
        if (entry.phase == Phase.RUNNING) {
            var recipe = binding.machine.getRecipeLogic().getLastRecipe();
            require(recipe != null && matches(entry, recipe) && empty(binding.provider)
                    && binding.machine.getRecipeLogic().getDuration() > 0, "缺少原生在途令牌和已消费独占槽位证据");
        } else if (entry.phase == Phase.LOADED) {
            require(!binding.machine.getRecipeLogic().isActive() && slotMatches(binding.provider, entry), "缺少原独占投料槽位的完整证据");
        } else {
            require(entry.phase == Phase.IDLE || entry.phase == Phase.COMPLETED || entry.phase == Phase.STOPPED,
                    "事务结果未知；禁止通过恢复命令重投、重抽或补发");
            require(empty(binding.provider), "总成存在未归属物料");
        }
        entry.paused = false;
        if (entry.probabilitySupply != null && !data.entries.get(entry.probabilitySupply).released)
            resume(player, entry.probabilitySupply);
        if (entry.supplyOrder != null && entry.probabilitySupply == null) {
            startMaterialSupply(binding, entry);
        }
        entry.note = "已凭原机器与批次证据恢复";
        persist(player.server, entry);
        binding.machine.getRecipeLogic().updateTickSubscription();
    }

    public static BigInteger claim(ServerPlayer player, UUID id) {
        var data = Hk3ProbabilityOrderData.get(player.server);
        if (data.groups.containsKey(id)) {
            var group = ownedGroup(player, id);
            BigInteger moved = BigInteger.ZERO;
            for (var route : routes(data, group)) if (!route.escrow.isEmpty()) moved = moved.add(claim(player, route.id));
            return moved;
        }
        var entry = owned(player, id);
        require(entry.phase != Phase.DELIVERING && entry.phase != Phase.UNKNOWN
                && entry.phase != Phase.TRANSFERRING && entry.phase != Phase.ROLLING, "存在未知事务，托管不自动重放");
        var binding = binding(player.server, entry);
        require(binding != null, "领取须连接原绑定机器、总成与有效AE网络");
        require(entry.nexusParent == null || entry.ledger.snapshot().cancelled() || nexusOnline(binding, entry), "产物须交回原订单所在的天枢网络");
        Phase previous = entry.phase;
        entry.phase = Phase.DELIVERING;
        if (!persist(player.server, entry)) return BigInteger.ZERO;
        BigInteger moved = BigInteger.ZERO;
        var storage = binding.provider.getGrid().getStorageService().getInventory();
        for (var output : entry.escrow.entrySet()) {
            long requested = output.getValue().min(BigInteger.valueOf(Long.MAX_VALUE)).longValueExact();
            long accepted = storage.insert(output.getKey(), requested, Actionable.MODULATE, IActionSource.ofPlayer(player));
            var inserted = BigInteger.valueOf(accepted);
            output.setValue(output.getValue().subtract(inserted));
            if (entry.unclaimedTarget.signum() > 0 && entry.target.equals(output.getKey()))
                entry.unclaimedTarget = entry.unclaimedTarget.subtract(entry.unclaimedTarget.min(inserted));
            moved = moved.add(inserted);
        }
        entry.escrow.values().removeIf(amount -> amount.signum() == 0);
        entry.phase = previous;
        entry.note = "按AE实际接收量交付；未接收余量仍托管";
        persist(player.server, entry);
        return moved;
    }

    public static void forget(ServerPlayer player, UUID id) throws IOException {
        var data = Hk3ProbabilityOrderData.get(player.server);
        if (data.groups.containsKey(id)) {
            var group = ownedGroup(player, id);
            var routes = routes(data, group);
            require(routes.stream().allMatch(route -> route.released && route.escrow.isEmpty()
                    && route.ledger.snapshot().pending() == null), "路线仍有在途令牌或托管余额，不能删除");
            for (var route : routes) require(supplySettled(player.server, route), "前置订单仍有在途批次，不能删除");
            for (var route : routes) forgetSupply(player.server, route);
            group.routes.forEach(data::remove);
            data.groups.remove(id);
            persist(player.server, routes.get(0));
            return;
        }
        var entry = owned(player, id);
        require(entry.group == null, "多路线子账本须通过主订单整体清理");
        require(entry.nexusParent == null || entry.receiptClaimed, "请等天枢收取本单的最终回执");
        require(entry.probabilitySupply == null && entry.supplyParent == null, "上游实际回执尚未交给父单");
        require(entry.released && entry.escrow.isEmpty() && entry.ledger.snapshot().pending() == null && supplySettled(player.server, entry),
                "仍有在途令牌或托管余额，不能删除");
        forgetSupply(player.server, entry);
        data.remove(id);
        persist(player.server, entry);
    }

    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.getServer().getTickCount() % 20 != 0) return;
        var server = event.getServer();
        var data = Hk3ProbabilityOrderData.get(server);
        for (var entry : List.copyOf(data.entries.values())) {
            if (entry.group != null || entry.paused || entry.released) continue;
            var binding = binding(server, entry);
            if (binding == null) { entry.paused = true; stopSupply(server, entry, false); entry.note = "绑定、权限、成型或连接已变化；等待原付款人核对恢复"; persist(server, entry); continue; }
            if (entry.nexusParent != null && !entry.ledger.snapshot().cancelled() && !nexusOnline(binding, entry)) continue;
            if (entry.probabilitySupply != null) {
                var receipt = nexusReceipt(server, entry.probabilitySupply);
                if (!receipt.settled()) continue;
                entry.supplyAttempts = entry.supplyAttempts.add(receipt.attempts());
                var child = data.entries.get(entry.probabilitySupply);
                entry.probabilitySupply = null;
                if (!receipt.satisfied()) { entry.ledger.cancel(); entry.note = "上游概率原料未完成：" + child.note; }
                if (entry.ledger.snapshot().cancelled()) entry.phase = Phase.COMPLETED;
                if (child.supplyOrder == null) data.remove(child.id);
                else { child.supplyParent = null; child.receiptClaimed = true; }
                if (!persist(server, entry)) continue;
                if (entry.supplyOrder != null) {
                    if (entry.ledger.snapshot().cancelled()) { if (!stopSupply(server, entry, true)) continue; }
                    else if (!resumeMaterialSupply(server, entry, binding)) continue;
                }
            }
            if (entry.phase == Phase.COMPLETED) {
                if (!entry.escrow.isEmpty()) claim(binding.player, entry.id);
                if (entry.phase == Phase.COMPLETED && entry.escrow.isEmpty()) {
                    entry.phase = Phase.IDLE;
                    if (entry.status() != Hk3ExactProbabilityLedger.Status.ACTIVE) {
                        entry.phase = Phase.STOPPED;
                        data.setReleased(entry, true);
                    }
                    persist(server, entry);
                }
            }
            if (entry.phase == Phase.IDLE && entry.status() == Hk3ExactProbabilityLedger.Status.ACTIVE)
                loadBatch(server, entry, binding);
            binding.machine.getRecipeLogic().updateTickSubscription();
        }
        for (var group : data.groups.values()) if (!group.paused) tickGroup(server, data, group);
    }

    private static void tickGroup(MinecraftServer server, Hk3ProbabilityOrderData data, Hk3ProbabilityOrderData.Group group) {
        var routes = routes(data, group);
        for (var entry : routes) {
            if (entry.released || entry.paused) continue;
            var binding = binding(server, entry);
            if (binding == null) {
                entry.paused = true;
                stopSupply(server, entry, false);
                entry.note = "路线绑定、权限、成型或连接已变化；其他空闲路线仍可使用共享余量";
                persist(server, entry);
                continue;
            }
            if (entry.phase == Phase.COMPLETED) {
                if (!entry.escrow.isEmpty()) claim(binding.player, entry.id);
                if (entry.phase == Phase.COMPLETED && entry.escrow.isEmpty()) {
                    data.setReleased(entry, entry.ledger.snapshot().cancelled());
                    entry.phase = entry.released ? Phase.STOPPED : Phase.IDLE;
                    persist(server, entry);
                }
            }
            binding.machine.getRecipeLogic().updateTickSubscription();
        }
        boolean done = group.cancelled || satisfied(group.goals, actual(routes))
                || allocated(routes).compareTo(group.attemptLimit) >= 0;
        if (done) {
            for (var entry : routes) if (!entry.released && entry.phase == Phase.IDLE) {
                if (!stopSupply(server, entry, true)) continue;
                entry.phase = Phase.STOPPED;
                data.setReleased(entry, true);
                persist(server, entry);
            }
            return;
        }
        if (routes.stream().anyMatch(entry -> entry.ledger.snapshot().pending() != null
                || entry.phase != Phase.IDLE && entry.phase != Phase.STOPPED)) return;
        for (var entry : routes) if (entry.supplyOrder != null) {
            var binding = binding(server, entry);
            if (entry.paused || binding == null || !supplyInputs(server, entry, binding)) return;
        }
        var actual = actual(routes);
        Hk3ProbabilityOrderData.Entry selected = null;
        Binding selectedBinding = null;
        Hk3ProbabilityOrderData.Entry supplyRoute = null;
        Binding supplyBinding = null;
        Score best = Score.ZERO;
        Score supplyBest = Score.ZERO;
        for (var entry : routes) {
            if (entry.released || entry.paused) continue;
            var binding = binding(server, entry);
            if (binding == null || !empty(binding.provider)) continue;
            var recipe = boundRecipe(binding.provider, entry.slot);
            Score score = contribution(group.goals, actual, targets(recipe, binding.machine, entry.returnedContainers));
            if (affordable(binding, entry)) {
                if (score.compareTo(best) > 0) { selected = entry; selectedBinding = binding; best = score; }
            } else if (score.compareTo(supplyBest) > 0) {
                supplyRoute = entry; supplyBinding = binding; supplyBest = score;
            }
        }
        if (selected != null) {
            selected.ledger = allocation(selected, selected.ledger.snapshot().allocatedAttempts().add(BigInteger.ONE));
            loadBatch(server, selected, selectedBinding);
            selectedBinding.machine.getRecipeLogic().updateTickSubscription();
        } else if (supplyRoute != null) supplyInputs(server, supplyRoute, supplyBinding);
    }

    private static Hk3ExactProbabilityLedger<AEKey> allocation(Hk3ProbabilityOrderData.Entry entry, BigInteger attempts) {
        var snapshot = entry.ledger.snapshot();
        var plan = snapshot.plan();
        Map<AEKey, BigInteger> caps = new LinkedHashMap<>();
        plan.inputsPerAttempt().forEach((key, amount) -> caps.put(key, amount.multiply(attempts)));
        var allocated = new Hk3ExactProbabilityPlan<>(plan.metadataId(), plan.target(), plan.chance(), plan.chanceScale(),
                plan.successYield(), plan.inputsPerAttempt(), caps, attempts.max(BigInteger.ONE), 1);
        return Hk3ExactProbabilityLedger.restore(new Hk3ExactProbabilityLedger.Snapshot<>(allocated,
                snapshot.allocatedAttempts(), snapshot.actualOutput(), null, snapshot.lastReceipt(), snapshot.cancelled()));
    }

    private static boolean affordable(Binding binding, Hk3ProbabilityOrderData.Entry entry) {
        var storage = binding.provider.getGrid().getStorageService().getInventory();
        var source = IActionSource.ofPlayer(binding.player);
        return entry.inputs.entrySet().stream().allMatch(input ->
                storage.extract(input.getKey(), input.getValue(), Actionable.SIMULATE, source) == input.getValue());
    }

    private record Score(BigInteger numerator, BigInteger denominator) implements Comparable<Score> {
        static final Score ZERO = new Score(BigInteger.ZERO, BigInteger.ONE);
        Score add(Score other) {
            BigInteger numerator = this.numerator.multiply(other.denominator).add(other.numerator.multiply(denominator));
            BigInteger denominator = this.denominator.multiply(other.denominator);
            BigInteger divisor = numerator.gcd(denominator);
            return new Score(numerator.divide(divisor), denominator.divide(divisor));
        }
        @Override public int compareTo(Score other) {
            return numerator.multiply(other.denominator).compareTo(other.numerator.multiply(denominator));
        }
    }

    private static Score contribution(Map<AEKey, BigInteger> goals, Map<AEKey, BigInteger> actual, List<Target> outputs) {
        Score score = Score.ZERO;
        for (var output : outputs) if (goals.containsKey(output.key)) {
            BigInteger goal = goals.get(output.key);
            BigInteger remaining = goal.subtract(actual.getOrDefault(output.key, BigInteger.ZERO)).max(BigInteger.ZERO);
            score = score.add(new Score(remaining.min(BigInteger.valueOf(output.successYield)).multiply(BigInteger.valueOf(output.chance)),
                    goal.multiply(BigInteger.valueOf(output.scale))));
        }
        return score;
    }

    private static List<Hk3ProbabilityOrderData.Entry> routes(Hk3ProbabilityOrderData data, Hk3ProbabilityOrderData.Group group) {
        return group.routes.stream().map(data.entries::get).toList();
    }

    private static BigInteger allocated(List<Hk3ProbabilityOrderData.Entry> routes) {
        return routes.stream().map(route -> route.ledger.snapshot().allocatedAttempts()).reduce(BigInteger.ZERO, BigInteger::add);
    }

    private static Map<AEKey, BigInteger> actual(List<Hk3ProbabilityOrderData.Entry> routes) {
        Map<AEKey, BigInteger> actual = new LinkedHashMap<>();
        routes.forEach(route -> route.actualOutputs.forEach((key, amount) -> actual.merge(key, amount, BigInteger::add)));
        return actual;
    }

    private static boolean satisfied(Map<AEKey, BigInteger> goals, Map<AEKey, BigInteger> actual) {
        return goals.entrySet().stream().allMatch(goal -> actual.getOrDefault(goal.getKey(), BigInteger.ZERO).compareTo(goal.getValue()) >= 0);
    }

    public static boolean find(RecipeLogic logic) {
        var entry = locked(logic.getMachine());
        if (entry == null) return false;
        var server = logic.getMachine().getLevel().getServer();
        var binding = binding(server, entry);
        if (entry.paused || binding == null || entry.phase != Phase.LOADED || entry.nexusParent != null && !nexusOnline(binding, entry)) {
            logic.setStatus(RecipeLogic.Status.IDLE);
            return true;
        }
        GTRecipe original = boundRecipe(binding.provider, entry.slot);
        GTRecipe recipe = binding.machine.fullModifyRecipe(original.copy(),
                new com.gregtechceu.gtceu.api.recipe.logic.OCParams(), new com.gregtechceu.gtceu.api.recipe.logic.OCResult());
        if (recipe == null) return true;
        CompoundTag modified = encode(recipe);
        if (recipe.parallels != 1 || !List.of("inputs", "outputs", "inputChanceLogics", "outputChanceLogics")
                .stream().allMatch(key -> Objects.equals(entry.recipe.get(key), modified.get(key)))) {
            entry.paused = true;
            entry.note = "本机修饰器改变单次物料或概率合同；原投料保留，可取消退款";
            persist(server, entry);
            return true;
        }
        if (recipeHasBoost(recipe)) {
            var current = targets(recipe, binding.machine).stream().filter(t -> t.key.equals(entry.target)).findFirst().orElseThrow();
            if (current.chance != entry.ledger.snapshot().plan().chance().intValueExact()) {
                entry.paused = true; entry.note = "机器概率加成已变化，请取消并重新下单"; persist(server, entry); return true;
            }
        }
        if (Hk3RecipeAccess.blocks(recipe, logic.getMachine()) || !recipe.checkConditions(logic).isSuccess()
                || !recipe.matchTickRecipe(binding.machine).isSuccess()) return true;
        recipe.data = recipe.data.copy();
        recipe.data.putUUID(ORDER, entry.id);
        recipe.data.putLong(SEQUENCE, Hk3ProbabilityOrderData.get(server).completedByMachine.getOrDefault(entry.machineIdentity, 0L) + 1);
        recipe.data.putUUID(TOKEN, entry.ledger.snapshot().pending().token());
        recipe.parallels = 1;
        logic.setupRecipe(recipe);
        return true;
    }

    public static boolean retireCompleted(RecipeLogic logic) {
        var recipe = logic.getLastRecipe();
        if (recipe == null || !recipe.data.contains(SEQUENCE)) return false;
        var machine = (Hk3WorkableMultiblockMachine) logic.getMachine();
        var completed = Hk3ProbabilityOrderData.get(machine.getLevel().getServer()).completedByMachine.getOrDefault(machine.getProbabilityIdentity(), 0L);
        if (recipe.data.getLong(SEQUENCE) > completed) return false;
        logic.resetRecipeLogic();
        machine.markDirty();
        return true;
    }

    public static boolean blocksWork(RecipeLogic logic) {
        var entry = locked(logic.getMachine());
        if (entry == null) return logic.getLastRecipe() != null && logic.getLastRecipe().data.hasUUID(TOKEN);
        return entry.paused || entry.phase != Phase.RUNNING || binding(logic.getMachine().getLevel().getServer(), entry) == null
                || !matches(entry, logic.getLastRecipe());
    }

    public static boolean blocksFinish(RecipeLogic logic) {
        GTRecipe recipe = logic.getLastRecipe();
        if (recipe == null || !recipe.data.hasUUID(TOKEN)) return false;
        var server = logic.getMachine().getLevel().getServer();
        var token = recipe.data.getUUID(TOKEN);
        var entries = Hk3ProbabilityOrderData.get(server).entries;
        boolean completed = recipe.data.hasUUID(ORDER)
                ? hasReceipt(entries.get(recipe.data.getUUID(ORDER)), logic.getMachine(), token)
                : entries.values().stream().anyMatch(entry -> hasReceipt(entry, logic.getMachine(), token));
        if (completed) return false;
        var entry = locked(logic.getMachine());
        return entry == null || entry.paused || entry.phase != Phase.RUNNING || !matches(entry, recipe) || binding(server, entry) == null;
    }

    private static boolean hasReceipt(Hk3ProbabilityOrderData.Entry entry, MetaMachine machine, UUID token) {
        return entry != null && entry.controller == machine.getPos().asLong()
                && entry.dimension.equals(machine.getLevel().dimension().location().toString()) && entry.ledger.hasReceipt(token);
    }

    public static Boolean input(RecipeLogic logic, GTRecipe recipe, IO io) {
        var entry = locked(logic.getMachine());
        if (entry == null) return recipe.data.hasUUID(TOKEN) ? Boolean.FALSE : null;
        if (io != IO.IN || entry.paused || entry.phase != Phase.LOADED || !matches(entry, recipe)) return false;
        var server = logic.getMachine().getLevel().getServer();
        var binding = binding(server, entry);
        if (binding == null || !slotMatches(binding.provider, entry)) return false;
        if (!org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper.matchRecipeInput(binding.machine, recipe)) return false;
        entry.phase = Phase.STARTING;
        if (!persist(server, entry)) return false;
        var selected = new it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap<GTRecipe>();
        selected.put(entry.slot, recipe);
        boolean consumed = access(binding.provider).commitSlotBoundRecipes(selected);
        entry.phase = consumed ? Phase.RUNNING : Phase.UNKNOWN;
        entry.note = consumed ? "原生配方已消费专属槽位；EU/HW及研究守卫照常执行" : "实际投料提交未完成，保留原令牌";
        persist(server, entry);
        return consumed && entry.phase == Phase.RUNNING;
    }

    public static boolean escrowsOutput(GTRecipe recipe) {
        return recipe.data.hasUUID(TOKEN);
    }

    private static boolean supports(Hk3WorkableMultiblockMachine machine) {
        return machine.getRecipeLogic() instanceof Hk3RecipeLogic
                && (machine.getClass() == Hk3WorkableMultiblockMachine.class || machine instanceof Hk3LiquidProcessMachine);
    }

    private static boolean nexusOnline(Binding binding, Hk3ProbabilityOrderData.Entry entry) {
        return parentNexus(binding, entry) != null;
    }

    private static Hk3NexusCrafting parentNexus(Binding binding, Hk3ProbabilityOrderData.Entry entry) {
        var root = entry;
        var data = Hk3ProbabilityOrderData.get(binding.player.server);
        while (root.supplyParent != null) {
            var parent = data.entries.get(root.supplyParent);
            if (parent == null || parent.paused || !root.id.equals(parent.probabilitySupply)) return null;
            root = parent;
        }
        UUID route = root.id;
        for (var host : Hk3NexusCrafting.forGrid(binding.provider.getGrid()))
            if (host.awaitingProbability(entry.nexusParent, route)) return host;
        return null;
    }

    public static Boolean output(IRecipeLogicMachine machine, GTRecipe recipe) {
        if (!recipe.data.hasUUID(TOKEN)) return null;
        var logic = machine.getRecipeLogic();
        if (logic.getLastRecipe() != recipe || logic.getDuration() <= 0 || logic.getProgress() < logic.getDuration()) return false;
        var entry = locked(machine.self());
        logic.markLastRecipeDirty();
        if (entry == null || entry.paused || entry.phase != Phase.RUNNING || !matches(entry, recipe)) return false;
        var server = machine.self().getLevel().getServer();
        if (binding(server, entry) == null) { entry.paused = true; persist(server, entry); return false; }
        entry.phase = Phase.ROLLING;
        if (!persist(server, entry)) return false;
        Map<AEKey, BigInteger> captured = new LinkedHashMap<>();
        var settled = Hk3ProbabilityOutput.capture(machine, recipe, captured);
        captured.forEach((key, amount) -> entry.escrow.merge(key, amount, BigInteger::add));
        captured.forEach((key, amount) -> {
            if (entry.goals.containsKey(key)) entry.actualOutputs.merge(key, amount, BigInteger::add);
        });
        entry.note = "真实抽样产物已托管，正在结算本批研究与工艺事实";
        if (!persist(server, entry)) return false;
        Hk3ProductionOutput.settled(machine, settled);
        var pending = entry.ledger.snapshot().pending();
        var targetOutput = captured.getOrDefault(entry.target, BigInteger.ZERO);
        entry.ledger.complete(new Hk3ExactProbabilityLedger.Receipt(pending.token(), pending.metadataId(), 1, targetOutput));
        if (entry.nexusParent != null) entry.unclaimedTarget = entry.unclaimedTarget.add(targetOutput);
        entry.phase = Phase.COMPLETED;
        entry.note = "原生完整尝试已结束；实际物品与流体已专属托管（允许目标零产出）";
        var completed = Hk3ProbabilityOrderData.get(server).completedByMachine;
        Long previous = recipe.data.contains(SEQUENCE) ? completed.put(entry.machineIdentity, recipe.data.getLong(SEQUENCE)) : null;
        if (!persist(server, entry) && recipe.data.contains(SEQUENCE)) {
            if (previous == null) completed.remove(entry.machineIdentity);
            else completed.put(entry.machineIdentity, previous);
        }
        return false;
    }

    public static boolean blocksPush(Object candidate) {
        var provider = assembly(candidate);
        if (provider == null || provider == authorizedPush || provider.isRemote()) return false;
        var level = (ServerLevel) provider.getLevel();
        return Hk3ProbabilityOrderData.get(level.getServer()).assemblies.containsKey(
                new Hk3ProbabilityOrderData.Location(level.dimension().location().toString(), provider.getPos().asLong()));
    }

    private static void startMaterialSupply(Binding binding, Hk3ProbabilityOrderData.Entry entry) throws IOException {
        var nexus = entry.nexusParent == null ? null : parentNexus(binding, entry);
        require(entry.nexusParent == null || nexus != null, "前置订单须接回原天枢网络");
        Hk3ExactOrderService.resumeSupply(binding.player, supplyHost(binding.player.server, entry), entry.id, entry.supplyOrder,
                nexus == null ? null : nexus.availableCpu());
    }

    private static IActionHost supplyHost(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry) {
        return () -> {
            var binding = binding(server, entry);
            return binding == null || entry.paused || entry.released || entry.nexusParent != null && !nexusOnline(binding, entry)
                    ? null : binding.provider.getMainNode().getNode();
        };
    }

    private static boolean supplyInputs(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry, Binding binding) {
        try {
            var grid = binding.provider.getGrid();
            var storage = grid.getStorageService().getInventory();
            var source = IActionSource.ofPlayer(binding.player);
            if (entry.supplyOrder != null) {
                var supply = Hk3ExactOrderService.supply(server, entry.id, entry.supplyOrder);
                var state = supply.order.snapshot();
                if (state.activeToken() != null || state.state() != Hk3ExactOrder.State.COMPLETE
                        && state.state() != Hk3ExactOrder.State.CANCELLED) {
                    entry.note = "前置生产 " + supply.target.getDisplayName().getString() + " / "
                            + state.state() + " / " + supply.note;
                    if (state.state() == Hk3ExactOrder.State.PAUSED) entry.paused = true;
                    if (state.state() == Hk3ExactOrder.State.READY && entry.nexusParent != null && !supply.missingSupply.isEmpty()) {
                        var nexus = parentNexus(binding, entry);
                        if (nexus == null) return false;
                        for (var need : supply.missingSupply.entrySet()) {
                            var key = need.getKey();
                            BigInteger shortage = nexus.missingAmount(key, need.getValue());
                            if (shortage.signum() <= 0 || !entry.supplyRoutes.containsKey(key)
                                    && !onlyConditional((CraftingService) grid.getCraftingService(), key)) continue;
                            Hk3ExactOrderService.stopSupply(server, entry.id, entry.supplyOrder, false);
                            startSupplyRoute(server, entry, binding, key, shortage);
                            break;
                        }
                    }
                    return false;
                }
                forgetSupply(server, entry);
                if (!persist(server, entry)) return false;
            }
            for (var input : entry.inputs.entrySet()) {
                long shortage = input.getValue() - storage.extract(input.getKey(), input.getValue(), Actionable.SIMULATE, source);
                if (shortage == 0) continue;
                if (grid.getCraftingService().getCraftingFor(input.getKey()).isEmpty()) {
                    entry.note = "等待基础原料 " + input.getKey().getDisplayName().getString() + "；没有确定性前置样板";
                    return false;
                }
                if (entry.nexusParent != null && onlyConditional((CraftingService) grid.getCraftingService(), input.getKey())) {
                    startSupplyRoute(server, entry, binding, input.getKey(), BigInteger.valueOf(shortage));
                    return false;
                }
                var supply = Hk3ExactOrderService.createSupply(binding.player, entry.id, input.getKey(), shortage);
                if (supply == null) { entry.note = "等待确定性订单空位；未预留概率尝试"; return false; }
                entry.supplyOrder = supply.order.snapshot().orderId();
                entry.note = "已建立确定性前置生产；未预留概率尝试";
                if (!persist(server, entry)) return false;
                startMaterialSupply(binding, entry);
                return false;
            }
            return true;
        } catch (IOException failure) {
            entry.paused = true;
            entry.note = "前置订单写盘失败：" + failure.getMessage();
            persist(server, entry);
            return false;
        }
    }

    private static void startSupplyRoute(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry, Binding binding,
                                         AEKey key, BigInteger shortage) {
        var route = entry.supplyRoutes.get(key);
        BigInteger left = remainingAttempts(entry).subtract(BigInteger.ONE);
        if (route == null || left.signum() <= 0) {
            stopNexusSupply(server, entry, route == null ? "缺少已确认的上游概率路线：" + key.getDisplayName().getString()
                    : "剩余次数不足以同时生产原料和成品");
            return;
        }
        try { route.start(binding.player, binding.provider.getGrid(), left, shortage, UUID.randomUUID(), entry.nexusParent, entry, null); }
        catch (IllegalArgumentException unavailable) { stopNexusSupply(server, entry, unavailable.getMessage()); }
    }

    private static boolean resumeMaterialSupply(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry, Binding binding) {
        try {
            startMaterialSupply(binding, entry);
            return true;
        } catch (IOException failure) {
            entry.paused = true;
            entry.note = "前置订单恢复失败：" + failure.getMessage();
            persist(server, entry);
            return false;
        }
    }

    private static BigInteger remainingAttempts(Hk3ProbabilityOrderData.Entry entry) {
        var ledger = entry.ledger.snapshot();
        return ledger.plan().attemptLimit().subtract(ledger.allocatedAttempts()).subtract(entry.supplyAttempts);
    }

    private static void stopNexusSupply(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry, String reason) {
        entry.ledger.cancel();
        if (!stopSupply(server, entry, true)) return;
        entry.phase = Phase.COMPLETED;
        entry.note = reason;
        persist(server, entry);
    }

    private static boolean stopSupply(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry, boolean cancel) {
        if (entry.supplyOrder == null) return true;
        try {
            Hk3ExactOrderService.stopSupply(server, entry.id, entry.supplyOrder, cancel);
            return true;
        } catch (IOException failure) {
            entry.paused = true;
            entry.note = "前置订单停止未落盘：" + failure.getMessage();
            persist(server, entry);
            return false;
        }
    }

    private static boolean supplySettled(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry) throws IOException {
        if (entry.supplyOrder == null) return true;
        var state = Hk3ExactOrderService.supply(server, entry.id, entry.supplyOrder).order.snapshot();
        return state.activeToken() == null && (state.state() == Hk3ExactOrder.State.COMPLETE
                || state.state() == Hk3ExactOrder.State.CANCELLED);
    }

    private static void forgetSupply(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry) throws IOException {
        if (entry.supplyOrder == null) return;
        Hk3ExactOrderService.forgetSupply(server, entry.id, entry.supplyOrder);
        entry.supplyOrder = null;
    }

    private static void loadBatch(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry, Binding binding) {
        if (entry.nexusParent != null && remainingAttempts(entry).signum() <= 0) {
            stopNexusSupply(server, entry, "共享尝试次数已用完");
            return;
        }
        if (!empty(binding.provider)) { entry.paused = true; entry.note = "专属总成出现外来投料"; persist(server, entry); return; }
        var converted = convert(entry);
        if (!converted.machine.equals(entry.machineInputs) || !converted.returned.equals(entry.returnedContainers)) {
            entry.paused = true;
            entry.note = "原填充容器的实际排空结果已变化；未提取本批原料";
            persist(server, entry);
            return;
        }
        if (!supplyInputs(server, entry, binding)) return;
        var storage = binding.provider.getGrid().getStorageService().getInventory();
        var source = IActionSource.ofPlayer(binding.player);
        var pending = entry.ledger.begin(entry.satisfied());
        if (pending.isEmpty()) return;
        entry.phase = Phase.TRANSFERRING;
        if (!persist(server, entry)) return;
        for (var input : entry.inputs.entrySet()) {
            long extracted = storage.extract(input.getKey(), input.getValue(), Actionable.MODULATE, source);
            entry.escrow.merge(input.getKey(), BigInteger.valueOf(extracted), BigInteger::add);
            if (extracted != input.getValue()) {
                entry.phase = Phase.COMPLETED;
                entry.ledger.cancel();
                entry.ledger.withdrawUnstarted(entry.ledger.snapshot().pending().token());
                entry.note = "AE实际提取不足，已停止；实际提取物料保留待领取";
                persist(server, entry);
                return;
            }
        }
        entry.escrow.clear();
        converted.machine.forEach((key, amount) -> entry.escrow.merge(key, BigInteger.valueOf(amount), BigInteger::add));
        converted.returned.forEach((key, amount) -> entry.escrow.merge(key, BigInteger.valueOf(amount), BigInteger::add));
        converted.returned.forEach((key, amount) -> {
            if (entry.goals.containsKey(key)) entry.actualOutputs.merge(key, BigInteger.valueOf(amount), BigInteger::add);
        });
        if (!entry.containerInputs.isEmpty() && !persist(server, entry)) return;
        KeyCounter counter = new KeyCounter();
        converted.machine.forEach(counter::add);
        KeyCounter[] counters = {counter};
        boolean pushed;
        authorizedPush = binding.provider;
        try { pushed = binding.provider.pushPattern(binding.pattern, counters); }
        finally { authorizedPush = null; }
        if (pushed) {
            converted.machine.forEach((key, amount) -> entry.escrow.compute(key,
                    (resource, held) -> held.subtract(BigInteger.valueOf(amount))));
            entry.escrow.values().removeIf(amount -> amount.signum() == 0);
        }
        entry.phase = pushed ? Phase.LOADED : Phase.COMPLETED;
        if (!pushed) {
            entry.ledger.cancel();
            entry.ledger.withdrawUnstarted(entry.ledger.snapshot().pending().token());
        }
        entry.note = pushed ? "真实原料已投入指定总成槽位；实际排空容器专属托管"
                : "总成拒绝投料，实际原料及排空容器保留待领取";
        binding.provider.getHolder().getSelf().setChanged();
        persist(server, entry);
    }

    private static Inputs convert(Hk3ProbabilityOrderData.Entry entry) {
        Map<AEKey, Long> machine = new LinkedHashMap<>(entry.inputs);
        Map<AEKey, Long> returned = new LinkedHashMap<>();
        entry.containerInputs.forEach((key, count) -> {
            var drain = drain(key);
            machine.compute(key, (resource, amount) -> amount - count);
            machine.merge(drain.fluid, Math.multiplyExact(drain.amount, count), Math::addExact);
            drain.returned.forEach((resource, amount) -> returned.merge(resource, Math.multiplyExact(amount, count), Math::addExact));
        });
        machine.values().removeIf(amount -> amount == 0);
        return new Inputs(entry.inputs, machine, entry.containerInputs, returned);
    }

    private static IPatternDetails patternAt(MEPatternBufferPartMachine provider, int slot) {
        return ((Hk3ProbabilityPatternSlot) provider).hk3gtl$patterns().inverse().get(slot);
    }

    private record Binding(Hk3WorkableMultiblockMachine machine, MEPatternBufferPartMachine provider, ServerPlayer player, IPatternDetails pattern) {}

    private static Binding binding(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry) {
        ServerPlayer player = server.getPlayerList().getPlayer(entry.owner);
        ServerLevel level = server.getLevel(ResourceKey.create(Registries.DIMENSION, new ResourceLocation(entry.dimension)));
        if (player == null || level == null || !level.hasChunkAt(BlockPos.of(entry.controller)) || !level.hasChunkAt(BlockPos.of(entry.assembly))) return null;
        var provider = assembly(MetaMachine.getMachine(level, BlockPos.of(entry.assembly)));
        if (!(MetaMachine.getMachine(level, BlockPos.of(entry.controller)) instanceof Hk3WorkableMultiblockMachine machine)
                || provider == null) return null;
        if (!entry.machineIdentity.equals(machine.getProbabilityIdentity())
                || !entry.assemblyIdentity.equals(((Hk3ProbabilityAssemblyIdentity) provider).hk3gtl$probabilityIdentity())
                || !entry.team.equals(machine.getResearchTeamUUID()) || !entry.team.equals(Hk3ResearchTeams.scope(server, entry.owner))
                || !machine.isFormed() || !provider.getMainNode().isActive() || provider.getGrid() == null
                || provider.getControllers().size() != 1 || !provider.getControllers().contains(machine)
                || !provider.getProxies().isEmpty() || !provider.getBoundProxyPositions().isEmpty()
                || !access(provider).hk3gtl$hasUnitScale()) return null;
        if (entry.slot >= provider.getPatternInventory().getSlots()
                || !entry.pattern.equals(provider.getPatternInventory().getStackInSlot(entry.slot).save(new CompoundTag()))) return null;
        var pattern = patternAt(provider, entry.slot);
        GTRecipe recipe = boundRecipe(provider, entry.slot);
        if (pattern == null || recipe == null || !entry.recipeId.equals(recipe.id.toString()) || !entry.recipe.equals(encode(recipe))) return null;
        for (Object raw : (Object[]) provider.getInternalInventory()) {
            var inventory = (Hk3ProbabilitySlotAccess) raw;
            if (inventory.hk3gtl$index() != entry.slot && (!inventory.hk3gtl$items().isEmpty() || !inventory.hk3gtl$fluids().isEmpty())) return null;
        }
        return new Binding(machine, provider, player, pattern);
    }

    private static Hk3ProbabilityOrderData.Entry locked(MetaMachine machine) {
        if (!(machine.getLevel() instanceof ServerLevel level)) return null;
        return Hk3ProbabilityOrderData.get(level.getServer()).controllers.get(
                new Hk3ProbabilityOrderData.Location(level.dimension().location().toString(), machine.getPos().asLong()));
    }

    private static Hk3ProbabilityOrderData.Entry owned(ServerPlayer player, UUID id) {
        var entry = Hk3ProbabilityOrderData.get(player.server).entries.get(id);
        require(entry != null && entry.owner.equals(player.getUUID()), "仅原付款人可管理这一订单");
        return entry;
    }

    private static Hk3ProbabilityOrderData.Group ownedGroup(ServerPlayer player, UUID id) {
        var group = Hk3ProbabilityOrderData.get(player.server).groups.get(id);
        require(group.owner.equals(player.getUUID()), "仅原付款人可管理这一多路线订单");
        return group;
    }

    private static boolean matches(Hk3ProbabilityOrderData.Entry entry, GTRecipe recipe) {
        var pending = entry.ledger.snapshot().pending();
        return recipe != null && pending != null && recipe.data.hasUUID(TOKEN) && recipe.data.getUUID(TOKEN).equals(pending.token())
                && (!recipe.data.hasUUID(ORDER) || entry.id.equals(recipe.data.getUUID(ORDER)))
                && recipe.id.toString().equals(entry.recipeId) && recipe.parallels == 1;
    }

    private static boolean empty(MEPatternBufferPartMachine provider) {
        return Arrays.stream((Object[]) provider.getInternalInventory()).map(Hk3ProbabilitySlotAccess.class::cast)
                .allMatch(inventory -> inventory.hk3gtl$items().isEmpty() && inventory.hk3gtl$fluids().isEmpty()
                        && inventory.hk3gtl$virtualItems().isEmpty() && inventory.hk3gtl$virtualFluids().isEmpty());
    }

    private static boolean slotMatches(MEPatternBufferPartMachine provider, Hk3ProbabilityOrderData.Entry entry) {
        Map<AEKey, Long> actual = new LinkedHashMap<>();
        var inventory = slot(provider, entry.slot);
        inventory.hk3gtl$items().forEach((key, amount) -> actual.put(key, amount));
        inventory.hk3gtl$fluids().forEach((key, amount) -> actual.put(key, amount));
        return actual.equals(entry.machineInputs);
    }

    private static Hk3ProbabilitySlotAccess slot(MEPatternBufferPartMachine provider, int index) {
        Object[] slots = provider.getInternalInventory();
        return (Hk3ProbabilitySlotAccess) slots[index];
    }

    private static CompoundTag encode(GTRecipe recipe) {
        return (CompoundTag) GTRecipeSerializer.CODEC.encodeStart(NbtOps.INSTANCE, recipe).getOrThrow(false, LogUtils.getLogger()::error);
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

    private static boolean persist(MinecraftServer server, Hk3ProbabilityOrderData.Entry entry) {
        try { Hk3ProbabilityOrderData.get(server).checkpoint(server); return true; }
        catch (IOException failure) {
            entry.phase = Phase.UNKNOWN;
            entry.paused = true;
            entry.note = "账本写盘失败，保留令牌并冻结所有重放";
            LogUtils.getLogger().error("HK3概率订单写盘失败：{}", entry.id, failure);
            return false;
        }
    }

    private static void validateRecipe(GTRecipe recipe) {
        require(recipe.parallels == 1 && !recipe.isFuel && recipe.ingredientActions.isEmpty(), "首版不支持合并、燃料或KubeJS物料动作配方");
        require(recipe.inputs.keySet().stream().allMatch(cap -> cap == ItemRecipeCapability.CAP || cap == FluidRecipeCapability.CAP)
                && recipe.outputs.keySet().stream().allMatch(cap -> cap == ItemRecipeCapability.CAP || cap == FluidRecipeCapability.CAP), "首尾IO仅支持真实物品与流体");
        require(recipe.tickInputs.keySet().stream().allMatch(cap -> cap == EURecipeCapability.CAP) && recipe.tickOutputs.isEmpty(), "首版逐tick IO只保留真实EU消耗，HW沿HK工作票据结算");
        for (var content : recipe.inputs.values().stream().flatMap(List::stream).toList())
            require((content.chance == 0 || content.chance == content.maxChance) && content.tierChanceBoost == 0,
                    "投料只支持必消耗原料与原生催化仓内不消耗标准件，不接概率投料");
        require(recipe.getOutputContents(ItemRecipeCapability.CAP).stream().allMatch(content -> {
            var ingredient = ItemRecipeCapability.CAP.of(content.content);
            return fixed(ingredient) && ingredient.getItems().length == 1
                    && ingredient.getItems()[0].getCount() > 0;
        }), "物品产物须为固定资源和数量");
        require(recipe.getOutputContents(FluidRecipeCapability.CAP).stream().allMatch(content -> {
            var ingredient = FluidRecipeCapability.CAP.of(content.content);
            return ingredient.getClass() == FluidIngredient.class && ingredient.values.length == 1
                    && ingredient.values[0].getClass() == FluidIngredient.FluidValue.class
                    && ingredient.getStacks().length == 1 && ingredient.getAmount() > 0;
        }), "流体产物须为固定单资源和正数量");
        require(recipe.outputChanceLogics.values().stream().allMatch(logic -> logic == ChanceLogic.OR), "首版只接独立OR概率逻辑");
    }

    private static Inputs inputs(GTRecipe recipe, IPatternDetails pattern) {
        Map<AEKey, Long> costs = new LinkedHashMap<>();
        for (var input : pattern.getInputs()) {
            require(input.getPossibleInputs().length == 1, "请用固定资源样板，首版不接替代输入");
            var stack = input.getPossibleInputs()[0];
            require(stack.what() instanceof AEItemKey || stack.what() instanceof AEFluidKey, "首版不接特殊AE资源");
            costs.merge(stack.what(), Math.multiplyExact(stack.amount(), input.getMultiplier()), Math::addExact);
        }
        Map<AEKey, Long> remaining = new LinkedHashMap<>(costs);
        Map<AEKey, Long> machine = new LinkedHashMap<>();
        Map<AEItemKey, Long> containers = new LinkedHashMap<>();
        Map<AEKey, Long> returned = new LinkedHashMap<>();
        for (var content : recipe.getInputContents(ItemRecipeCapability.CAP)) {
            if (content.chance == 0) continue;
            Ingredient ingredient = ItemRecipeCapability.CAP.of(content.content);
            require(fixed(ingredient), "首版不接范围或自定义动态投料数量");
            long amount = ingredient instanceof SizedIngredient sized ? sized.getAmount() : 1;
            for (var candidate : remaining.entrySet()) if (candidate.getKey() instanceof AEItemKey item && ingredient.test(item.toStack())) {
                long consumed = Math.min(amount, candidate.getValue());
                candidate.setValue(candidate.getValue() - consumed);
                if (consumed > 0) machine.merge(candidate.getKey(), consumed, Math::addExact);
                amount -= consumed;
            }
            require(amount == 0, "样板物品投料不等于绑定配方的一次真实消耗");
        }
        for (var candidate : remaining.entrySet()) if (candidate.getValue() > 0 && candidate.getKey() instanceof AEItemKey item) {
            var drain = drain(item);
            long count = candidate.getValue();
            containers.put(item, count);
            machine.merge(drain.fluid, Math.multiplyExact(drain.amount, count), Math::addExact);
            drain.returned.forEach((key, amount) -> returned.merge(key, Math.multiplyExact(amount, count), Math::addExact));
            candidate.setValue(0L);
        }
        Map<AEKey, Long> fluidInputs = new LinkedHashMap<>();
        remaining.forEach((key, amount) -> {
            if (key instanceof AEFluidKey && amount > 0) machine.merge(key, amount, Math::addExact);
        });
        machine.forEach((key, amount) -> {
            if (key instanceof AEFluidKey) fluidInputs.put(key, amount);
        });
        for (var content : recipe.getInputContents(FluidRecipeCapability.CAP)) {
            if (content.chance == 0) continue;
            FluidIngredient ingredient = FluidRecipeCapability.CAP.of(content.content);
            long amount = ingredient.getAmount();
            for (var candidate : fluidInputs.entrySet()) if (candidate.getKey() instanceof AEFluidKey fluid
                    && ingredient.test(com.lowdragmc.lowdraglib.side.fluid.FluidStack.create(fluid.getFluid(), 1, fluid.getTag()))) {
                long consumed = Math.min(amount, candidate.getValue());
                candidate.setValue(candidate.getValue() - consumed);
                amount -= consumed;
            }
            require(amount == 0, "样板流体投料不等于绑定配方的一次真实消耗");
        }
        require(!costs.isEmpty() && fluidInputs.values().stream().allMatch(amount -> amount == 0), "样板存在多余投料或空投料");
        return new Inputs(costs, machine, containers, returned);
    }

    private static Drain drain(AEItemKey key) {
        var handler = FluidUtil.getFluidHandler(key.toStack(1));
        require(handler.isPresent(), "样板多余物品不是可实际排空的流体容器");
        var inventory = handler.orElseThrow(IllegalArgumentException::new);
        require(inventory.getTanks() == 1, "只接固定单流体容器");
        var stored = inventory.getFluidInTank(0).copy();
        require(!stored.isEmpty(), "流体容器须实际装有流体");
        var drained = inventory.drain(stored.getAmount(), IFluidHandler.FluidAction.EXECUTE);
        require(drained.isFluidEqual(stored) && drained.getAmount() == stored.getAmount()
                && inventory.getFluidInTank(0).isEmpty(), "流体容器须能完整排空一次");
        Map<AEKey, Long> returned = new LinkedHashMap<>();
        var container = inventory.getContainer();
        if (!container.isEmpty()) returned.put(AEItemKey.of(container), (long) container.getCount());
        return new Drain(AEFluidKey.of(drained.getFluid(), drained.getTag()), drained.getAmount(), returned);
    }

    private static boolean fixed(Ingredient ingredient) {
        while (ingredient instanceof SizedIngredient sized) ingredient = sized.getInner();
        return ingredient.getClass() == Ingredient.class
                || ingredient.getClass() == net.minecraftforge.common.crafting.StrictNBTIngredient.class;
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new IllegalArgumentException(message);
    }
}
