package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallPattern;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;

public final class Hk3W01Machines {
    public static MultiblockMachineDefinition HALL;
    private Hk3W01Machines() {}
    public static void init() {
        HALL = Hk3Gtl.REGISTRATE.multiblock("w01_origin_stellar_concert_court", Hk3W01HallMachine::new)
                .tier(Hk3Tiers.WSV).rotationState(RotationState.NON_Y_AXIS)
                .allowFlip(false).allowExtendedFacing(false)
            .recipeType(com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("W01")).noRecipeModifier()
                .appearanceBlock(() -> Blocks.SMOOTH_QUARTZ)
                .pattern(Hk3W01HallPattern::new)
                .multiblockPreviewRenderer(false, true)
                .workableCasingRenderer(new ResourceLocation("hk3gtl", "block/casings/industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/w01_appearance_0002_r7"))
                .tooltips(Component.translatable("hk3gtl.machine.w01_origin_stellar_concert_court.tooltip.0"),
                        Component.translatable("hk3gtl.machine.w01_origin_stellar_concert_court.tooltip.1"),
                        Component.translatable("hk3gtl.machine.controller.research_required"),
                        Component.translatable("hk3gtl.machine.controller.voltage", "WSV"),
                        Component.translatable("hk3gtl.w01.sparse"))
                .register();
    }
}
