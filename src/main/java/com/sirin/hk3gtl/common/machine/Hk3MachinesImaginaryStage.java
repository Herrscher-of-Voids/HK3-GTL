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
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesFinality;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImaginary;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;

/**
 * 虚数阶段（v0.3）12 台机器。
 */
public class Hk3MachinesImaginaryStage {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    public static MultiblockMachineDefinition IMAGINARY_DIMENSION_GATEWAY;
    public static MultiblockMachineDefinition IMAGINARY_TREE_OBSERVATION_ARRAY;
    public static MultiblockMachineDefinition IMAGINARY_ANCHOR_DEVICE;
    public static MultiblockMachineDefinition SEA_OF_QUANTA_OBSERVATORY;
    public static MultiblockMachineDefinition IMAGINARY_CIRCUIT_COMPUTATION_SANCTUM;
    public static MultiblockMachineDefinition SOULIUM_SUPERSTRUCTURE_FORGE;
    public static MultiblockMachineDefinition CIVILIZATION_EXCHANGE_COUNCIL_HUB;
    public static MultiblockMachineDefinition PRECIVILIZATION_DATABASE_DECODER;
    public static MultiblockMachineDefinition HONKAI_PHASE_PURIFICATION_PLANT;
    public static MultiblockMachineDefinition DUAL_ENERGY_STABLE_SUPPLY_STATION;
    public static MultiblockMachineDefinition IMAGINARY_DREAM_FURNACE;
    public static MultiblockMachineDefinition IMAGINARY_MATTER_WEAVER;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {
        IMAGINARY_DIMENSION_GATEWAY = reg()
                .multiblock("imaginary_dimension_gateway", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.IMAGINARY_DIMENSION_GATEWAY_PROC)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_ANCHOR)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_ANCHOR))
                .workableCasingRenderer(tex("casing_imaginary_anchor"), OVERLAY)
                .register();

        IMAGINARY_TREE_OBSERVATION_ARRAY = reg()
                .multiblock("imaginary_tree_observation_array", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypesImaginary.IMAGINARY_TREE_OBSERVATION)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_TREE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_TREE))
                .workableCasingRenderer(tex("casing_imaginary_tree"), OVERLAY)
                .register();

        IMAGINARY_ANCHOR_DEVICE = reg()
                .multiblock("imaginary_anchor_device", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesImaginary.IMAGINARY_ANCHORING)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_ANCHOR)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_ANCHOR))
                .workableCasingRenderer(tex("casing_imaginary_anchor"), OVERLAY)
                .register();

        SEA_OF_QUANTA_OBSERVATORY = reg()
                .multiblock("sea_of_quanta_observatory", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypes.SEA_OF_QUANTA_OBSERVATION_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_TREE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_TREE))
                .workableCasingRenderer(tex("casing_imaginary_tree"), OVERLAY)
                .register();

        IMAGINARY_CIRCUIT_COMPUTATION_SANCTUM = reg()
                .multiblock("imaginary_circuit_computation_sanctum", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_LATTICE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_LATTICE))
                .workableCasingRenderer(tex("casing_imaginary_lattice"), OVERLAY)
                .register();

        SOULIUM_SUPERSTRUCTURE_FORGE = reg()
                .multiblock("soulium_superstructure_forge", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesImaginary.SOULIUM_SUPERSTRUCTURE_FORGING)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_WEAVE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_WEAVE))
                .workableCasingRenderer(tex("casing_imaginary_weave"), OVERLAY)
                .register();

        CIVILIZATION_EXCHANGE_COUNCIL_HUB = reg()
                .multiblock("civilization_exchange_council_hub", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesImaginary.CIVILIZATION_EXCHANGE)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_LATTICE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_LATTICE))
                .workableCasingRenderer(tex("casing_imaginary_lattice"), OVERLAY)
                .register();

        PRECIVILIZATION_DATABASE_DECODER = reg()
                .multiblock("precivilization_database_decoder", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypesImaginary.PRECIVILIZATION_DATABASE_DECODING)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_LATTICE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_LATTICE))
                .workableCasingRenderer(tex("casing_imaginary_lattice"), OVERLAY)
                .register();

        HONKAI_PHASE_PURIFICATION_PLANT = reg()
                .multiblock("honkai_phase_purification_plant", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesImaginary.HONKAI_PHASE_PURIFICATION)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_WEAVE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_WEAVE))
                .workableCasingRenderer(tex("casing_imaginary_weave"), OVERLAY)
                .register();

        DUAL_ENERGY_STABLE_SUPPLY_STATION = reg()
                .multiblock("dual_energy_stable_supply_station", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesImaginary.DUAL_ENERGY_STABLE_SUPPLY)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_CORE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_CORE))
                .workableCasingRenderer(tex("casing_imaginary_core"), OVERLAY)
                .register();

        IMAGINARY_DREAM_FURNACE = reg()
                .multiblock("imaginary_dream_furnace", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesImaginary.IMAGINARY_DREAM_MELTING)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_LATTICE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_LATTICE))
                .workableCasingRenderer(tex("casing_imaginary_lattice"), OVERLAY)
                .register();

        IMAGINARY_MATTER_WEAVER = reg()
                .multiblock("imaginary_matter_weaver", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesImaginary.IMAGINARY_MATTER_WEAVING)
                .appearanceBlock(CasingBlocks.CASING_IMAGINARY_WEAVE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_IMAGINARY_WEAVE))
                .workableCasingRenderer(tex("casing_imaginary_weave"), OVERLAY)
                .register();

        LOGGER.info("[HK3GTL] 虚数阶段多方块初始化完成（12台）。");
    }
}
