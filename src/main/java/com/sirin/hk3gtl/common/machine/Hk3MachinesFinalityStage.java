package com.sirin.hk3gtl.common.machine;



import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3P1Patterns;
import com.sirin.hk3gtl.common.multiblock.pattern.HyperionPatternProvider;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesFinality;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;

/**
 * 终焉阶段（v0.3）12 台机器。
 */
public class Hk3MachinesFinalityStage {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    public static MultiblockMachineDefinition HYPERION_FLAGSHIP;
    public static MultiblockMachineDefinition SHIPBOARD_FINALITY_OBSERVATION;
    public static MultiblockMachineDefinition SHIPBOARD_DUAL_ENERGY_REACTOR_DECK;
    public static MultiblockMachineDefinition SHIPBOARD_CIVILIZATION_COORDINATION_HALL;
    public static MultiblockMachineDefinition SHIPBOARD_DIVINE_KEY_SHRINE;
    public static MultiblockMachineDefinition FINALITY_CIVILIZATION_CONSTRUCTION_WORKS;
    public static MultiblockMachineDefinition CIVILIZATION_VALIDATION_MATRIX;
    public static MultiblockMachineDefinition FINALITY_CIVILIZATION_POWER_HUB;
    public static MultiblockMachineDefinition FINALITY_ULTIMATE_MATERIAL_FORGE;
    public static MultiblockMachineDefinition FINALITY_HONKAI_ANNIHILATION_RING;
    public static MultiblockMachineDefinition GRADUATION_PERMISSION_VERIFICATION_ALTAR;
    public static MultiblockMachineDefinition CIVILIZATION_WONDER_SANCTUM;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {
        // 休伯利安号控制器：外观使用原版石英方块（白色），与船身石英主体视觉一致
        HYPERION_FLAGSHIP = reg()
                .multiblock("hyperion_flagship", com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.HYPERION_FLAGSHIP_PROCESSING)
                .appearanceBlock(() -> net.minecraft.world.level.block.Blocks.QUARTZ_BLOCK)
                .pattern(HyperionPatternProvider::createPattern)
                .workableCasingRenderer(new ResourceLocation("minecraft", "block/quartz_block"), OVERLAY)
                .register();

        SHIPBOARD_FINALITY_OBSERVATION = reg()
                .multiblock("shipboard_finality_observation", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.SHIPBOARD_FINALITY_OBSERVATION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_HYPERION)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_HYPERION))
                .workableCasingRenderer(tex("casing_finality_hyperion"), OVERLAY)
                .register();

        SHIPBOARD_DUAL_ENERGY_REACTOR_DECK = reg()
                .multiblock("shipboard_dual_energy_reactor_deck", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.SHIPBOARD_DUAL_ENERGY_REACTOR)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_HYPERION)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_HYPERION))
                .workableCasingRenderer(tex("casing_finality_hyperion"), OVERLAY)
                .register();

        SHIPBOARD_CIVILIZATION_COORDINATION_HALL = reg()
                .multiblock("shipboard_civilization_coordination_hall", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.SHIPBOARD_ENDGAME_COORDINATION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_HYPERION)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_HYPERION))
                .workableCasingRenderer(tex("casing_finality_hyperion"), OVERLAY)
                .register();

        SHIPBOARD_DIVINE_KEY_SHRINE = reg()
                .multiblock("shipboard_divine_key_shrine", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.SHIPBOARD_DIVINE_KEY)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_HYPERION)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_HYPERION))
                .workableCasingRenderer(tex("casing_finality_hyperion"), OVERLAY)
                .register();

        FINALITY_CIVILIZATION_CONSTRUCTION_WORKS = reg()
                .multiblock("finality_civilization_construction_works", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.FINALITY_CIVILIZATION_CONSTRUCTION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_VOID)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_VOID))
                .workableCasingRenderer(tex("casing_finality_void"), OVERLAY)
                .register();

        CIVILIZATION_VALIDATION_MATRIX = reg()
                .multiblock("civilization_validation_matrix", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.CIVILIZATION_VALIDATION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_SANCTUM)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_SANCTUM))
                .workableCasingRenderer(tex("casing_finality_sanctum"), OVERLAY)
                .register();

        FINALITY_CIVILIZATION_POWER_HUB = reg()
                .multiblock("finality_civilization_power_hub", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.FINALITY_ENERGY_DISTRIBUTION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_DOMINION)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_DOMINION))
                .workableCasingRenderer(tex("casing_finality_dominion"), OVERLAY)
                .register();

        FINALITY_ULTIMATE_MATERIAL_FORGE = reg()
                .multiblock("finality_ultimate_material_forge", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.FINALITY_ULTIMATE_MATERIAL_FORGE)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_VOID)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_VOID))
                .workableCasingRenderer(tex("casing_finality_void"), OVERLAY)
                .register();

        FINALITY_HONKAI_ANNIHILATION_RING = reg()
                .multiblock("finality_honkai_annihilation_ring", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.FINALITY_HONKAI_ANNIHILATION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_DOMINION)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_DOMINION))
                .workableCasingRenderer(tex("casing_finality_dominion"), OVERLAY)
                .register();

        GRADUATION_PERMISSION_VERIFICATION_ALTAR = reg()
                .multiblock("graduation_permission_verification_altar", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.GRADUATION_PERMISSION_VERIFICATION)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_WONDER)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_WONDER))
                .workableCasingRenderer(tex("casing_finality_wonder"), OVERLAY)
                .register();

        CIVILIZATION_WONDER_SANCTUM = reg()
                .multiblock("civilization_wonder_sanctum", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypesFinality.CIVILIZATION_WONDER_SANCTUM)
                .appearanceBlock(CasingBlocks.CASING_FINALITY_WONDER)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_FINALITY_WONDER))
                .workableCasingRenderer(tex("casing_finality_wonder"), OVERLAY)
                .register();

        LOGGER.info("[HK3GTL] 终焉阶段多方块初始化完成（12台）。");
    }
}
