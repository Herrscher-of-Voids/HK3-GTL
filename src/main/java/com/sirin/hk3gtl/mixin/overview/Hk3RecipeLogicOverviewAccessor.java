package com.sirin.hk3gtl.mixin.overview;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;






@Mixin(value = RecipeLogic.class, remap = false)
public interface Hk3RecipeLogicOverviewAccessor {
    @Accessor("waitingReason") Component hk3gtl$waitingReason();
}
