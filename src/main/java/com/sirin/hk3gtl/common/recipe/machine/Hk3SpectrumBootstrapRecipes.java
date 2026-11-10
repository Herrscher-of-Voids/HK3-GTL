package com.sirin.hk3gtl.common.recipe.machine;

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;
import com.sirin.hk3gtl.common.item.Hk3Items;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.machine.Hk3MachinesImpl;
import com.sirin.hk3gtl.common.machine.Hk3MachinesAbyssStage;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImpl;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import java.util.function.Consumer;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文说明：该处说明已按当前代码行为整理。*/
public final class Hk3SpectrumBootstrapRecipes {
    /** 【变更记录 #1】2026-09-29 19:19:27（内测5修订96）：新增MAX阶段复杂材料的超时空装配线手机配方；不借用免费命令入口。 */
    private Hk3SpectrumBootstrapRecipes() {}

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    public static ItemStack item(String id) { return new ItemStack(Hk3IndustrialContent.items().get(id).get()); }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    public static void register(Consumer<FinishedRecipe> provider) {
        long max = Hk3Values.VA_LONG[GTValues.MAX];
        org.gtlcore.gtlcore.common.data.GTLRecipeTypes.SUPRACHRONAL_ASSEMBLY_LINE_RECIPES
                .recipeBuilder(new ResourceLocation("hk3gtl", "personal_phone"))
                .inputItems(CustomTags.MAX_CIRCUITS, 8)
                .inputItems(org.gtlcore.gtlcore.common.data.GTLItems.SENSOR_MAX.asStack(4))
                .inputItems(org.gtlcore.gtlcore.common.data.GTLItems.EMITTER_MAX.asStack(4))
                .inputItems(org.gtlcore.gtlcore.common.data.GTLItems.FIELD_GENERATOR_MAX.asStack(2))
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 32)
                .inputItems(TagPrefix.wireFine, GTMaterials.NiobiumTitanium, 32)
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(2304))
                .outputItems(Hk3Items.PERSONAL_PHONE.get())
                .duration(2400).EUt(max).save(provider);
        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        org.gtlcore.gtlcore.common.data.GTLRecipeTypes.SUPRACHRONAL_ASSEMBLY_LINE_RECIPES
                .recipeBuilder(new ResourceLocation("hk3gtl", "industrial_prototype_honkai_detector"))
                .inputItems(CustomTags.MAX_CIRCUITS, 4)
                .inputItems(org.gtlcore.gtlcore.common.data.GTLItems.SENSOR_MAX.asStack(2))
                .inputItems(org.gtlcore.gtlcore.common.data.GTLItems.EMITTER_MAX.asStack(2))
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 32)
                .inputItems(TagPrefix.frameGt, GTMaterials.TungstenSteel, 4)
                .inputItems(TagPrefix.wireGtSingle, GTMaterials.Platinum, 24)
                .inputItems(TagPrefix.wireFine, GTMaterials.NiobiumTitanium, 32)
                .inputItems(TagPrefix.gem, GTMaterials.Diamond, 8)
                .inputItems(Items.GLASS_PANE, 16)
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(1152))
                .outputItems(item("prototype_honkai_detector"))
                .duration(1200).EUt(max).save(provider);
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new ResourceLocation("hk3gtl", "i01_collection_controller"))
                .inputItems(CustomTags.MAX_CIRCUITS, 4)
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 16)
                .inputItems(TagPrefix.wireGtSingle, GTMaterials.Platinum, 8)
                .inputItems(TagPrefix.gem, GTMaterials.Diamond, 4)
                .outputItems(Hk3MachinesImpl.I01_HONKAI_COLLECTION_TOWER.asStack())
                .duration(1200).EUt(max).save(provider);
        collectionUpgrade(provider, "i01_collection_controller_2",
                Hk3MachinesImpl.I01_HONKAI_COLLECTION_TOWER,
                Hk3MachinesImpl.I01_2_HONKAI_COLLECTION_TOWER, max);
        collectionUpgrade(provider, "i01_collection_controller_3",
                Hk3MachinesImpl.I01_2_HONKAI_COLLECTION_TOWER,
                Hk3MachinesImpl.I01_3_HONKAI_COLLECTION_TOWER, max);
        collectionUpgrade(provider, "i01_collection_controller_4",
                Hk3MachinesImpl.I01_3_HONKAI_COLLECTION_TOWER,
                Hk3MachinesImpl.I01_4_HONKAI_COLLECTION_TOWER, max);
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new ResourceLocation("hk3gtl", "i02_spectrum_controller"))
                .inputItems(CustomTags.MAX_CIRCUITS, 4)
                .inputItems(TagPrefix.plate, GTMaterials.StainlessSteel, 16)
                .inputItems(TagPrefix.wireGtSingle, GTMaterials.Platinum, 8)
                .inputItems(TagPrefix.gem, GTMaterials.Diamond, 8)
                .outputItems(Hk3MachinesAbyssStage.I02_SPECTRUM_ANALYSIS_ARRAY.asStack())
                .duration(1200).EUt(max).save(provider);
        GTRecipeTypes.CANNER_RECIPES.recipeBuilder(new ResourceLocation("hk3gtl", "industrial_honkai_sample_canning"))
                .inputItems(Items.GLASS_BOTTLE)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(100))
                .outputItems(item("honkai_analysis_sample"))
                .duration(100).EUt(30).save(provider);
        Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS
                .recipeBuilder(new ResourceLocation("hk3gtl", "industrial_initial_spectrum"))
                .circuitMeta(1).inputItems(item("honkai_analysis_sample"))
                .inputItems(Items.PAPER)
                .outputItems(item("analyzed_honkai_sample"))
                .duration(200).EUt(max).save(provider);
    }

    private static void collectionUpgrade(Consumer<FinishedRecipe> provider, String id,
            com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition previous,
            com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition next, long voltage) {
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new ResourceLocation("hk3gtl", id))
                .inputItems(previous.asStack())
                .inputItems(CustomTags.MAX_CIRCUITS, 4)
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 16)
                .inputItems(TagPrefix.wireGtSingle, GTMaterials.Platinum, 8)
                .outputItems(next.asStack())
                .duration(1200).EUt(voltage).save(provider);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
