package com.sirin.hk3gtl.mixin.gtlultimate;

import com.mojang.logging.LogUtils;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

@Pseudo
@Mixin(targets = "org.gtlultimate.gtlultimate.common.data.GTLUltimateRecipeTypes", remap = false)
abstract class Hk3ConflictingRecipeTypesMixin {
    @ModifyArg(method = "<clinit>", at = @At(value = "INVOKE", target =
            "Lcom/gregtechceu/gtceu/common/data/GTRecipeTypes;register(Ljava/lang/String;Ljava/lang/String;[Lnet/minecraft/world/item/crafting/RecipeType;)Lcom/gregtechceu/gtceu/api/recipe/GTRecipeType;"), index = 0, require = 1)
    private static String hk3gtl$separateRecipeType(String id) {
        if (!id.equals("holographic_data_storage") && !id.equals("floating_point_computation")) return id;
        String separated = "gtlultimate_" + id;
        LogUtils.getLogger().info("HK3GTL: GTL Ultimate recipe type gtceu:{} moved to gtceu:{} for GTL-Supb compatibility", id, separated);
        return separated;
    }
}
