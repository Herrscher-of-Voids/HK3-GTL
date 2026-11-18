package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets = {
        "org.gtlcore.gtlcore.common.machine.trait.MolecularAssemblerRecipesLogic",
        "com.gtladd.gtladditions.api.machine.ConversationMachine$ConversationRecipeLogic",
        "com.gtladd.gtladditions.common.machine.multiblock.controller.ConversationMachine$Companion$ConversationRecipeLogic",
        "com.gtladd.gtladditions.api.machine.logic.MultiRecipeTypesLogic",
        "com.gtladd.gtladditions.common.machine.multiblock.controller.OreProcessorMachine$OreProcessorRecipeLogic",
        "com.gtladd.gtladditions.common.machine.multiblock.controller.PlanetaryIonisationConvergenceTower$PICTRecipeLogic",
        "com.gtladd.gtladditions.common.machine.multiblock.controller.PlanetaryIonisationConvergenceTower$Companion$PICTRecipeLogic",
        "com.gtladd.gtladditions.common.machine.multiblock.controller.TimeSpaceDistorter$TimeSpaceDistorterRecipeLogic",
        "com.gtladd.gtladditions.common.machine.multiblock.controller.df.FractalManipulator$FMRecipeLogic",
        "com.gtladd.gtladditions.common.machine.multiblock.controller.df.HyperdimensionalEnergyConcentrator$HECRecipeLogic",
        "com.gtladd.gtladditions.common.machine.multiblock.controller.df.RecursiveReverseForge$RRFRecipeLogic",
        "com.gtladd.gtladditions.common.machine.multiblock.controller.fl.FloatingLightController$FLRecipeLogic",
        "com.gtlsupb.gtlsupb.common.machine.multiblock.GTLSupbMolecularAssemblerLogic"
}, remap = false)
public abstract class Hk3IndustrialWorkingGazeMixin {
    @Inject(method = "handleRecipeWorking", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$industrialWorking(CallbackInfo callback) {
        if (Hk3RecipeEnvironment.throttlesByGaze(((RecipeLogic) (Object) this).getMachine()))
            callback.cancel();
    }
}
