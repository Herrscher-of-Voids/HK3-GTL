package com.sirin.hk3gtl.common.machine.w02;

import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;

public final class Hk3W02Machines {
    public static MultiblockMachineDefinition MATRIX;
    private Hk3W02Machines(){}
    public static void init(){
        MATRIX=Hk3Gtl.REGISTRATE.multiblock("omnia_autonomous_industrial_matrix",Hk3W02Machine::new)
            .tier(Hk3Tiers.WSV).rotationState(RotationState.NON_Y_AXIS).allowFlip(false).allowExtendedFacing(false)
            .recipeType(com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("W02")).noRecipeModifier()
            .appearanceBlock(()->Blocks.LIGHT_BLUE_CONCRETE).pattern(Hk3W02Pattern::new).multiblockPreviewRenderer(false,true)
            .workableCasingRenderer(new ResourceLocation("hk3gtl","block/casings/industrial_controller_shell"),new ResourceLocation("hk3gtl","block/overlay/w02_appearance_0002_r7"))
            .tooltips(Component.translatable("hk3gtl.machine.omnia_autonomous_industrial_matrix.tooltip.0"),
                Component.translatable("hk3gtl.machine.omnia_autonomous_industrial_matrix.tooltip.1"),
                Component.translatable("hk3gtl.machine.controller.research_required"),
                Component.translatable("hk3gtl.machine.controller.voltage", "WSV"),
                Component.translatable("hk3gtl.machine.omnia_autonomous_industrial_matrix.tooltip.structure")).register();
    }
}
