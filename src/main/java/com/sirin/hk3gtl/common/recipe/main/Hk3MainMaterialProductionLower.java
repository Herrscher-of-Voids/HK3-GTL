package com.sirin.hk3gtl.common.recipe.main;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import net.minecraft.data.recipes.FinishedRecipe;
import org.gtlcore.gtlcore.common.data.GTLRecipeTypes;

import java.util.function.Consumer;

import static com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialRecipes.*;

/**
 * 【文件职责】HBV至QAV八阶主材料实体制备；首制与L1、L3量产明确分开。
 * 【变更记录 #1】2026-10-17 16:26:09（第1次备注 · 修订165）
 * - 删除：无；不删除魂钢八步主线，不用新主材冒充旧魂钢。
 * - 新增：MAX三步首制、HBV稳定液魂钢量产、梯度/晶格/致密/层压/栅格/配对/锚定工序。
 * - 修改：每级先级实体必消耗，支线先制备再合流；配对A/B批料各自消耗后才形成配对坯。
 * - 用途：使用既有SPS、大化工、压机和线材类型；静态实体配方不冒充随机缺陷检测或同步量子态模拟。
 */
final class Hk3MainMaterialProductionLower {
    private Hk3MainMaterialProductionLower() {}

    static void register(Consumer<FinishedRecipe> out) {
        hbv(out); hcv(out); hrv(out); hdv(out); qsv(out); qcv(out); qev(out); qav(out);
    }

    private static void hbv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.HBV;
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, GTValues.MAX, "max_initial_mix", 2400)
                .inputItems(external("gtceu:chaos_plate", 16), external("gtceu:shirabon_foil", 16))
                .notConsumable(external("kubejs:ingot_field_shape", 1))
                .inputFluids(fluid("gtceu:magmatter", 1000))
                .outputItems(material(t, "stage_1", 16)).save(out);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, GTValues.MAX, "max_spatial_impregnation", 2400)
                .inputItems(material(t, "stage_1", 16))
                .inputFluids(fluid("gtceu:spatialfluid", 1000), fluid("gtceu:argon", 8000))
                .outputItems(material(t, "stage_2", 16)).save(out);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, GTValues.MAX, "max_thermal_stabilization", 3200)
                .inputItems(material(t, "stage_2", 16)).inputFluids(fluid("gtceu:argon", 16000))
                .outputItems(material(t, "billet", 16)).save(out);

        // 量产同时消耗L3魂钢和L1稳定液，首制不能取代两条正式工业线的其他产品与研究事实。
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "industrial_soulium_impregnation", 1800)
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 16))
                .inputItems(external("hk3gtl:controlled_nano_swarm", 4), external("gtceu:shirabon_foil", 16))
                .inputFluids(fluid("hk3gtl:stabilized_liquid_honkai_energy", 2000), fluid("hk3gtl:honkai_coolant", 1000))
                .outputItems(material(t, "stage_3", 16))
                .outputFluids(fluid("hk3gtl:hot_honkai_coolant", 1000)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void hcv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.HCV;
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "ceramic_impregnation_slurry", 2000)
                .inputItems(material(t - 1, "billet", 16), external("hk3gtl:nano_ceramic", 8))
                .inputFluids(fluid("gtceu:polybenzimidazole", 1152))
                .outputItems(material(t, "stage_1", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "corrosion_resistant_interface", 2400)
                .inputItems(material(t, "stage_1", 16), external("gtceu:shirabon_foil", 16))
                .inputFluids(fluid("gtceu:argon", 16000)).outputItems(material(t, "stage_2", 16)).save(out);
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "gradient_pressure_lamination", 3000)
                .inputItems(material(t, "stage_2", 16)).outputItems(material(t, "stage_3", 16)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void hrv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.HRV;
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "nano_phase_deposition", 2400)
                .inputItems(material(t - 1, "billet", 16), external("hk3gtl:controlled_nano_swarm", 8))
                .inputFluids(fluid("hk3gtl:stabilized_liquid_honkai_energy", 4000))
                .outputItems(material(t, "stage_1", 16)).save(out);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, "seeded_oriented_crystal_growth", 3200)
                .inputItems(material(t, "stage_1", 16), external("gtceu:neutronium_wafer", 4))
                .inputFluids(fluid("gtceu:argon", 24000)).outputItems(material(t, "stage_2", 16)).save(out);
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "lattice_orientation", 3200)
                .inputItems(material(t, "stage_2", 16)).outputItems(material(t, "stage_3", 16)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void hdv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.HDV;
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "multistage_densification", 3600)
                .inputItems(material(t - 1, "billet", 16), ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 16))
                .outputItems(material(t, "stage_1", 16)).save(out);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, "homogenizing_anneal", 4200)
                .inputItems(material(t, "stage_1", 16)).inputFluids(fluid("gtceu:argon", 32000))
                .outputItems(material(t, "stage_2", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "controlled_stress_release", 4200)
                .inputItems(material(t, "stage_2", 16)).inputFluids(fluid("hk3gtl:honkai_coolant", 4000))
                .outputItems(material(t, "stage_3", 16)).outputFluids(fluid("hk3gtl:hot_honkai_coolant", 4000)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void qsv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.QSV;
        process(GTRecipeTypes.WIREMILL_RECIPES, t, "conductive_mesh_layer", 3600)
                .inputItems(material(t - 1, "billet", 8), external("gtceu:fine_shirabon_wire", 32))
                .outputItems(material(t, "stage_1", 8)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "independent_dielectric_layer", 3600)
                .inputItems(material(t - 1, "billet", 8), external("hk3gtl:nano_ceramic", 16))
                .inputFluids(fluid("gtceu:polybenzimidazole", 2304))
                .outputItems(material(t, "stage_2", 8)).save(out);
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "ordered_laminate_consolidation", 4200)
                .inputItems(material(t, "stage_1", 8), material(t, "stage_2", 8))
                .outputItems(material(t, "stage_3", 16)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void qcv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.QCV;
        process(GTRecipeTypes.WIREMILL_RECIPES, t, "coherent_microgrid_drawing", 4000)
                .inputItems(material(t - 1, "billet", 16), external("hk3gtl:superconductive_metal_hydrogen", 16))
                .outputItems(material(t, "stage_1", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "cryogenic_dielectric_coating", 4400)
                .inputItems(material(t, "stage_1", 16), external("hk3gtl:nano_ceramic", 16))
                .inputFluids(fluid("gtceu:liquid_hydrogen", 4000)).outputItems(material(t, "stage_2", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "grid_isolation_encapsulation", 4800)
                .inputItems(material(t, "stage_2", 16), external("gtceu:shirabon_foil", 32))
                .inputFluids(fluid("gtceu:polybenzimidazole", 2304)).outputItems(material(t, "stage_3", 16)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void qev(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.QEV;
        for (int branch = 1; branch <= 2; branch++) {
            process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, "crystal_seed_" + branch, 4800 + branch * 400)
                    .inputItems(material(t - 1, "billet", 8), external("gtceu:neutronium_wafer", 8))
                    .inputFluids(fluid("gtceu:quantum_dots", 2000), fluid("gtceu:argon", branch * 16000))
                    .outputItems(material(t, "stage_" + branch, 8)).save(out);
        }
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "paired_lattice_assembly", 5600)
                .inputItems(material(t, "stage_1", 8), material(t, "stage_2", 8))
                .outputItems(material(t, "stage_3", 16)).save(out);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, "paired_lattice_ageing", 6000)
                .inputItems(material(t, "stage_3", 16)).inputFluids(fluid("gtceu:argon", 48000))
                .outputItems(material(t, "stage_4", 16)).save(out);
        // 以两件为完整配对，拒收量也为偶数，不给半对合格的旁路。
        quality(t, "stage_4", 16, 12, out);
    }

    private static void qav(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.QAV;
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "directional_constraint_coating", 5200)
                .inputItems(material(t - 1, "billet", 16), external("hk3gtl:nano_ceramic", 32))
                .inputFluids(fluid("gtceu:polybenzimidazole", 4608)).outputItems(material(t, "stage_1", 16)).save(out);
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "triaxial_anchor_composite", 6000)
                .inputItems(material(t, "stage_1", 16), external("hk3gtl:einstein_ringmagnet", 8))
                .outputItems(material(t, "stage_2", 16)).save(out);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, "anchored_superlattice_curing", 6800)
                .inputItems(material(t, "stage_2", 16)).inputFluids(fluid("gtceu:spatialfluid", 4000))
                .outputItems(material(t, "stage_3", 16)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    static void quality(int tier, String stage, int inputs, int accepted, Consumer<FinishedRecipe> out) {
        Hk3MainMaterialUnits.requireBalanced(inputs * 144L, accepted * 144L + (inputs - accepted) * 144L);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, tier, "surface_finish_and_batch_separation", 2400 + (tier - Hk3Tiers.HBV) * 200)
                .inputItems(material(tier, stage, inputs)).inputFluids(fluid("gtceu:argon", 16000))
                .outputItems(material(tier, "billet", accepted), material(tier, "rejected_batch", inputs - accepted)).save(out);
    }
}
