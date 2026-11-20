package com.sirin.hk3gtl.common.machine.energy;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.lowdragmc.lowdraglib.syncdata.annotation.Persisted;
import com.lowdragmc.lowdraglib.syncdata.annotation.DescSynced;
import com.lowdragmc.lowdraglib.syncdata.field.ManagedFieldHolder;
import com.sirin.hk3gtl.common.machine.research.Hk3LateIndustrialMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;
import com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuels;
import com.sirin.hk3gtl.common.recipe.honkai.Hk3FuelBundlePlans;
import com.sirin.hk3gtl.common.research.Hk3ResearchRecipeRuntime;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.hepdd.gtmthings.data.WirelessEnergySavaedData;
import com.hepdd.gtmthings.api.misc.WirelessEnergyManager;
import com.hepdd.gtmthings.utils.TeamUtil;
import com.mojang.datafixers.util.Pair;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.Containers;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.LinkedHashSet;
import java.util.Comparator;
import java.math.BigInteger;
import java.util.UUID;
import java.util.stream.Collectors;

public final class Hk3ReactorMachine extends Hk3LateIndustrialMachine {
    private static final ManagedFieldHolder FIELDS = new ManagedFieldHolder(Hk3ReactorMachine.class, HK3_MANAGED_FIELD_HOLDER);
    private static final Map<String, Hk3ResearchProcessPlans.Plan> PLANS = Hk3ResearchProcessPlans.all().stream()
            .filter(p -> com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuels.reactor(p.role()))
            .collect(Collectors.toUnmodifiableMap(Hk3ResearchProcessPlans.Plan::id, p -> p));
    private static final Map<String, Long> OUTPUT_LIMITS = PLANS.values().stream()
            .collect(Collectors.toUnmodifiableMap(Hk3ResearchProcessPlans.Plan::role,
                    Hk3ResearchProcessPlans.Plan::outputEut, Math::max));
    @Persisted @DescSynced private double heat;
    @Persisted @DescSynced private int heatLimit = 160000;
    @Persisted @DescSynced private int fuelMultiplier = 1;
    @Persisted @DescSynced private double fuelHeatPerTick = Hk3ReactorFuels.RODS.get(0).heatPerTick();
    @Persisted @DescSynced private int rodsPerBatch = 1;
    @Persisted @DescSynced private int activityMultiplier = 1;
    @Persisted @DescSynced private boolean highGradeFuel;
    @Persisted @DescSynced private String loadedFuel = "";
    @Persisted @DescSynced private CompoundTag generationTotals = new CompoundTag();
    private boolean reconcileGeneration;

    public Hk3ReactorMachine(IMachineBlockEntity holder, String role) { super(holder, role); }
    @Override public ManagedFieldHolder getFieldHolder() { return FIELDS; }

    @Override public long getOverclockVoltage() {
        return Math.max(getMaxVoltage(), OUTPUT_LIMITS.get(researchRole()));
    }

    @Override public void onLoad() {
        super.onLoad();
        if (!isRemote()) {
            reconcileGeneration = true;
            subscribeServerTick(this::thermalTick);
        }
    }

    public boolean stageEnergyOutput(UUID owner, BigInteger amount, Hk3EnergyTick tick) {
        UUID account = TeamUtil.getTeamUUID(owner);
        String key = account.toString();
        var ledger = (Hk3ReactorGridLedger) WirelessEnergySavaedData.INSTANCE;
        tick.onCommit(() -> {
            BigInteger generated = generationTotals.contains(key)
                    ? new BigInteger(generationTotals.getString(key)) : BigInteger.ZERO;
            BigInteger next = generated.add(amount);
            generationTotals.putString(key, next.toString());
            markDirty();
            ledger.hk3gtl$creditReactor(getProbabilityIdentity(), account, next);
            WirelessEnergyManager.MachineData.put(Pair.of(owner, this), amount.longValueExact());
        });
        var logic = getRecipeLogic();
        var recipe = logic.getLastRecipe();
        BigInteger total = recipe.data.contains(Hk3LiquidProcessMachine.CREDIT, net.minecraft.nbt.Tag.TAG_STRING)
                ? new BigInteger(recipe.data.getString(Hk3LiquidProcessMachine.CREDIT))
                : BigInteger.valueOf(recipe.data.getLong(Hk3LiquidProcessMachine.CREDIT));
        BigInteger progress = BigInteger.valueOf(logic.getProgress());
        BigInteger duration = BigInteger.valueOf(logic.getDuration());
        BigInteger honkai = total.multiply(progress.add(BigInteger.ONE)).divide(duration)
                .subtract(total.multiply(progress).divide(duration));
        tick.onCommit(() -> HonkaiWirelessNetwork.insert(owner, honkai, false));
        return true;
    }

    private void reconcileGeneration() {
        var ledger = (Hk3ReactorGridLedger) WirelessEnergySavaedData.INSTANCE;
        for (String account : generationTotals.getAllKeys())
            ledger.hk3gtl$creditReactor(getProbabilityIdentity(), UUID.fromString(account),
                    new BigInteger(generationTotals.getString(account)));
    }

    @Override public boolean beforeWorking(GTRecipe recipe) {
        return loadedFuel.isEmpty() && heat < operation(recipe).heatLimit() / 10.0 && super.beforeWorking(recipe);
    }

    private Hk3FuelBundlePlans.Operation operation(GTRecipe recipe) {
        String id = recipe.data.getString(Hk3ResearchRecipeRuntime.PLAN);
        if (id.isEmpty()) id = recipe.data.getList(Hk3ResearchRecipeRuntime.MERGED, 10)
                .getCompound(0).getString(Hk3ResearchRecipeRuntime.PLAN);
        return Hk3FuelBundlePlans.get(id);
    }

    private void loadFuel(GTRecipe recipe) {
        var operation = operation(recipe);
        loadedFuel = operation.plan().inputs().get(0).id();
        fuelMultiplier = operation.bundleSize();
        rodsPerBatch = operation.rodsPerBatch();
        activityMultiplier = operation.activityMultiplier();
        fuelHeatPerTick = operation.heatPerRodTick();
        heatLimit = operation.heatLimit();
        highGradeFuel = operation.highGrade();
        markDirty();
    }

    @Override protected RecipeLogic createRecipeLogic(Object... args) {
        return new ProcessLogic(this) {
            @Override protected long getMaxParallel() { return 1; }
            @Override protected Set<GTRecipe> lookupRecipeSet() {
                return super.lookupRecipeSet().stream().sorted(Comparator.comparing(
                        (GTRecipe recipe) -> operation(recipe).plan().fluidInputs().isEmpty()))
                        .collect(Collectors.toCollection(LinkedHashSet::new));
            }
            @Override protected void doDamping() {}
            @Override public void findAndHandleRecipe() {
                if (!loadedFuel.isEmpty()) return;
                lastFailedMatches = null;
                lastRecipe = null;
                lastOriginRecipe = null;
                var recipe = getRecipe();
                if (recipe != null) setupRecipe(recipe);
                recipeDirty = pendingLookup();
            }
            @Override protected boolean handleRecipeIO(GTRecipe recipe, IO io) {
                boolean committed = super.handleRecipeIO(recipe, io);
                if (committed && io == IO.IN) loadFuel(recipe);
                return committed;
            }
            @Override public void resetRecipeLogic() {
                if (loadedFuel.isEmpty()) super.resetRecipeLogic();
                else {
                    setWaiting(Component.literal("堆芯已装料，结构恢复后继续燃烧"));
                    updateTickSubscription();
                }
            }
            @Override public void interruptRecipe() {
                if (loadedFuel.isEmpty()) super.interruptRecipe();
                else setWaiting(Component.literal("堆芯保持装料状态，等待工况恢复"));
            }
        };
    }

    @Override protected void onRequiredProcessOutput(GTRecipe recipe) {
        super.onRequiredProcessOutput(recipe);
        loadedFuel = "";
        markDirty();
    }

    private void thermalTick() {
        if (reconcileGeneration) {
            reconcileGeneration();
            reconcileGeneration = false;
        }
        heat = Math.max(0, heat + (loadedFuel.isEmpty() ? -2
                : fuelHeatPerTick * fuelMultiplier * rodsPerBatch * activityMultiplier));
        if (isFormed() && getOffsetTimer() % 20 == 0 && heat > 0)
            heat -= Hk3ReactorCooling.cool(this, highGradeFuel, heat, rodsPerBatch, activityMultiplier);
        if (heat >= heatLimit) meltDown();
        markDirty();
    }

    private void meltDown() {
        String damaged = loadedFuel.startsWith("hk3gtl:honkai_fuel_rod")
                ? loadedFuel.replace("hk3gtl:honkai_fuel_rod", "hk3gtl:broken_honkai_fuel_rod")
                : loadedFuel.startsWith("hk3gtl:dense_honkai_fuel_rod")
                ? loadedFuel.replace("hk3gtl:dense_honkai_fuel_rod", "hk3gtl:broken_dense_honkai_fuel_rod")
                : "hk3gtl:broken_" + loadedFuel.substring("hk3gtl:".length());
        loadedFuel = "";
        getRecipeLogic().interruptRecipe();
        heat = 0;
        getLevel().explode(null, getPos().getX() + 0.5, getPos().getY() + 0.5, getPos().getZ() + 0.5,
                4.0F, Level.ExplosionInteraction.BLOCK);
        getLevel().setBlockAndUpdate(getPos(), Blocks.MAGMA_BLOCK.defaultBlockState());
        Containers.dropItemStack(getLevel(), getPos().getX(), getPos().getY() + 1, getPos().getZ(),
                new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation(damaged)), rodsPerBatch));
    }

    @Override public void addDisplayText(List<Component> lines) {
        super.addDisplayText(lines);
        lines.add(Component.translatable("hk3gtl.machine.reactor.heat", heat, heatLimit));
        lines.add(Component.translatable("hk3gtl.machine.reactor.bundle", fuelMultiplier));
        lines.add(Component.translatable("hk3gtl.tooltip.reactor_fuel.heat", fuelHeatPerTick,
                fuelHeatPerTick * fuelMultiplier * rodsPerBatch * activityMultiplier));
        lines.add(Component.literal("堆芯组数：" + rodsPerBatch + "，活性倍率：" + activityMultiplier));
        lines.add(Component.translatable("hk3gtl.tooltip.reactor_fuel." + (highGradeFuel ? "high" : "low")));
        for (var coolant : Hk3ReactorCooling.Coolant.values()) {
            if (highGradeFuel && coolant != Hk3ReactorCooling.Coolant.INDUSTRIAL) continue;
            int capacity = coolant.capacityPerCycle() * rodsPerBatch * 16 * activityMultiplier;
            int maximumFluid = (int) Math.ceil((double) capacity / coolant.heatPerMb());
            lines.add(Component.translatable("hk3gtl.machine.reactor.cooling_rate",
                    Component.translatable("hk3gtl.machine.reactor.coolant." + coolant.id()),
                    coolant.heatPerMb(), capacity, maximumFluid));
        }
        BigInteger generated = generationTotals.getAllKeys().stream()
                .map(key -> new BigInteger(generationTotals.getString(key))).reduce(BigInteger.ZERO, BigInteger::add);
        lines.add(Component.literal("累计发电：" + generated + " EU"));
        lines.add(Component.translatable("hk3gtl.machine.reactor.cooling"));
    }
}
