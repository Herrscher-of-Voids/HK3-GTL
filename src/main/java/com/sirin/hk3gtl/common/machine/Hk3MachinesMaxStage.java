package com.sirin.hk3gtl.common.machine;



import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3P1Patterns;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;

/**
 * Max 起始阶段（v0.3）仅保留 4 台核心机器。
 */
public class Hk3MachinesMaxStage {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    public static MultiblockMachineDefinition VOID_ARCHIVES_ANALYSIS_CHAMBER;
    public static MultiblockMachineDefinition REASON_RECONSTRUCTION_ARRAY;
    public static MultiblockMachineDefinition HONKAI_EU_CONVERTER;
    public static MultiblockMachineDefinition HONKAI_NETWORK_INJECTOR;
    public static MultiblockMachineDefinition ABYSS_CIRCUIT_FOUNDRY;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {
        VOID_ARCHIVES_ANALYSIS_CHAMBER = reg()
                .multiblock("void_archives_analysis_chamber", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.VOID_ARCHIVES_ANALYSIS_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_RESEARCH)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_ABYSS_RESEARCH))
                .workableCasingRenderer(tex("casing_abyss_research"), OVERLAY)
                .register();

        REASON_RECONSTRUCTION_ARRAY = reg()
                .multiblock("reason_reconstruction_array", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.REASON_RECONSTRUCTION_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_RESEARCH)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_ABYSS_RESEARCH))
                .workableCasingRenderer(tex("casing_abyss_research"), OVERLAY)
                .register();

        HONKAI_EU_CONVERTER = reg()
                .multiblock("honkai_eu_converter", com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiEuConverterMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.HONKAI_EU_CONVERSION_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_ENERGY)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_ABYSS_ENERGY))
                .workableCasingRenderer(tex("casing_abyss_energy"), OVERLAY)
                .register();

        // 双能源引擎（D-01）的充网入口：液态崩坏能/结晶/EU → 玩家无线崩坏能网络
        HONKAI_NETWORK_INJECTOR = reg()
                .multiblock("honkai_network_injector", com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiNetworkInjectorMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.HONKAI_NETWORK_INJECTION_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_ENERGY)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_ABYSS_ENERGY))
                .workableCasingRenderer(tex("casing_abyss_energy"), OVERLAY)
                .tooltips(
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.honkai_network_injector.tooltip.0"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.honkai_network_injector.tooltip.1"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.honkai_network_injector.tooltip.2"))
                .register();

        ABYSS_CIRCUIT_FOUNDRY = reg()
                .multiblock("abyss_circuit_foundry", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.ABYSS_CIRCUIT_FOUNDRY_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_MECHANICAL)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_ABYSS_MECHANICAL))
                .workableCasingRenderer(tex("casing_abyss_mechanical"), OVERLAY)
                .register();

        LOGGER.info("[HK3GTL] Max阶段多方块初始化完成（5台）。");
    }
}
