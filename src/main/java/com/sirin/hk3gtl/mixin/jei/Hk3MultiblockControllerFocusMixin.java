package com.sirin.hk3gtl.mixin.jei;

import com.gregtechceu.gtceu.integration.jei.multipage.MultiblockInfoWrapper;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.library.util.IngredientSupplierHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

@Mixin(value = IngredientSupplierHelper.class, remap = false)
abstract class Hk3MultiblockControllerFocusMixin {
    // JEI 建索引时蓝图尚未展开，直接用本页主控关联查配方和查用途。
    @ModifyArg(method = "getIngredientSupplier", index = 0, at = @At(value = "INVOKE", target =
            "Lmezz/jei/api/recipe/category/IRecipeCategory;setRecipe(Lmezz/jei/api/gui/builder/IRecipeLayoutBuilder;Ljava/lang/Object;Lmezz/jei/api/recipe/IFocusGroup;)V"))
    private static IRecipeLayoutBuilder hk3gtl$indexController(IRecipeLayoutBuilder builder, Object recipe, IFocusGroup focuses) {
        if (recipe instanceof MultiblockInfoWrapper page && "hk3gtl".equals(page.definition.getId().getNamespace())) {
            var controller = page.definition.asStack();
            builder.addInvisibleIngredients(RecipeIngredientRole.INPUT).addItemStack(controller);
            builder.addInvisibleIngredients(RecipeIngredientRole.OUTPUT).addItemStack(controller);
        }
        return builder;
    }
}
