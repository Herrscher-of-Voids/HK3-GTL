package com.sirin.hk3gtl.common.recipe.main;

import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import net.minecraft.data.recipes.FinishedRecipe;
import org.gtlcore.gtlcore.common.data.GTLRecipeTypes;

import java.util.function.Consumer;

import static com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialRecipes.*;

/**
 * 【文件职责】同级制造边角料及拒收批的有损回收，不按名称混收，也不让小件返还整坯。
 * 【变更记录 #1】2026-10-17 16:28:36（第1次备注 · 修订165）
 * - 删除：无；不添加废料首通、无损拆机、跨级废物升阶或不可逆尾料回主材路径。
 * - 新增：各功能形态分批拆解、拒收分类、75%相回收、新鲜Shirabon补料再制及尾料灰化。
 * - 修改：一坯相含量144，回收细分18；八坯分类料必得48份回收和16份尾料，闭环最多回到六坯。
 * - 用途：复用现有提取机、大化工和SPS；尾料只能生成惰性灰，不参与任何本级主材返制。
 */
/**
 * 【变更记录 #2】2026-10-17 17:45:14（第2次备注 · 修订165）
 * - 删除：以提取机机械拆零件的128条入口；目标2.8会按零件输入统一移除此类配方。
 * - 新增：每批消耗1000mB盐酸与1000mB蒸馏水的大化工湿法解聚，回收身份仍为本阶分类料。
 * - 修改：只改拆解载体及加入化学介质；物料相含量、同阶研究、加工功率与75%回收上限不变。
 * - 用途：在实际整包保留合法回收工艺，不改第三方移除脚本，也不恢复其禁止的熔融拆件旁路。
 */
final class Hk3MainMaterialRecoveryRecipes {
    private Hk3MainMaterialRecoveryRecipes() {}

    static void register(int tier, Consumer<FinishedRecipe> out) {
        for (String form : new String[]{"billet", "plate", "rod", "fine_wire", "ring", "foil", "frame", "rejected_batch"}) {
            int units = Hk3MainMaterialUnits.perItem(form);
            int inputs = units < 144 ? 144 / units : 1;
            int outputs = units > 144 ? units / 144 : 1;
            Hk3MainMaterialUnits.requireConversion(form, inputs, "classified_scrap", outputs);
            process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, tier, "dismantle_" + form, 800)
                    .inputItems(material(tier, form, inputs))
                    .inputFluids(fluid("gtceu:hydrochloric_acid", 1000), fluid("gtceu:distilled_water", 1000))
                    .outputItems(material(tier, "classified_scrap", outputs)).save(out);
        }

        Hk3MainMaterialUnits.requireBalanced(Hk3MainMaterialUnits.amount("classified_scrap", 8),
                Hk3MainMaterialUnits.amount("recovered_fraction", 48) + Hk3MainMaterialUnits.amount("unrecoverable_tailings", 16));
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, tier, "lossy_phase_separation", 2400)
                .inputItems(material(tier, "classified_scrap", 8)).inputFluids(fluid("gtceu:argon", 8000))
                .outputItems(material(tier, "recovered_fraction", 48), material(tier, "unrecoverable_tailings", 16)).save(out);

        Hk3MainMaterialUnits.requireConversion("recovered_fraction", 8, "billet", 1);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, tier, "fresh_feed_reconstitution", 3200)
                .inputItems(material(tier, "recovered_fraction", 8), external("gtceu:shirabon_foil", 4))
                .inputFluids(fluid("gtceu:argon", 8000)).outputItems(material(tier, "billet", 1)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, tier, "irreversible_tailings_inerting", 1200)
                .inputItems(material(tier, "unrecoverable_tailings", 16))
                .inputFluids(fluid("gtceu:distilled_water", 1000))
                .outputItems(TagPrefix.dust, GTMaterials.Ash, 2).save(out);
    }
}
