package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.capability.recipe.*;
import it.unimi.dsi.fastutil.objects.Object2IntMap;
import java.util.Map;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(value=RecipeLogic.class,remap=false)
 
 
public abstract class Hk3EggGenerationMixin {
    @Redirect(method="handleTickRecipeIO",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;handleTickRecipeIO(Lcom/gregtechceu/gtceu/api/capability/recipe/IO;Lcom/gregtechceu/gtceu/api/capability/recipe/IRecipeCapabilityHolder;Ljava/util/Map;)Z"))
    private boolean hk3gtl$capture(GTRecipe recipe,IO io,IRecipeCapabilityHolder machine,Map<RecipeCapability<?>,Object2IntMap<?>> cache){return com.sirin.hk3gtl.common.easter.Hk3EggGeneration.tick(recipe,io,(IRecipeLogicMachine)machine,cache);}
}
