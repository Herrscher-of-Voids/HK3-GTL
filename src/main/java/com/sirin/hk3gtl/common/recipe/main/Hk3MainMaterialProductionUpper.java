package com.sirin.hk3gtl.common.recipe.main;

import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.data.recipes.FinishedRecipe;
import org.gtlcore.gtlcore.common.data.GTLRecipeTypes;

import java.util.function.Consumer;

import static com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialProductionLower.quality;
import static com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialRecipes.*;

/**
 * 【文件职责】IMV至CEV实体主材链，覆盖陶瓷、导带、重构、多轴纤维、四系统合与单向服役复核。
 * 【变更记录 #1】2026-10-17 16:27:11（第1次备注 · 修订165）
 * - 删除：无；不把废料当作重构材料首通唯一来源。
 * - 新增：先阶主材、独立功能层、四实体汇流以及不可返老化入口的修复工序。
 * - 修改：有限服役以一次老化—拆解—补料—成板的有向图表示；不伪造逐件寿命或真实裂纹测量。
 * - 用途：提供工艺实体和消费路径；高阶能源、实际机器权限和游戏测试仍需独立验证。
 * 【变更记录 #2】2026-10-17 17:03:09（第2次备注 · 修订165）
 * - 删除：CIV认知支线对尚无现役I40承载的cognitive_composite的必需输入。
 * - 新增：已接通IMV电子平台CPU作为认知模块的实物计算核心。
 * - 修改：保留WSV坯、稳定崩坏能、四路独立汇流和RN-IAA权限，不改I40规划。
 * - 用途：避免把仅已注册但无法加工的旧复合材当成已闭合上游，不新增物品或机器。
 */
final class Hk3MainMaterialProductionUpper {
    private Hk3MainMaterialProductionUpper() {}

    static void register(Consumer<FinishedRecipe> out) {
        imv(out); icv(out); irv(out); iwv(out); wfv(out); wsv(out); civ(out); cev(out);
    }

    private static void imv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.IMV;
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "ceramic_precursor_slurry", 6000)
                .inputItems(material(t - 1, "billet", 16), external("hk3gtl:nano_ceramic", 32))
                .inputFluids(fluid("gtceu:polybenzimidazole", 4608)).outputItems(material(t, "stage_1", 16)).save(out);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, "controlled_phase_transfer", 6800)
                .inputItems(material(t, "stage_1", 16), external("hk3gtl:phase_transfer_mirror", 8))
                .inputFluids(fluid("gtceu:spatialfluid", 8000)).outputItems(material(t, "stage_2", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "ceramic_quench_and_wash", 7200)
                .inputItems(material(t, "stage_2", 16)).inputFluids(fluid("hk3gtl:honkai_coolant", 8000))
                .outputItems(material(t, "stage_3", 16)).outputFluids(fluid("hk3gtl:hot_honkai_coolant", 8000)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void icv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.ICV;
        process(GTRecipeTypes.WIREMILL_RECIPES, t, "high_conductance_backing_band", 6400)
                .inputItems(material(t - 1, "billet", 16), external("hk3gtl:superconductive_metal_hydrogen", 32))
                .outputItems(material(t, "stage_1", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "multilayer_ceramic_impregnation", 7200)
                .inputItems(material(t, "stage_1", 16), material(t - 1, "foil", 32))
                .inputFluids(fluid("gtceu:polybenzimidazole", 9216)).outputItems(material(t, "stage_2", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "cryogenic_band_isolation", 8000)
                .inputItems(material(t, "stage_2", 16), external("gtceu:shirabon_foil", 32))
                .inputFluids(fluid("gtceu:liquid_hydrogen", 8000)).outputItems(material(t, "stage_3", 16)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void irv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.IRV;
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, "fresh_reconstruction_feed", 7200)
                .inputItems(material(t - 1, "billet", 16), external("gtceu:shirabon_ingot", 32))
                .inputFluids(fluid("gtceu:argon", 48000)).outputItems(material(t, "stage_1", 16)).save(out);
        // 这是消耗既有废料的补充路线；新鲜首通完全不要求本级废料。
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "classified_reconstruction_feed", 6800)
                .inputItems(material(t - 1, "billet", 8), material(t, "classified_scrap", 8))
                .inputFluids(fluid("gtceu:argon", 32000))
                .outputItems(material(t, "stage_1", 14), material(t, "unrecoverable_tailings", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "fresh_alloy_composition_adjustment", 8000)
                .inputItems(material(t, "stage_1", 16), external("gtceu:shirabon_ingot", 32))
                .inputFluids(fluid("hk3gtl:stabilized_liquid_honkai_energy", 8000))
                .outputItems(material(t, "stage_2", 16)).save(out);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, "reconstructed_alloy_anneal", 8800)
                .inputItems(material(t, "stage_2", 16)).inputFluids(fluid("gtceu:argon", 64000))
                .outputItems(material(t, "stage_3", 16)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void iwv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.IWV;
        String[] additives = {"hk3gtl:nano_ceramic", "gtceu:fine_shirabon_wire", "gtceu:carbon_fibers", "hk3gtl:controlled_nano_swarm"};
        for (int branch = 1; branch <= 4; branch++) {
            process(branch == 2 ? GTRecipeTypes.WIREMILL_RECIPES : GTRecipeTypes.LARGE_CHEMICAL_RECIPES,
                    t, "independent_reinforcement_" + branch, 7600 + branch * 400)
                    .inputItems(material(t - 1, "billet", 4), external(additives[branch - 1], 16))
                    .outputItems(material(t, "stage_" + branch, 4)).save(out);
        }
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "multiaxial_four_layer_cocure", 9600)
                .inputItems(material(t, "stage_1", 4), material(t, "stage_2", 4), material(t, "stage_3", 4), material(t, "stage_4", 4))
                .outputItems(material(t, "stage_5", 16)).save(out);
        quality(t, "stage_5", 16, 14, out);
    }

    private static void wfv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.WFV;
        process(GTRecipeTypes.WIREMILL_RECIPES, t, "reinforced_gradient_fiber", 8400)
                .inputItems(material(t - 1, "billet", 16), external("gtceu:carbon_fiber_mesh", 32))
                .outputItems(material(t, "stage_1", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "spatial_gradient_surface_treatment", 9600)
                .inputItems(material(t, "stage_1", 16), external("hk3gtl:phase_transfer_mirror", 16))
                .inputFluids(fluid("gtceu:spatialfluid", 16000)).outputItems(material(t, "stage_2", 16)).save(out);
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "oriented_fiber_layup", 10400)
                .inputItems(material(t, "stage_2", 16), material(Hk3Tiers.IWV, "foil", 32))
                .outputItems(material(t, "stage_3", 16)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void wsv(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.WSV;
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "constraint_barrier_precursor", 9200)
                .inputItems(material(t - 1, "billet", 16), external("hk3gtl:nano_ceramic", 64))
                .inputFluids(fluid("gtceu:polybenzimidazole", 18432)).outputItems(material(t, "stage_1", 16)).save(out);
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "fiber_barrier_multilayer", 10400)
                .inputItems(material(t, "stage_1", 16), material(Hk3Tiers.WFV, "foil", 32))
                .outputItems(material(t, "stage_2", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "thermal_fatigue_conditioning", 11600)
                .inputItems(material(t, "stage_2", 16)).inputFluids(fluid("hk3gtl:honkai_coolant", 16000))
                .outputItems(material(t, "stage_3", 16)).outputFluids(fluid("hk3gtl:hot_honkai_coolant", 16000)).save(out);
        quality(t, "stage_3", 16, 14, out);
    }

    private static void civ(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.CIV;
        // 四系各自实际耗料、实际输出；不能把同一件基材无耗料复制成四个模块。
        process(GTRecipeTypes.WIREMILL_RECIPES, t, "independent_energy_module", 10400)
                .inputItems(material(t - 1, "billet", 4), material(Hk3Tiers.ICV, "fine_wire", 32))
                .outputItems(material(t, "stage_1", 4)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "independent_constraint_module", 11200)
                .inputItems(material(t - 1, "billet", 4), external("hk3gtl:nano_ceramic", 32))
                .inputFluids(fluid("gtceu:polybenzimidazole", 18432)).outputItems(material(t, "stage_2", 4)).save(out);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, t, "independent_reconstruction_module", 12000)
                .inputItems(material(t - 1, "billet", 4), material(Hk3Tiers.IRV, "billet", 8))
                .inputFluids(fluid("gtceu:spatialfluid", 16000)).outputItems(material(t, "stage_3", 4)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "independent_cognitive_module", 12800)
                .inputItems(material(t - 1, "billet", 4),
                        com.sirin.hk3gtl.common.recipe.Hk3ElectronicRecipes.part(2, "cpu", 16))
                .inputFluids(fluid("hk3gtl:stabilized_liquid_honkai_energy", 16000)).outputItems(material(t, "stage_4", 4)).save(out);
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "quadrisystem_cocure", 13600)
                .inputItems(material(t, "stage_1", 4), material(t, "stage_2", 4), material(t, "stage_3", 4), material(t, "stage_4", 4))
                .outputItems(material(t, "stage_5", 16)).save(out);
        quality(t, "stage_5", 16, 14, out);
    }

    private static void cev(Consumer<FinishedRecipe> out) {
        int t = Hk3Tiers.CEV;
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "repairable_functional_layer", 12000)
                .inputItems(material(t - 1, "billet", 8), external("gtceu:shirabon_ingot", 64))
                .inputFluids(fluid("gtceu:polybenzimidazole", 18432)).outputItems(material(t, "stage_1", 8)).save(out);
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, t, "service_laminate_assembly", 13600)
                .inputItems(material(t - 1, "billet", 8), material(t, "stage_1", 8))
                .outputItems(material(t, "stage_2", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "accelerated_service_ageing", 15200)
                .inputItems(material(t, "stage_2", 16)).inputFluids(fluid("hk3gtl:honkai_coolant", 32000))
                .outputItems(material(t, "stage_3", 16)).outputFluids(fluid("hk3gtl:hot_honkai_coolant", 32000)).save(out);
        process(GTRecipeTypes.EXTRACTOR_RECIPES, t, "service_piece_dismantling", 15200)
                .inputItems(material(t, "stage_3", 16)).outputItems(material(t, "stage_4", 16)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, t, "fresh_feed_repair_cure", 16800)
                .inputItems(material(t, "stage_4", 16), material(t - 1, "billet", 8))
                .inputFluids(fluid("gtceu:argon", 64000))
                .outputItems(material(t, "stage_5", 16), material(t, "unrecoverable_tailings", 64)).save(out);
        // 修复态只通向终检，不返回stage_2或stage_3，因此不是无限维修或无损服役循环。
        quality(t, "stage_5", 16, 14, out);
    }
}
