package com.sirin.hk3gtl.common.recipe.soulium;

import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 魂钢产业链配方 —— 海渊闭环的材料主线。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>启动线：魂钢冶铸中心只负责前驱体和少量低效魂钢锭，避免首台海渊设备死锁</li>
 *   <li>工业线：海渊深熔精炼联合体负责纳米活化 / 原质稳定，海渊精密装配工坊负责批量凝锭</li>
 *   <li>加工线：板材/框架/细线/箔材保留 GT 标准机路线，作为早期手工加工；后续由海渊精密装配工坊承接批量路线</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>调整电压：修改 ABYSS_1_EUT</li>
 *   <li>冶铸启动配方使用 SOULIUM_SMELTING_RECIPES；批量链使用 ABYSS_VACUUM_SMELTING / ABYSS_PRECISION_ASSEMBLY</li>
 *   <li>加工配方使用 GT 标准机类型（BENDER/ASSEMBLER/WIREMILL），配方ID需加 "hk3gtl_" 前缀</li>
 *   <li>所有魂钢配方 EU/t 必须高于 MAX（Tier 14），避免 int 溢出</li>
 * </ul>
 */
public class SouliumRecipes {

    /** 海渊I阶段基准电压（EU/t） */
    private static final long HBV_EUT = Hk3Values.VA_LONG[Hk3Tiers.HBV];

    /** 注册魂钢加工配方（使用 GT 标准机：弯曲机/组装机/线材厂） */
    public static void addSouliumProcessingRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipePower.require(GTRecipeTypes.BENDER_RECIPES.recipeBuilder("hk3gtl_soulium_plate")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 128))
                .circuitMeta(1)
                .outputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 64))
                .duration(240)
                .EUt(HBV_EUT), Hk3Tiers.HBV).save(provider);

        Hk3RecipePower.require(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_soulium_frame")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .outputItems(ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 32))
                .duration(600)
                .EUt(HBV_EUT), Hk3Tiers.HBV).save(provider);

        Hk3RecipePower.require(GTRecipeTypes.WIREMILL_RECIPES.recipeBuilder("hk3gtl_soulium_fine_wire")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 256))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .outputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 512))
                .duration(400)
                .EUt(HBV_EUT), Hk3Tiers.HBV).save(provider);

        Hk3RecipePower.require(GTRecipeTypes.BENDER_RECIPES.recipeBuilder("hk3gtl_soulium_foil")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 256))
                .circuitMeta(10)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(1152))
                .outputItems(ChemicalHelper.get(TagPrefix.foil, SouliumMaterial.SOULIUM, 256))
                .duration(300)
                .EUt(HBV_EUT), Hk3Tiers.HBV).save(provider);
    }
}
