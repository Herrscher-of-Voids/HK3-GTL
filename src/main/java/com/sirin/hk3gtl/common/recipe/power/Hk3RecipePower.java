package com.sirin.hk3gtl.common.recipe.power;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.capability.recipe.EURecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.WorkableElectricMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.hepdd.gtmthings.api.misc.WirelessEnergyManager;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.capability.Hk3GridEnergyPayment;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.machine.Hk3RecipeLogic;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.trait.Hk3PlayerGridEnergyTrait;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import org.gtlcore.gtlcore.common.machine.trait.MultipleRecipesLogic;

import java.math.BigInteger;
import java.util.List;

/**
 * 【文件职责】HK3高阶配方的额定电压、足额能源和安全执行入口；JEI与服务端共同读取配方数据。
 * 【变更记录 #1】2026-10-17 16:27:36（第1次备注 · 修订165）
 * 删除：无；新增：注册器require、只读守卫、精确倍乘/合并及已有玩家网事务支付适配。
 * 修改：只约束显式标记的HK3配方，MAX启动不标记；总功率不能代替单路电压。
 * 用途：防止GTL高压euTier钳MAX和double倍乘导致越阶/少付；未证明安全的第三方执行器明确拒绝。
 * 边界：不新增设备，不修改第三方配方；现有玩家网名义输入只到CIV，CEV仍无已验证额定承载。
 */
/**
 * 【变更记录 #2】2026-10-17 16:43:35（第2次备注 · 修订165）
 * 删除：本轮工程假设引入的单路额定限制及一律拒绝第三方载体的分支。
 * 新增：沿GTL总输入功率语义的缓冲仓事务适配与标准工作循环身份核验。
 * 修改：阶段表示需求功率阶段，进度仍由研究和材料前置决定；HK自带玩家网沿原任意精度支付语义。
 * 用途：现有GTL机器可安全执行显式HK固定工况，不假称MAX高安培是实际升压，不变更原第三方配方。
 */
/**
 * 【变更记录 #3】2026-10-17 17:58:50（第3次备注 · 修订165）
 * 删除：仅凭工作循环继承就接受未知多配方规划器的漏洞。
 * 新增：多配方选方/完工入口必须继承已接入固定工况的GTL规划器，不得另建getGTRecipe。
 * 修改：GTLAdd光子晶阵复制工况在未经安全规划适配时明确拒绝；标准维度聚焦阵列仍受支持。
 * 用途：阻止自建规划器先吃料再丢失HK费用及研究data，不扩大未验证执行路径。
 */
/** 【变更记录 #4】2026-11-05：高阶tier数据接受任意NBT数值类型；Forge运行态byte编码可正确读取，不改变功率校验规则。 */
public final class Hk3RecipePower {
    public static final String TIER_KEY = "hk3_required_voltage_tier";
    public static final String MATERIAL_TIER_KEY = "hk3_main_material_tier";
    public static final String MINIMUM_COST_KEY = "hk3_required_eut";
    private static final String INVALID_KEY = "hk3_invalid_power";
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

    private static BigInteger minimum(GTRecipe recipe) {
        return recipe.data.contains(MINIMUM_COST_KEY, Tag.TAG_STRING)
                ? new BigInteger(recipe.data.getString(MINIMUM_COST_KEY)) : Hk3GridEnergyPayment.total(amounts(recipe));
    }

    /** 检查只读，不能因显示、模拟或不满足条件而扣款。 */
    public static GTRecipe.ActionResult check(GTRecipe recipe, RecipeLogic logic) {
        if (!marked(recipe)) return GTRecipe.ActionResult.SUCCESS;
        try {
            int requiredTier = tier(recipe);
            if (requiredTier <= GTValues.MAX || requiredTier >= Hk3Values.VA_LONG.length
                    || recipe.data.getBoolean(INVALID_KEY)) return fail("invalid");
            BigInteger cost = Hk3PowerBudget.cost(amounts(recipe));
            if (cost.compareTo(minimum(recipe)) < 0
                    || cost.compareTo(BigInteger.valueOf(Hk3Values.VA_LONG[requiredTier])) < 0
                    || !recipe.hasTick() || !recipe.getTickOutputContents(EURecipeCapability.CAP).isEmpty())
                return fail("invalid");
            MetaMachine machine = logic.getMachine();
            if (machine.getLevel() == null || machine.getLevel().isClientSide()) return fail("side");
            if (logic instanceof Hk3RecipeLogic && machine instanceof Hk3WorkableMultiblockMachine hk) {
                if (source(machine) == null) return fail("executor");
                if (hk.getOwnerUUID() == null || WirelessEnergyManager.getUserEU(hk.getOwnerUUID()).compareTo(cost) < 0)
                    return fail("balance", cost.toString());
            } else {
                if (!(machine instanceof WorkableElectricMultiblockMachine) || !supported(logic)) return fail("executor");
                var ports = Hk3PowerPorts.of(logic);
                if (ports.isEmpty()) return fail("executor");
                if (Hk3PortPayment.power(ports).compareTo(cost) < 0) return fail("capacity", cost.toString());
                if (Hk3PortPayment.available(ports).compareTo(cost) < 0) return fail("balance", cost.toString());
            }
            return GTRecipe.ActionResult.SUCCESS;
        } catch (RuntimeException unavailable) {
            return fail("invalid");
        }
    }

    public static boolean supported(RecipeLogic logic) {
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
        return Hk3PortPayment.pay(Hk3PowerPorts.of(logic), Hk3PowerBudget.cost(amounts(recipe)), tick);
    }

    /** HK工作票据已开启后精确付款；其余tick IO使用移除EU的副本，避免真实仓抢先支付或重复扣款。 */
    public static boolean pay(GTRecipe recipe, Hk3RecipeLogic logic) {
        if (!marked(recipe)) return true;
        if (logic.getEnergyTick() == null || !check(recipe, logic).isSuccess()) return false;
        Hk3PlayerGridEnergyTrait source = source(logic.getMachine());
        return source != null && source.handleRecipeInner(IO.IN, recipe, amounts(recipe), null, false) == null;
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

    /** 只对标记工况修正EU倍乘；超long的单条费用显式拒绝，不使用饱和金额运行。 */
    public static void scale(GTRecipe original, GTRecipe scaled, long multiplier) {
        if (!marked(original)) return;
        scaled.data = original.data.copy();
        BigInteger multiple = BigInteger.valueOf(multiplier);
        scaled.data.putString(MINIMUM_COST_KEY, minimum(original).multiply(multiple).toString());
        try {
            if (multiplier <= 0) throw new ArithmeticException("并行必须为正数");
            var from = amounts(original);
            var contents = scaled.getTickInputContents(EURecipeCapability.CAP);
            if (from.size() != contents.size()) throw new ArithmeticException("费用条目被丢失");
            for (int i = 0; i < from.size(); i++) {
                BigInteger value = BigInteger.valueOf(from.get(i)).multiply(multiple);
                if (value.signum() <= 0 || value.compareTo(LONG_MAX) > 0) throw new ArithmeticException("单条EU费用超long");
                contents.get(i).content = value.longValueExact();
            }
        } catch (RuntimeException invalid) {
            scaled.data.putBoolean(INVALID_KEY, true);
        }
    }

    /** 合并时保留最高需求功率阶段和全部最低费用，不能只保留首条配方的数据。 */
    public static void merge(GTRecipe base, GTRecipe other) {
        if (!marked(base) && !marked(other)) return;
        BigInteger required = minimum(base).add(minimum(other));
        int highest = Math.max(tier(base), tier(other));
        boolean invalid = base.data.getBoolean(INVALID_KEY) || other.data.getBoolean(INVALID_KEY);
        base.data = base.data.copy();
        base.data.putInt(TIER_KEY, highest);
        base.data.putString(MINIMUM_COST_KEY, required.toString());
        if (invalid) base.data.putBoolean(INVALID_KEY, true);
    }

    public static Component tooltip(GTRecipe recipe) {
        if (!marked(recipe)) return Component.empty();
        try {
            int requiredTier = tier(recipe);
            if (requiredTier <= GTValues.MAX || requiredTier >= Hk3Values.VA_LONG.length) throw new IllegalArgumentException("未知电压");
            return Component.translatable("hk3gtl.recipe.power.required", Hk3Values.getVN(requiredTier),
                    Hk3Values.VA_LONG[requiredTier], Hk3PowerBudget.cost(amounts(recipe)).toString());
        } catch (RuntimeException invalid) {
            return Component.translatable("hk3gtl.recipe.power.invalid");
        }
    }

    private static GTRecipe.ActionResult fail(String reason, Object... arguments) {
        return GTRecipe.ActionResult.fail(() -> Component.translatable("hk3gtl.recipe.power." + reason, arguments));
    }
}
