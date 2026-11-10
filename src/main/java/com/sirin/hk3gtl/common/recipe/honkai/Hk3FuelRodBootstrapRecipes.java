package com.sirin.hk3gtl.common.recipe.honkai;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Items;
import java.util.function.Consumer;

import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;

/**
 * 燃料棒研究的起步制造链；由液态工艺入口注册，I02真实输出回调负责授予实验证据。
 * 【变更记录 #1】2026-09-27 01:54:24（第 1 次备注 · 内测5修订86）
 * 删除：无，不替换旧燃料棒配方，不注册未经审批的I18结构。
 * 新增：钨钢棒壳、耐化学密封组件、100mB液体燃料封装样件及破坏性隔离检测。
 * 修改：四道工序仅要求前置RN-HFB；检测通过EXPERIMENT元数据记录RN-FRP，不能直接完成研究。
 * 用途：首份样件不依赖魂钢或I18；独立样件无发电用途，I02只接收物品，检测不返还燃料。
 */
public final class Hk3FuelRodBootstrapRecipes {
    private Hk3FuelRodBootstrapRecipes() {}

    /** 全链以已有MAX设备启动；封装研究及其后继不能成为自身实验的门槛。 */
    private static GTRecipeBuilder recipe(GTRecipeType type, String id, int ticks) {
        Hk3RecipeResearchGate.bind(type.registryName.getPath(), id, "RN-HFB");
        return type.recipeBuilder(new ResourceLocation("hk3gtl", id))
                .duration(ticks).EUt(Hk3Values.VA_LONG[GTValues.MAX]);
    }

    public static void register(Consumer<FinishedRecipe> provider) {
        recipe(GTRecipeTypes.ASSEMBLER_RECIPES, "industrial_fuel_rod_casing", 400)
                .circuitMeta(21)
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 4)
                .inputItems(TagPrefix.foil, GTMaterials.Platinum, 2)
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(144))
                .outputItems(item("honkai_fuel_rod_casing", 2)).save(provider);

        recipe(GTRecipeTypes.ASSEMBLER_RECIPES, "industrial_fuel_encapsulation_part", 300)
                .circuitMeta(22)
                .inputItems(TagPrefix.plate, GTMaterials.Polytetrafluoroethylene, 2)
                .inputItems(TagPrefix.foil, GTMaterials.Platinum, 2)
                .outputItems(item("fuel_encapsulation_part", 4)).save(provider);

        // 灌装机使用两个物品输入；不加入编程电路，以免超出原配方类型槽位。
        recipe(GTRecipeTypes.CANNER_RECIPES, "industrial_fuel_encapsulation_specimen", 200)
                .inputItems(item("honkai_fuel_rod_casing", 1), item("fuel_encapsulation_part", 1))
                .inputFluids(fluid("liquid_honkai_fuel", 100))
                .outputItems(item("fuel_encapsulation_test_specimen", 1)).save(provider);

        // 试验样件被消耗并成为不合格棒；满输出时沿用I02结算等待，不提前授予实验。
        recipe(Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS, "industrial_fuel_rod_isolation_experiment", 800)
                .circuitMeta(3)
                .inputItems(item("fuel_encapsulation_test_specimen", 1), item("honkai_reference_sample", 1))
                .inputItems(Items.PAPER, 4)
                .outputItems(item("rejected_fuel_rod", 1))
                .addData(Hk3LiquidProcessMachine.EXPERIMENT, "RN-FRP").save(provider);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
