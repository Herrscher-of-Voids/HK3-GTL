package com.sirin.hk3gtl.common.recipe.soulium;



import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTItems;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;
import org.gtlcore.gtlcore.common.data.GTLMaterials;

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
    private static final long ABYSS_1_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1];
    /** 海渊II阶段基准电压（EU/t） */
    private static final long ABYSS_2_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_2];

    /**
     * 注册魂钢主链。
     * <p>设计原则：冶铸中心提供启动批次，深熔/精密装配提供真正工业产能。</p>
     */
    public static void addSouliumSmeltingRecipes(Consumer<FinishedRecipe> provider) {
        // 启动线第一步：外部 GTL 高阶材料 + 神经处理器 + 崩坏能结晶 -> 魂钢前体。
        // 只放在魂钢冶铸中心，作为整个海渊材料链的入口。
        Hk3RecipeTypes.SOULIUM_SMELTING_RECIPES.recipeBuilder("precursor_mix")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Shirabon, 512))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 256))
                .inputItems(GTItems.NEURO_PROCESSOR.asStack(512))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .outputItems(new ItemStack(SouliumChainItems.SOULIUM_PRECURSOR_MIX.get(), 256))
                .duration(800)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 启动线兜底：低效率直接凝锭，只用于造第一批深熔/精密装配设备。
        // 效率明显低于完整工业线，避免玩家长期用单机替代整条海渊闭环。
        Hk3RecipeTypes.SOULIUM_SMELTING_RECIPES.recipeBuilder("bootstrap_soulium_ingot")
                .inputItems(new ItemStack(SouliumChainItems.SOULIUM_PRECURSOR_MIX.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .outputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 16))
                .duration(1200)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 工业线第二步：海渊深熔精炼联合体完成纳米活化。
        // 这里开始引入液态崩坏能作为反应环境，体现“纳米机器人集群”而非普通合金。
        Hk3RecipeTypes.ABYSS_VACUUM_SMELTING_RECIPES.recipeBuilder("soulium_nano_activation")
                .inputItems(new ItemStack(SouliumChainItems.SOULIUM_PRECURSOR_MIX.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(8000))
                .outputItems(new ItemStack(SouliumChainItems.ACTIVATED_NANO_MATRIX.get(), 192))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(500))
                .duration(900)
                .EUt(ABYSS_2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_vacuum_smelting", "soulium_nano_activation", "R-AB-013");

        // 工业线第三步：海渊深熔精炼联合体完成崩坏能注入和初生质聚集。
        Hk3RecipeTypes.ABYSS_VACUUM_SMELTING_RECIPES.recipeBuilder("soulium_proto_mass_growth")
                .inputItems(new ItemStack(SouliumChainItems.ACTIVATED_NANO_MATRIX.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(SouliumChainItems.SOULIUM_PROTO_MASS.get(), 160))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 4))
                .duration(900)
                .EUt(ABYSS_2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_vacuum_smelting", "soulium_proto_mass_growth", "R-AB-013");

        // 工业线第四步：海渊精密装配工坊用稳定晶体和数据控制把初生质定形成魂钢锭。
        // 输出量高于 bootstrap，要求玩家搭建跨机器物流后才获得真正批量产能。
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("soulium_industrial_ingot_casting")
                .inputItems(new ItemStack(SouliumChainItems.SOULIUM_PROTO_MASS.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 192))
                .duration(1000)
                .EUt(ABYSS_2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_precision_assembly", "soulium_industrial_ingot_casting", "R-AB-012");

        // 工业线延伸：稳定魂钢初生质，作为海渊 III/IV 八大件和定向构件的前置。
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("stabilized_proto_mass_industrial")
                .inputItems(new ItemStack(SouliumChainItems.SOULIUM_PROTO_MASS.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(SouliumChainItems.STABILIZED_SOULIUM_PROTO_MASS.get(), 96))
                .duration(1200)
                .EUt(ABYSS_2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_precision_assembly", "stabilized_proto_mass_industrial", "R-AB-012");
    }

    /** 注册魂钢加工配方（使用 GT 标准机：弯曲机/组装机/线材厂） */
    public static void addSouliumProcessingRecipes(Consumer<FinishedRecipe> provider) {
        GTRecipeTypes.BENDER_RECIPES.recipeBuilder("hk3gtl_soulium_plate")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 128))
                .circuitMeta(1)
                .outputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 64))
                .duration(240)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_soulium_frame")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .outputItems(ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 32))
                .duration(600)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        GTRecipeTypes.WIREMILL_RECIPES.recipeBuilder("hk3gtl_soulium_fine_wire")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 256))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .outputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 512))
                .duration(400)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        GTRecipeTypes.BENDER_RECIPES.recipeBuilder("hk3gtl_soulium_foil")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 256))
                .circuitMeta(10)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(1152))
                .outputItems(ChemicalHelper.get(TagPrefix.foil, SouliumMaterial.SOULIUM, 256))
                .duration(300)
                .EUt(ABYSS_1_EUT)
                .save(provider);
    }
}
