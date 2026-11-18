package com.sirin.hk3gtl.common.machine;

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;


import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3I02SpectrumPattern;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;






















public class Hk3MachinesAbyssStage {



    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    /** I02 样本光谱分析阵列。 */
    public static MultiblockMachineDefinition I02_SPECTRUM_ANALYSIS_ARRAY;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {








        I02_SPECTRUM_ANALYSIS_ARRAY = reg()
                .multiblock("i02_spectrum_analysis_array", com.sirin.hk3gtl.common.machine.research.Hk3SpectrumAnalysisMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3IndustrialApprovedPatterns.create(def, "i02"))
                // 2026-09-25：光谱棱镜面板使用独立状态贴图；机器功能、接口和配方关联保持不变。
                .workableCasingRenderer(tex("industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/i02_appearance_0002_r7"))
                .tooltips(
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.i02_spectrum_analysis_array.tooltip.0"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.i02_spectrum_analysis_array.tooltip.1"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.i02_spectrum_analysis_array.tooltip.2"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();

        LOGGER.info("[HK3GTL] machine registration completed");
    }
}


