package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableItemStackHandler;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.lowdragmc.lowdraglib.misc.ItemStackTransfer;
import com.sirin.hk3gtl.common.capability.Hk3MaterialTick;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;
import java.util.List;

@Mixin(value = NotifiableItemStackHandler.class, remap = false)
public abstract class Hk3ItemTickUndoMixin {
    @Redirect(method = "handleIngredient", at = @At(value = "INVOKE", target =
            "Lcom/lowdragmc/lowdraglib/misc/ItemStackTransfer;extractItem(IIZ)Lnet/minecraft/world/item/ItemStack;"), require = 1)
    private static ItemStack hk3gtl$extract(ItemStackTransfer storage, int slot, int amount, boolean simulate,
            IO io, GTRecipe recipe, List<Ingredient> left, boolean simulation, IO handlerIO, ItemStackTransfer original) {
        return Hk3MaterialTick.item(recipe, storage, slot, simulate || simulation,
                () -> storage.extractItem(slot, amount, simulate));
    }

    @Redirect(method = "handleIngredient", at = @At(value = "INVOKE", target =
            "Lcom/lowdragmc/lowdraglib/misc/ItemStackTransfer;insertItem(ILnet/minecraft/world/item/ItemStack;Z)Lnet/minecraft/world/item/ItemStack;"), require = 1)
    private static ItemStack hk3gtl$insert(ItemStackTransfer storage, int slot, ItemStack stack, boolean simulate,
            IO io, GTRecipe recipe, List<Ingredient> left, boolean simulation, IO handlerIO, ItemStackTransfer original) {
        return Hk3MaterialTick.item(recipe, storage, slot, simulate || simulation,
                () -> storage.insertItem(slot, stack, simulate));
    }
}
