package com.sirin.hk3gtl.common.machine.hyperion;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;

public final class Hk3HyperionMachines {
    public static MultiblockMachineDefinition FLAGSHIP;
    private Hk3HyperionMachines() {}
    public static void init() {
        FLAGSHIP = Hk3Gtl.REGISTRATE.multiblock("hyperion_flagship", Hk3HyperionMachine::new)
                .tier(com.sirin.hk3gtl.common.constants.Hk3Tiers.WSV).rotationState(RotationState.NON_Y_AXIS)
                .allowFlip(false).allowExtendedFacing(false)
            .recipeType(com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("H01")).noRecipeModifier()
                .appearanceBlock(() -> Blocks.WHITE_CONCRETE)
                .pattern(Hk3HyperionConstructionPattern::new)
                .multiblockPreviewRenderer(false, true)
                .workableCasingRenderer(new ResourceLocation("hk3gtl", "block/casings/industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/hyperion_flagship_appearance_0002_r15"))
                .tooltips(Component.translatable("hk3gtl.hyperion.tooltip"),
                        Component.translatable("hk3gtl.machine.controller.research_required"),
                        Component.translatable("hk3gtl.hyperion.size"),
                        Component.translatable("hk3gtl.hyperion.creative"),
                        Component.translatable("hk3gtl.hyperion.tooltip.output"))
                .register();
    }
}
