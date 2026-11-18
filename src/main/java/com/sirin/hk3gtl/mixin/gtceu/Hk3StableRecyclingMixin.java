package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.chemical.material.Material;
import com.gregtechceu.gtceu.api.data.chemical.material.stack.MaterialStack;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.data.recipe.misc.RecyclingRecipes;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.Redirect;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

@Mixin(value = RecyclingRecipes.class, remap = false)
public abstract class Hk3StableRecyclingMixin {
    @ModifyArg(method = "finalizeOutputs", at = @At(value = "INVOKE",
            target = "Ljava/util/stream/Stream;sorted(Ljava/util/Comparator;)Ljava/util/stream/Stream;"),
            index = 0, require = 2)
    private static Comparator<Map.Entry<MaterialStack, ItemStack>> hk3gtl$stableMaterialOrder(
            Comparator<Map.Entry<MaterialStack, ItemStack>> original) {
        return original.thenComparing(entry -> entry.getKey().material().getResourceLocation().toString());
    }

    @Redirect(method = {"registerMaceratorRecycling", "registerExtractorRecycling", "registerArcRecycling"},
            at = @At(value = "INVOKE", target = "Lcom/gregtechceu/gtceu/api/data/chemical/ChemicalHelper;getTag(Lcom/gregtechceu/gtceu/api/data/tag/TagPrefix;Lcom/gregtechceu/gtceu/api/data/chemical/material/Material;)Lnet/minecraft/tags/TagKey;"),
            require = 3)
    private static TagKey<Item> hk3gtl$materialSpecificInput(TagPrefix prefix, Material material) {
        return prefix == TagPrefix.lens ? null : ChemicalHelper.getTag(prefix, material);
    }

    @Redirect(method = "registerExtractorRecycling", at = @At(value = "INVOKE",
            target = "Lcom/gregtechceu/gtceu/api/data/chemical/ChemicalHelper;getMaterial(Lnet/minecraft/world/item/ItemStack;)Lcom/gregtechceu/gtceu/api/data/chemical/material/stack/MaterialStack;"),
            require = 1)
    private static MaterialStack hk3gtl$materialSpecificLens(ItemStack stack, Consumer<FinishedRecipe> provider,
            ItemStack input, List<MaterialStack> materials, int multiplier, TagPrefix prefix) {
        return prefix == TagPrefix.lens ? materials.get(0) : ChemicalHelper.getMaterial(stack);
    }
}
