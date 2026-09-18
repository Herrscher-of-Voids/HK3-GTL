package com.sirin.hk3gtl.common.machine;



import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3P1Patterns;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesQuantum;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;

/**
 * 量子阶段（v0.3）12 台机器。
 */
public class Hk3MachinesQuantumStage {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    public static MultiblockMachineDefinition QUANTUM_ENTANGLEMENT_COMPUTER;
    public static MultiblockMachineDefinition THOUSAND_REALMS_TRAIN;
    public static MultiblockMachineDefinition WORLD_BUBBLE_MELTDOWN_FURNACE;
    public static MultiblockMachineDefinition QUANTUM_SUPERCONDUCTOR_LATTICE_FACTORY;
    public static MultiblockMachineDefinition HONKAI_WIRELESS_TRANSIT_HUB;
    public static MultiblockMachineDefinition QUANTUM_THOUGHT_FORGE;
    public static MultiblockMachineDefinition DIVINE_KEY_GALLERY;
    public static MultiblockMachineDefinition QUANTUM_CIVILIZATION_TRADE_PORT;
    public static MultiblockMachineDefinition QUANTUM_HONKAI_FUSION_RING;
    public static MultiblockMachineDefinition FINALITY_PRESSURE_BUFFER_ARRAY;
    public static MultiblockMachineDefinition WONDER_CONSTRUCTION_SIMULATION_PLATFORM;
    public static MultiblockMachineDefinition QUANTUM_PRECISION_ASSEMBLY_FACTORY;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {
        QUANTUM_ENTANGLEMENT_COMPUTER = reg()
                .multiblock("quantum_entanglement_computer", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.QUANTUM_ENTANGLEMENT_COMPUTING)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_ENTANGLE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_ENTANGLE))
                .workableCasingRenderer(tex("casing_quantum_entangle"), OVERLAY)
                .register();

        THOUSAND_REALMS_TRAIN = reg()
                .multiblock("thousand_realms_train", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.THOUSAND_REALMS_TRANSIT)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_SEA)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_SEA))
                .workableCasingRenderer(tex("casing_quantum_sea"), OVERLAY)
                .register();

        WORLD_BUBBLE_MELTDOWN_FURNACE = reg()
                .multiblock("world_bubble_meltdown_furnace", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.WORLD_BUBBLE_MELTDOWN)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_BUBBLE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_BUBBLE))
                .workableCasingRenderer(tex("casing_quantum_bubble"), OVERLAY)
                .register();

        QUANTUM_SUPERCONDUCTOR_LATTICE_FACTORY = reg()
                .multiblock("quantum_superconductor_lattice_factory", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.QUANTUM_SUPERCONDUCTOR_LATTICE)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_FLUX)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_FLUX))
                .workableCasingRenderer(tex("casing_quantum_flux"), OVERLAY)
                .register();

        HONKAI_WIRELESS_TRANSIT_HUB = reg()
                .multiblock("honkai_wireless_transit_hub", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypesQuantum.HONKAI_WIRELESS_TRANSIT)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_FLUX)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_FLUX))
                .workableCasingRenderer(tex("casing_quantum_flux"), OVERLAY)
                .register();

        QUANTUM_THOUGHT_FORGE = reg()
                .multiblock("quantum_thought_forge", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.QUANTUM_THOUGHT_FORGING)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_BUBBLE)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_BUBBLE))
                .workableCasingRenderer(tex("casing_quantum_bubble"), OVERLAY)
                .register();

        DIVINE_KEY_GALLERY = reg()
                .multiblock("divine_key_gallery", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.DIVINE_KEY_DISPLAY)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_SEA)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_SEA))
                .workableCasingRenderer(tex("casing_quantum_sea"), OVERLAY)
                .register();

        QUANTUM_CIVILIZATION_TRADE_PORT = reg()
                .multiblock("quantum_civilization_trade_port", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.QUANTUM_CIVILIZATION_TRADE)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_SEA)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_SEA))
                .workableCasingRenderer(tex("casing_quantum_sea"), OVERLAY)
                .register();

        QUANTUM_HONKAI_FUSION_RING = reg()
                .multiblock("quantum_honkai_fusion_ring", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.QUANTUM_HONKAI_FUSION)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_FLUX)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_FLUX))
                .workableCasingRenderer(tex("casing_quantum_flux"), OVERLAY)
                .register();

        FINALITY_PRESSURE_BUFFER_ARRAY = reg()
                .multiblock("finality_pressure_buffer_array", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.FINALITY_PRESSURE_BUFFERING)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_FLUX)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_FLUX))
                .workableCasingRenderer(tex("casing_quantum_flux"), OVERLAY)
                .register();

        WONDER_CONSTRUCTION_SIMULATION_PLATFORM = reg()
                .multiblock("wonder_construction_simulation_platform", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.WONDER_CONSTRUCTION_SIMULATION)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_SEA)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_SEA))
                .workableCasingRenderer(tex("casing_quantum_sea"), OVERLAY)
                .register();

        // 独立量子机器：不使用 shipboard recipeType，不参与休伯利安 Pattern 候选。
        QUANTUM_PRECISION_ASSEMBLY_FACTORY = reg()
                .multiblock("quantum_precision_assembly_factory", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesQuantum.QUANTUM_PRECISION_ASSEMBLY)
                .appearanceBlock(CasingBlocks.CASING_QUANTUM_FLUX)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_QUANTUM_FLUX))
                .workableCasingRenderer(tex("casing_quantum_flux"), OVERLAY)
                .register();

        LOGGER.info("[HK3GTL] 量子阶段多方块初始化完成（12 台）。");
    }
}
