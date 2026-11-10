package com.sirin.hk3gtl.common.recipe;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.machine.multiblock.CleanroomType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;
import com.sirin.hk3gtl.common.item.Hk3CircuitItems;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;
import java.util.function.Consumer;
import static com.sirin.hk3gtl.common.recipe.Hk3ElectronicRecipes.part;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;

/**
 * 【变更记录 #1】2026-09-26 01:58:37（第 1 次备注 · 内测5修订74）
 * 删除：无。新增：四形态封装工艺与四平台前级种子配方。
 * 修改：以真实PCB、CPU、RAM、贴片阵列、互连网及封装件组成工艺，不使用铝框/退火铜线冒充终局封装。
 * 用途：复用34条已存在的专用路线及研究绑定，系列升级精确引用前形态；MAX起步不依赖HBV电路或机壳。
 */
/**
 * 【变更记录 #2】2026-09-26 22:06:33（第 2 次备注 · 内测5修订75）
 * 删除：无。新增：六个已确认系列24条制造路线与平台映射。
 * 修改：输入仍为平台电子部件与具体前形态；首形态使用前一级电压。
 * 用途：新系列可制造，沿用现役专用机器和研究门槛，不依赖待产电路自身。
 */
/**
 * 【变更记录 #3】2026-09-30 02:17:47（第3次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/** 【变更记录 #4】2026-10-01 20:58:37（修订149）：删除本轮电路旧研究绑定；新增/修改：普通、补充系列、批量和前级种子电路全部按平台读取RN多前置；用途：新版团队研究一致核验，保留材料、耗时、能耗与历史备注，不代表结构已接通。 */
/** 【变更记录 #5】2026-10-17 16:28:34（修订165）：删除仅HBV一项的生产注册；新增52项正式电路本阶主材封装与前形态消耗；修改封装件通过CPU上游消耗以维持六种物品输入，成品在前一级供电下首制；用途：闭合四平台消费者，不恢复退役配方类型或自动授予研究。 */
public final class Hk3CircuitManufacturing {
    private Hk3CircuitManufacturing() {}

    public static int platform(Hk3CircuitCatalog.Entry entry) {
        return switch (entry.family()) {
            case "soulium_lattice", "honkai_resonance", "rhythmic_coupling", "quantum_bridge" -> 0;
            case "quantum_coherence", "entanglement_anchor", "quantum_interference", "imaginary_anchoring" -> 1;
            case "imaginary_reconstruction", "world_weaving", "causal_reconstruction", "terminal_computation" -> 2;
            case "civilization_endurance" -> 3;
            default -> throw new IllegalArgumentException("未知电路系列：" + entry.family());
        };
    }

    /** 将电子制造成本集中接入原配方入口；同系列升级必须消耗具体上一形态。 */
    public static GTRecipeBuilder assemble(GTRecipeBuilder builder, String id, long eut) {
        var entry = Hk3CircuitCatalog.ENTRIES.stream().filter(e -> e.id().equals(id)).findFirst().orElseThrow();
        int p = platform(entry);
        Hk3RecipeResearchGate.bindAll(builder.recipeType.registryName.getPath(), builder.id.getPath(),
                com.sirin.hk3gtl.common.research.Hk3ElectronicResearch.requirements(p));
        int form = entry.form();
        int units = 1 << form;
        builder.EUt(eut).duration((600 + p * 240) * (form + 1))
                .inputItems(part(p, "printed_circuit_board", units))
                .inputItems(part(p, "ram_chip", 4 * units))
                .inputItems(part(p, "interconnect_mesh", 2 * units))
                .inputItems(Hk3MainMaterialItems.stack(entry.tier(), form == 0 ? "foil" : "plate", 2 * units));
        if (form == 0) {
            builder.inputItems(part(p, "cpu", 2)).inputItems(part(p, "smd_array", 2));
        } else {
            var previous = Hk3CircuitCatalog.ENTRIES.stream()
                    .filter(e -> e.family().equals(entry.family()) && e.form() == form - 1).findFirst().orElseThrow();
            builder.inputItems(new ItemStack(Hk3CircuitItems.DETAILED_CIRCUITS.get(previous.id()).get(), 2))
                    .inputItems(part(p, "smd_array", units));
        }
        return builder.inputFluids(fluid("circuit_growth_medium", 500 * units * (p + 1)))
                .outputItems(new ItemStack(Hk3CircuitItems.DETAILED_CIRCUITS.get(id).get(), 1))
                .cleanroom(CleanroomType.CLEANROOM);
    }

    /** 每种电路首制消耗本阶主材，使用前一阶供电；同系列必须真实生产前一形态。 */
    public static void registerSeeds(Consumer<FinishedRecipe> provider) {
        for (var entry : Hk3CircuitCatalog.ENTRIES) {
            int powerTier = entry.tier() - 1;
            var builder = assemble(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_main_circuit_" + entry.id()),
                    entry.id(), Hk3Values.VA_LONG[powerTier]);
            if (powerTier > GTValues.MAX) Hk3RecipePower.require(builder, powerTier);
            builder.duration(2400 + entry.form() * 600).save(provider);
        }
    }
}

// 【变更记录 · 修订162】2026-10-17 14:40:05：删除退役设备上的补充系列及后三平台种子注册；保留MAX首制与封装成本构造器，其他种子设计目标待现行设备接线。
