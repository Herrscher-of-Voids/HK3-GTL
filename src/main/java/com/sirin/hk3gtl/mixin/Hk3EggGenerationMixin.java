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
/** 【变更记录 #1】2026-10-01 06:45:17（修订128）：删除：无；新增/修改：新增配方输出实际EU计量及只读阅读关闭回执，模拟与网络搬运均不计发电；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #2】2026-10-01 06:47:03（修订128）：删除：无；新增/修改：按实际字节码修正GTRecipe参数为IRecipeCapabilityHolder，来源仍限定RecipeLogic自身机器；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggGenerationMixin {
    @Redirect(method="handleTickRecipeIO",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;handleTickRecipeIO(Lcom/gregtechceu/gtceu/api/capability/recipe/IO;Lcom/gregtechceu/gtceu/api/capability/recipe/IRecipeCapabilityHolder;Ljava/util/Map;)Z"))
    private boolean hk3gtl$capture(GTRecipe recipe,IO io,IRecipeCapabilityHolder machine,Map<RecipeCapability<?>,Object2IntMap<?>> cache){return com.sirin.hk3gtl.common.easter.Hk3EggGeneration.tick(recipe,io,(IRecipeLogicMachine)machine,cache);}
}
