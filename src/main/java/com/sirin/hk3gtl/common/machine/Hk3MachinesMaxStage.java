package com.sirin.hk3gtl.common.machine;

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;


import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import com.gregtechceu.gtceu.api.GTValues;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;















public class Hk3MachinesMaxStage {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/network_injector_appearance_0002_r7");

    public static MultiblockMachineDefinition HONKAI_NETWORK_INJECTOR;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {






        HONKAI_NETWORK_INJECTOR = reg()
                .multiblock("honkai_network_injector", com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiNetworkInjectorMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3IndustrialRecipeTypes.NETWORK_INJECTION)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLinePatterns.create(def,
                        com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLineLayout.Kind.INJECTION))
                .shapeInfo(def -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLinePatterns.shape(def,
                        com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLineLayout.Kind.INJECTION))
                .workableCasingRenderer(tex("industrial_controller_shell"), OVERLAY)
                .tooltips(
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.honkai_network_injector.tooltip.0"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.honkai_network_injector.tooltip.1"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.honkai_network_injector.tooltip.2"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();



        LOGGER.info("[HK3GTL] machine registration completed");
    }
}


