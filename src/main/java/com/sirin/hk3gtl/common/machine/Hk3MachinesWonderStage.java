package com.sirin.hk3gtl.common.machine;



import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3P1Patterns;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesWonder;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;

/**
 * 奇观阶段（v0.3）12 台机器。
 */
public class Hk3MachinesWonderStage {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    public static MultiblockMachineDefinition HONKAI_ULTIMATE_FUSION_CORE;
    public static MultiblockMachineDefinition DIVINE_KEY_GRAND_CATHEDRAL;
    public static MultiblockMachineDefinition CIVILIZATION_JUDGMENT_CORRIDOR;
    public static MultiblockMachineDefinition CIVILIZATION_MEMORY_ETERNAL_MONUMENT;
    public static MultiblockMachineDefinition MYRIAD_REALMS_COMMUNICATION_NEXUS;
    public static MultiblockMachineDefinition DESTINY_LOOM;
    public static MultiblockMachineDefinition CIVILIZATION_EYE_OBSERVATION_ARRAY;
    public static MultiblockMachineDefinition CYCLE_NARRATOR_PLATFORM;
    public static MultiblockMachineDefinition CIVILIZATION_STARSHIP_MUSEUM;
    public static MultiblockMachineDefinition PROOF_OF_EXISTENCE_MEMORIAL;
    public static MultiblockMachineDefinition ULTIMATE_MEDITATION_SANCTUM;
    public static MultiblockMachineDefinition GRAND_CONVERGENCE_ALTAR;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {
        HONKAI_ULTIMATE_FUSION_CORE = reg()
                .multiblock("honkai_ultimate_fusion_core", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesWonder.HONKAI_ULTIMATE_FUSION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_DOMINION)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_DOMINION))
                .workableCasingRenderer(tex("casing_finality_dominion"), OVERLAY)
                .register();

        DIVINE_KEY_GRAND_CATHEDRAL = reg()
                .multiblock("divine_key_grand_cathedral", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesWonder.DIVINE_KEY_GRAND_CATHEDRAL)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_WONDER)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_WONDER))
                .workableCasingRenderer(tex("casing_finality_wonder"), OVERLAY)
                .register();

        CIVILIZATION_JUDGMENT_CORRIDOR = reg()
                .multiblock("civilization_judgment_corridor", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesWonder.CIVILIZATION_JUDGMENT)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_SANCTUM)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_SANCTUM))
                .workableCasingRenderer(tex("casing_finality_sanctum"), OVERLAY)
                .register();

        CIVILIZATION_MEMORY_ETERNAL_MONUMENT = reg()
                .multiblock("civilization_memory_eternal_monument", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypesWonder.CIVILIZATION_MEMORY_ETERNAL)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_SANCTUM)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_SANCTUM))
                .workableCasingRenderer(tex("casing_finality_sanctum"), OVERLAY)
                .register();

        MYRIAD_REALMS_COMMUNICATION_NEXUS = reg()
                .multiblock("myriad_realms_communication_nexus", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypesWonder.MYRIAD_REALMS_COMMUNICATION)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_ENTANGLE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_ENTANGLE))
                .workableCasingRenderer(tex("casing_quantum_entangle"), OVERLAY)
                .register();

        DESTINY_LOOM = reg()
                .multiblock("destiny_loom", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesWonder.DESTINY_WEAVING)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_TREE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_TREE))
                .workableCasingRenderer(tex("casing_imaginary_tree"), OVERLAY)
                .register();

        CIVILIZATION_EYE_OBSERVATION_ARRAY = reg()
                .multiblock("civilization_eye_observation_array", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesWonder.CIVILIZATION_EYE_OBSERVATION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_SANCTUM)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_SANCTUM))
                .workableCasingRenderer(tex("casing_finality_sanctum"), OVERLAY)
                .register();

        CYCLE_NARRATOR_PLATFORM = reg()
                .multiblock("cycle_narrator_platform", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypesWonder.CYCLE_NARRATION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_SANCTUM)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_SANCTUM))
                .workableCasingRenderer(tex("casing_finality_sanctum"), OVERLAY)
                .register();

        CIVILIZATION_STARSHIP_MUSEUM = reg()
                .multiblock("civilization_starship_museum", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesWonder.CIVILIZATION_STARSHIP_EXHIBITION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_HYPERION)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_HYPERION))
                .workableCasingRenderer(tex("casing_finality_hyperion"), OVERLAY)
                .register();

        PROOF_OF_EXISTENCE_MEMORIAL = reg()
                .multiblock("proof_of_existence_memorial", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypesWonder.PROOF_OF_EXISTENCE)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_WONDER)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_WONDER))
                .workableCasingRenderer(tex("casing_finality_wonder"), OVERLAY)
                .register();

        ULTIMATE_MEDITATION_SANCTUM = reg()
                .multiblock("ultimate_meditation_sanctum", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesWonder.ULTIMATE_MEDITATION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_SANCTUM)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_SANCTUM))
                .workableCasingRenderer(tex("casing_finality_sanctum"), OVERLAY)
                .register();

        GRAND_CONVERGENCE_ALTAR = reg()
                .multiblock("grand_convergence_altar", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesWonder.GRAND_CONVERGENCE)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_WONDER)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_WONDER))
                .workableCasingRenderer(tex("casing_finality_wonder"), OVERLAY)
                .register();

        LOGGER.info("[HK3GTL] 奇观阶段多方块初始化完成（12台）。");
    }
}
