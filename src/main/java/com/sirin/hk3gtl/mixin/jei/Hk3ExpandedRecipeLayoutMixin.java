package com.sirin.hk3gtl.mixin.jei;

import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.api.recipe.ui.GTRecipeTypeUI;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = GTRecipeTypeUI.class, remap = false)
abstract class Hk3ExpandedRecipeLayoutMixin {
    @Shadow @Final private GTRecipeType recipeType;

    @ModifyExpressionValue(method = "lambda$createEditableUITemplate$0", at = @At(value = "INVOKE", target =
            "Lcom/gregtechceu/gtceu/api/recipe/ui/GTRecipeTypeUI;hasCustomUI()Z"))
    private boolean hk3gtl$useFullSlotLayout(boolean custom) {
        if (!custom || !recipeType.registryName.getNamespace().equals("gtceu")) return custom;
        return switch (recipeType.registryName.getPath()) {
            case "precision_assembler", "suprachronal_assembly_line" -> false;
            default -> true;
        };
    }
}
