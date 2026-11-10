package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchMachines;
import net.minecraft.data.recipes.FinishedRecipe;
import java.util.function.Consumer;

/** 中文说明：该处说明已按当前代码行为整理。*/
public final class Hk3ResearchComputerRecipes {
    private Hk3ResearchComputerRecipes() {}

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static void register(Consumer<FinishedRecipe> provider) {
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_research_point_computer")
                .inputItems(CustomTags.MAX_CIRCUITS, 4)
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 16)
                .inputItems(TagPrefix.wireGtSingle, GTMaterials.Platinum, 8)
                .inputItems(TagPrefix.gem, GTMaterials.Diamond, 8)
                .outputItems(Hk3ResearchMachines.RESEARCH_COMPUTER.asStack())
                .duration(1200).EUt(Hk3Values.VA_LONG[GTValues.MAX]).save(provider);
    }
}
