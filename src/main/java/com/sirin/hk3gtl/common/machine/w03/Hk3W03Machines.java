package com.sirin.hk3gtl.common.machine.w03;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.network.chat.Component;

public final class Hk3W03Machines {
    public static MultiblockMachineDefinition VOID_ANCHOR;
    private Hk3W03Machines(){}
    public static void init(){
        VOID_ANCHOR=Hk3Gtl.REGISTRATE.multiblock("void_anchor_ring",Hk3W03Machine::new)
            .tier(com.sirin.hk3gtl.common.constants.Hk3Tiers.WSV).rotationState(RotationState.NON_Y_AXIS).allowFlip(false).allowExtendedFacing(false)
            .recipeType(com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("W03")).noRecipeModifier()
            .appearanceBlock(()->Blocks.QUARTZ_BLOCK).pattern(Hk3W03Pattern::new).multiblockPreviewRenderer(false,true)
            .workableCasingRenderer(new ResourceLocation("hk3gtl","block/casings/industrial_controller_shell"),new ResourceLocation("hk3gtl","block/overlay/w03_appearance_0002_r7"))
            .tooltips(Component.translatable("hk3gtl.machine.void_anchor_ring.tooltip.0"),
                Component.translatable("hk3gtl.machine.void_anchor_ring.tooltip.1"),
                Component.translatable("hk3gtl.machine.controller.research_required"),
                Component.translatable("hk3gtl.machine.controller.voltage", "WSV"),
                Component.translatable("hk3gtl.w03.size")).register();
    }
}
