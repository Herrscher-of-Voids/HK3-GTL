package com.sirin.hk3gtl.common.recipe.power;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.capability.recipe.EURecipeCapability;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.WorkableElectricMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.hepdd.gtmthings.api.misc.WirelessEnergyManager;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.capability.Hk3GridEnergyPayment;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.machine.Hk3RecipeLogic;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.trait.Hk3PlayerGridEnergyTrait;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.block.entity.BlockEntity;
import com.sirin.hk3gtl.common.easter.Hk3EggProduction;
import org.gtlcore.gtlcore.common.machine.trait.MultipleRecipesLogic;

import java.math.BigInteger;
import java.util.List;
import java.util.UUID;

/**
 * HK3高阶配方的额定电压、足额能源和安全执行入口；JEI与服务端共同读取配方数据。
 */
public final class Hk3RecipePower {
    public static final String TIER_KEY = "hk3_required_voltage_tier";
    public static final String MATERIAL_TIER_KEY = "hk3_main_material_tier";
    public static final String MINIMUM_COST_KEY = "hk3_required_eut";
    public static final String EXACT_COST_KEY = "hk3_exact_eut";
    private static final String INVALID_KEY = "hk3_invalid_power";
    private static final ThreadLocal<RecipeLogic> ISOLATED = new ThreadLocal<>();
    private static final BigInteger LONG_MAX = BigInteger.valueOf(Long.MAX_VALUE);

    private Hk3RecipePower() {}

    /** 必须在EUt后调用；MAX种子维持原有机器规则。 */
    public static GTRecipeBuilder require(GTRecipeBuilder builder, int tier) {
        if (tier < 0 || tier >= Hk3Values.VA_LONG.length) throw new IllegalArgumentException("未知配方电压阶级");
        if (tier <= GTValues.MAX) return builder;
        long cost = builder.EUt();
        if (cost < Hk3Values.VA_LONG[tier]) throw new IllegalArgumentException("高阶工况耗电低于对应电压基准");
        return builder.addData(TIER_KEY, tier).addData(MINIMUM_COST_KEY, Long.toString(cost));
    }

    public static boolean marked(GTRecipe recipe) {
        return recipe != null && (recipe.data.contains(TIER_KEY, Tag.TAG_ANY_NUMERIC)
                || recipe.data.contains(MATERIAL_TIER_KEY, Tag.TAG_ANY_NUMERIC)
                && recipe.data.getInt(MATERIAL_TIER_KEY) > GTValues.MAX);
    }

    public static int tier(GTRecipe recipe) {
        if (!marked(recipe)) return GTValues.MAX;
        return recipe.data.contains(TIER_KEY, Tag.TAG_ANY_NUMERIC) ? recipe.data.getInt(TIER_KEY)
                : recipe.data.getInt(MATERIAL_TIER_KEY);
    }

    public static List<Long> amounts(GTRecipe recipe) {
        return recipe.getTickInputContents(EURecipeCapability.CAP).stream()
                .map(content -> EURecipeCapability.CAP.of(content.content)).toList();
    }

    public static BigInteger cost(GTRecipe recipe) {
        if (hasExactCost(recipe)) return new BigInteger(recipe.data.getString(EXACT_COST_KEY));
        var amounts = amounts(recipe);
        return marked(recipe) ? Hk3PowerBudget.cost(amounts) : Hk3GridEnergyPayment.total(amounts);
    }

    public static boolean hasExactCost(GTRecipe recipe) {
        return recipe.data.contains(EXACT_COST_KEY, Tag.TAG_STRING);
    }

    private static BigInteger minimum(GTRecipe recipe) {
        return recipe.data.contains(MINIMUM_COST_KEY, Tag.TAG_STRING)
                ? new BigInteger(recipe.data.getString(MINIMUM_COST_KEY)) : Hk3GridEnergyPayment.total(amounts(recipe));
    }

    /** 检查只读，不能因显示、模拟或不满足条件而扣款。 */
    public static GTRecipe.ActionResult check(GTRecipe recipe, RecipeLogic logic) {
        boolean fixed = marked(recipe);
        MetaMachine machine = logic.getMachine();
        boolean wireless = logic instanceof Hk3RecipeLogic && machine instanceof Hk3WorkableMultiblockMachine;
        if (!fixed && (!wireless || !hasExactCost(recipe))) return GTRecipe.ActionResult.SUCCESS;
        try {
            BigInteger cost = cost(recipe);
            if (recipe.data.getBoolean(INVALID_KEY) || cost.signum() <= 0) return fail("invalid");
            if (fixed) {
                int requiredTier = tier(recipe);
                if (requiredTier <= GTValues.MAX || requiredTier >= Hk3Values.VA_LONG.length
                        || cost.compareTo(minimum(recipe)) < 0
                        || cost.compareTo(BigInteger.valueOf(Hk3Values.VA_LONG[requiredTier])) < 0
                        || !recipe.hasTick() || !recipe.getTickOutputContents(EURecipeCapability.CAP).isEmpty())
                    return fail("invalid");
            }
            if (machine.getLevel() == null || machine.getLevel().isClientSide()) return fail("side");
            if (logic instanceof Hk3RecipeLogic && machine instanceof Hk3WorkableMultiblockMachine hk) {
                if (source(machine) == null) return fail("executor");
                if (hk.getOwnerUUID() == null || WirelessEnergyManager.getUserEU(hk.getOwnerUUID()).compareTo(cost) < 0)
                    return fail("balance", cost.toString());
            } else {
                if (!(machine instanceof WorkableElectricMultiblockMachine electric) || !supported(logic)) return fail("executor");
                if (fixed && Hk3PowerPorts.inputTier(electric, GTValues.MAX) < tier(recipe))
                    return fail("rating", Hk3Values.getVN(tier(recipe)), GTValues.V[tier(recipe)]);
                var ports = Hk3PowerPorts.of(logic);
                if (ports.isEmpty()) return fail("executor");
                if (Hk3PortPayment.power(ports).compareTo(cost) < 0) return fail("capacity", cost.toString());
                if (Hk3PortPayment.availablePower(ports).compareTo(cost) < 0) return fail("balance", cost.toString());
                BigInteger honkai = Hk3DualEnergyCosts.getMergedCost(recipe);
                if (honkai != null && honkai.signum() > 0) {
                    UUID payer = externalPayer(machine);
                    if (payer == null || HonkaiWirelessNetwork.getStoredAmount(payer).compareTo(honkai) < 0)
                        return fail("honkai_balance", honkai.toString());
                }
            }
            return GTRecipe.ActionResult.SUCCESS;
        } catch (RuntimeException unavailable) {
            return fail("invalid");
        }
    }

    public static GTRecipe.ActionResult checkIsolated(GTRecipe recipe, RecipeLogic logic) {
        if (!marked(recipe)) return recipe.checkConditions(logic);
        RecipeLogic previous = ISOLATED.get();
        ISOLATED.set(logic);
        try { return recipe.checkConditions(logic); }
        finally { if (previous == null) ISOLATED.remove(); else ISOLATED.set(previous); }
    }

    public static boolean supported(RecipeLogic logic) {
        if (ISOLATED.get() == logic || logic instanceof Hk3PowerWork.Isolated || logic instanceof Hk3PowerWork.Batch) return true;
        if (logic instanceof Hk3PowerWork.Mutable mutable && mutable.hk3gtl$usesFixedMutablePower()) return true;
        try {
            return logic instanceof Hk3PowerWork
                    && logic.getClass().getMethod("handleRecipeWorking").getDeclaringClass() == RecipeLogic.class
                    && (!(logic instanceof MultipleRecipesLogic)
                    || Hk3PowerPlanner.inherits(logic.getClass(), MultipleRecipesLogic.class,
                    "findAndHandleRecipe", "onRecipeFinish"));
        } catch (ReflectiveOperationException unsupported) { return false; }
    }

    /** 标准外部循环使用其现有物理/无线缓冲仓；服务器线程串行付款，失败交给票据逆序退款。 */
    public static boolean pay(GTRecipe recipe, RecipeLogic logic, Hk3EnergyTick tick) {
        if (!check(recipe, logic).isSuccess() || logic.getMachine().getLevel() == null
                || !logic.getMachine().getLevel().getServer().isSameThread()) return false;
        BigInteger honkai = Hk3DualEnergyCosts.getMergedCost(recipe);
        return Hk3PortPayment.pay(Hk3PowerPorts.of(logic), cost(recipe), tick)
                && reserveHonkai(logic, honkai, tick);
    }

    public static boolean reserveHonkai(RecipeLogic logic, BigInteger cost, Hk3EnergyTick tick) {
        return cost == null || cost.signum() == 0 || HonkaiWirelessNetwork.reserve(externalPayer(logic.getMachine()), cost, tick);
    }

    public static GTRecipe isolatedTick(GTRecipe tick) {
        tick.data = tick.data.copy();
        tick.data.remove(TIER_KEY);
        tick.data.remove(MATERIAL_TIER_KEY);
        tick.data.remove(MINIMUM_COST_KEY);
        tick.data.remove(EXACT_COST_KEY);
        return tick;
    }

    static UUID externalPayer(MetaMachine machine) {
        if (machine instanceof Hk3WorkableMultiblockMachine owned) return owned.getOwnerUUID();
        var data = ((BlockEntity) machine.getHolder()).getPersistentData();
        return data.hasUUID(Hk3EggProduction.OWNER) ? data.getUUID(Hk3EggProduction.OWNER) : null;
    }

    /** HK工作票据已开启后精确付款；其余tick IO使用移除EU的副本，避免真实仓抢先支付或重复扣款。 */
    public static boolean pay(GTRecipe recipe, Hk3RecipeLogic logic) {
        if (!marked(recipe) && !hasExactCost(recipe)) return true;
        if (logic.getEnergyTick() == null || !check(recipe, logic).isSuccess()) return false;
        Hk3PlayerGridEnergyTrait source = source(logic.getMachine());
        return source != null && source.consumeEnergy(cost(recipe));
    }

    public static GTRecipe withoutEU(GTRecipe recipe) {
        GTRecipe copy = recipe.copy();
        copy.tickInputs.remove(EURecipeCapability.CAP);
        copy.tickInputChanceLogics.remove(EURecipeCapability.CAP);
        return copy;
    }

    private static Hk3PlayerGridEnergyTrait source(MetaMachine machine) {
        return machine.getTraits().stream().filter(Hk3PlayerGridEnergyTrait.class::isInstance)
                .map(Hk3PlayerGridEnergyTrait.class::cast).findFirst().orElse(null);
    }

    /** 倍乘费用保留精确总额，Long内容只保留显示值。 */
    public static void scale(GTRecipe original, GTRecipe scaled, long multiplier) {
        boolean fixed = marked(original);
        var from = amounts(original);
        if (!fixed && Hk3GridEnergyPayment.total(from).signum() == 0) return;
        scaled.data = original.data.copy();
        BigInteger multiple = BigInteger.valueOf(multiplier);
        if (fixed) {
            scaled.data.putString(MINIMUM_COST_KEY, minimum(original).multiply(multiple).toString());
        }
        try {
            if (multiplier <= 0) throw new ArithmeticException("并行必须为正数");
            var contents = scaled.getTickInputContents(EURecipeCapability.CAP);
            if (from.size() != contents.size()) throw new ArithmeticException("费用条目被丢失");
            scaled.data.putString(EXACT_COST_KEY, cost(original).multiply(multiple).toString());
            for (int i = 0; i < from.size(); i++) {
                BigInteger value = BigInteger.valueOf(from.get(i)).multiply(multiple);
                if (value.signum() < 0 || fixed && value.signum() == 0)
                    throw new ArithmeticException("运行耗电不符合配方要求");
                contents.get(i).content = value.min(LONG_MAX).longValueExact();
            }
        } catch (RuntimeException invalid) {
            scaled.data.putBoolean(INVALID_KEY, true);
        }
    }

    /** 合并时保留最高需求功率阶段和全部最低费用，不能只保留首条配方的数据。 */
    public static void merge(GTRecipe base, GTRecipe other) {
        BigInteger mergedCost = cost(base).add(cost(other));
        if (!marked(base) && !marked(other)) {
            if (mergedCost.signum() > 0) {
                base.data = base.data.copy();
                base.data.putString(EXACT_COST_KEY, mergedCost.toString());
            }
            return;
        }
        BigInteger required = minimum(base).add(minimum(other));
        int highest = Math.max(tier(base), tier(other));
        boolean invalid = base.data.getBoolean(INVALID_KEY) || other.data.getBoolean(INVALID_KEY);
        base.data = base.data.copy();
        base.data.putInt(TIER_KEY, highest);
        base.data.putString(MINIMUM_COST_KEY, required.toString());
        base.data.putString(EXACT_COST_KEY, mergedCost.toString());
        if (invalid) base.data.putBoolean(INVALID_KEY, true);
    }

    public static GTRecipe.ActionResult unsupportedExecutor() {
        return fail("executor");
    }

    private static GTRecipe.ActionResult fail(String reason, Object... arguments) {
        return GTRecipe.ActionResult.fail(() -> Component.translatable("hk3gtl.recipe.power." + reason, arguments));
    }
}
