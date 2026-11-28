package com.sirin.hk3gtl.mixin.enhanced.iv;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.gen.Accessor;
import org.spongepowered.asm.mixin.gen.Invoker;

@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.common.recipe.iv.IvJob", remap = false)
public interface Hk3IvJobAccess {
    @Accessor("recipe") GTRecipe hk3gtl$recipe();
    @Accessor("parallel") long hk3gtl$parallel();
    @Invoker("validateAccounting") void hk3gtl$validateAccounting();
}
