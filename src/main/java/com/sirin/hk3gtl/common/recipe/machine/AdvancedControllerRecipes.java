package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.finality.FinalityCircuitItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumCircuitItems;
import com.sirin.hk3gtl.common.machine.Hk3MachinesFinalityStage;
import com.sirin.hk3gtl.common.machine.Hk3MachinesQuantumStage;
import com.sirin.hk3gtl.common.machine.Hk3MachinesWonderStage;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;


public final class AdvancedControllerRecipes {

    private static final long Q2_EUT = Hk3Values.VA_LONG[Hk3Tiers.QUANTUM_2];
    private static final long F2_EUT = Hk3Values.VA_LONG[Hk3Tiers.FINALITY_2];
    private static final long F4_EUT = Hk3Values.VA_LONG[Hk3Tiers.FINALITY_4];

    private AdvancedControllerRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        addQuantumControllers(provider);
        addFinalityControllers(provider);
        addWonderControllers(provider);
    }

    private static void addQuantumControllers(Consumer<FinishedRecipe> provider) {
        ItemStack qCircuit = new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 64);
        // 死锁修复：本机器建成触发 E-FB-012，而 R-QT-001（量子所有研究前置根节点）以 E-FB-012
        // 为 requiredEvent；原门槛 R-QT-004 又前置于 R-QT-001，形成"造机器需先解锁量子研究、
        // 解锁量子研究又需先造机器"死锁。改绑虚数出口认证 R-IM-021（虚数毕业即可解锁），
        // 作为量子阶段的无环入口锚点。
        build(provider, "hk3gtl_quantum_entanglement_computer", Hk3MachinesQuantumStage.QUANTUM_ENTANGLEMENT_COMPUTER, CasingBlocks.CASING_QUANTUM_ENTANGLE.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-IM-021");
        build(provider, "hk3gtl_thousand_realms_train", Hk3MachinesQuantumStage.THOUSAND_REALMS_TRAIN, CasingBlocks.CASING_QUANTUM_SEA.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-006");
        build(provider, "hk3gtl_world_bubble_meltdown_furnace", Hk3MachinesQuantumStage.WORLD_BUBBLE_MELTDOWN_FURNACE, CasingBlocks.CASING_QUANTUM_BUBBLE.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-009");
        build(provider, "hk3gtl_quantum_superconductor_lattice_factory", Hk3MachinesQuantumStage.QUANTUM_SUPERCONDUCTOR_LATTICE_FACTORY, CasingBlocks.CASING_QUANTUM_FLUX.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-005");
        build(provider, "hk3gtl_honkai_wireless_transit_hub", Hk3MachinesQuantumStage.HONKAI_WIRELESS_TRANSIT_HUB, CasingBlocks.CASING_QUANTUM_FLUX.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-008");
        build(provider, "hk3gtl_quantum_thought_forge", Hk3MachinesQuantumStage.QUANTUM_THOUGHT_FORGE, CasingBlocks.CASING_QUANTUM_BUBBLE.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-008");
        build(provider, "hk3gtl_divine_key_gallery", Hk3MachinesQuantumStage.DIVINE_KEY_GALLERY, CasingBlocks.CASING_QUANTUM_SEA.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-009");
        build(provider, "hk3gtl_quantum_civilization_trade_port", Hk3MachinesQuantumStage.QUANTUM_CIVILIZATION_TRADE_PORT, CasingBlocks.CASING_QUANTUM_SEA.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-009");
        build(provider, "hk3gtl_quantum_honkai_fusion_ring", Hk3MachinesQuantumStage.QUANTUM_HONKAI_FUSION_RING, CasingBlocks.CASING_QUANTUM_FLUX.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-010");
        build(provider, "hk3gtl_finality_pressure_buffer_array", Hk3MachinesQuantumStage.FINALITY_PRESSURE_BUFFER_ARRAY, CasingBlocks.CASING_QUANTUM_FLUX.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-011");
        build(provider, "hk3gtl_wonder_construction_simulation_platform", Hk3MachinesQuantumStage.WONDER_CONSTRUCTION_SIMULATION_PLATFORM, CasingBlocks.CASING_QUANTUM_SEA.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-012");
        build(provider, "hk3gtl_quantum_precision_assembly_factory", Hk3MachinesQuantumStage.QUANTUM_PRECISION_ASSEMBLY_FACTORY, CasingBlocks.CASING_QUANTUM_FLUX.get().asItem().getDefaultInstance(), qCircuit, Q2_EUT, "R-QT-010");
    }

    private static void addFinalityControllers(Consumer<FinishedRecipe> provider) {
        ItemStack fInputCircuit = new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 64);
        build(provider, "hk3gtl_hyperion_flagship", Hk3MachinesFinalityStage.HYPERION_FLAGSHIP, CasingBlocks.CASING_FINALITY_HYPERION.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-002");
        build(provider, "hk3gtl_shipboard_finality_observation", Hk3MachinesFinalityStage.SHIPBOARD_FINALITY_OBSERVATION, CasingBlocks.CASING_FINALITY_HYPERION.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-003");
        build(provider, "hk3gtl_shipboard_dual_energy_reactor_deck", Hk3MachinesFinalityStage.SHIPBOARD_DUAL_ENERGY_REACTOR_DECK, CasingBlocks.CASING_FINALITY_HYPERION.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-004");
        build(provider, "hk3gtl_shipboard_civilization_coordination_hall", Hk3MachinesFinalityStage.SHIPBOARD_CIVILIZATION_COORDINATION_HALL, CasingBlocks.CASING_FINALITY_HYPERION.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-003");
        build(provider, "hk3gtl_shipboard_divine_key_shrine", Hk3MachinesFinalityStage.SHIPBOARD_DIVINE_KEY_SHRINE, CasingBlocks.CASING_FINALITY_HYPERION.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-004");
        build(provider, "hk3gtl_finality_civilization_construction_works", Hk3MachinesFinalityStage.FINALITY_CIVILIZATION_CONSTRUCTION_WORKS, CasingBlocks.CASING_FINALITY_VOID.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-005");
        build(provider, "hk3gtl_civilization_validation_matrix", Hk3MachinesFinalityStage.CIVILIZATION_VALIDATION_MATRIX, CasingBlocks.CASING_FINALITY_SANCTUM.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-007");
        build(provider, "hk3gtl_finality_civilization_power_hub", Hk3MachinesFinalityStage.FINALITY_CIVILIZATION_POWER_HUB, CasingBlocks.CASING_FINALITY_DOMINION.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-004");
        build(provider, "hk3gtl_finality_ultimate_material_forge", Hk3MachinesFinalityStage.FINALITY_ULTIMATE_MATERIAL_FORGE, CasingBlocks.CASING_FINALITY_VOID.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-005");
        build(provider, "hk3gtl_finality_honkai_annihilation_ring", Hk3MachinesFinalityStage.FINALITY_HONKAI_ANNIHILATION_RING, CasingBlocks.CASING_FINALITY_DOMINION.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-006");
        build(provider, "hk3gtl_graduation_permission_verification_altar", Hk3MachinesFinalityStage.GRADUATION_PERMISSION_VERIFICATION_ALTAR, CasingBlocks.CASING_FINALITY_WONDER.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-009");
        build(provider, "hk3gtl_civilization_wonder_sanctum", Hk3MachinesFinalityStage.CIVILIZATION_WONDER_SANCTUM, CasingBlocks.CASING_FINALITY_WONDER.get().asItem().getDefaultInstance(), fInputCircuit, F2_EUT, "R-FN-008");
    }

    private static void addWonderControllers(Consumer<FinishedRecipe> provider) {
        ItemStack wCircuit = new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 64);
        build(provider, "hk3gtl_honkai_ultimate_fusion_core", Hk3MachinesWonderStage.HONKAI_ULTIMATE_FUSION_CORE, CasingBlocks.CASING_FINALITY_DOMINION.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-008");
        build(provider, "hk3gtl_divine_key_grand_cathedral", Hk3MachinesWonderStage.DIVINE_KEY_GRAND_CATHEDRAL, CasingBlocks.CASING_FINALITY_WONDER.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-008");
        build(provider, "hk3gtl_civilization_judgment_corridor", Hk3MachinesWonderStage.CIVILIZATION_JUDGMENT_CORRIDOR, CasingBlocks.CASING_FINALITY_SANCTUM.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-009");
        build(provider, "hk3gtl_civilization_memory_eternal_monument", Hk3MachinesWonderStage.CIVILIZATION_MEMORY_ETERNAL_MONUMENT, CasingBlocks.CASING_FINALITY_SANCTUM.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-008");
        build(provider, "hk3gtl_myriad_realms_communication_nexus", Hk3MachinesWonderStage.MYRIAD_REALMS_COMMUNICATION_NEXUS, CasingBlocks.CASING_QUANTUM_ENTANGLE.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-008");
        build(provider, "hk3gtl_destiny_loom", Hk3MachinesWonderStage.DESTINY_LOOM, CasingBlocks.CASING_IMAGINARY_TREE.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-008");
        build(provider, "hk3gtl_civilization_eye_observation_array", Hk3MachinesWonderStage.CIVILIZATION_EYE_OBSERVATION_ARRAY, CasingBlocks.CASING_FINALITY_SANCTUM.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-009");
        build(provider, "hk3gtl_cycle_narrator_platform", Hk3MachinesWonderStage.CYCLE_NARRATOR_PLATFORM, CasingBlocks.CASING_FINALITY_SANCTUM.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-008");
        build(provider, "hk3gtl_civilization_starship_museum", Hk3MachinesWonderStage.CIVILIZATION_STARSHIP_MUSEUM, CasingBlocks.CASING_FINALITY_HYPERION.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-009");
        build(provider, "hk3gtl_proof_of_existence_memorial", Hk3MachinesWonderStage.PROOF_OF_EXISTENCE_MEMORIAL, CasingBlocks.CASING_FINALITY_WONDER.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-009");
        build(provider, "hk3gtl_ultimate_meditation_sanctum", Hk3MachinesWonderStage.ULTIMATE_MEDITATION_SANCTUM, CasingBlocks.CASING_FINALITY_SANCTUM.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-009");
        build(provider, "hk3gtl_grand_convergence_altar", Hk3MachinesWonderStage.GRAND_CONVERGENCE_ALTAR, CasingBlocks.CASING_FINALITY_WONDER.get().asItem().getDefaultInstance(), wCircuit, F4_EUT, "R-FN-012");
    }

    private static void build(Consumer<FinishedRecipe> provider,
                              String recipeId,
                              MultiblockMachineDefinition outputMachine,
                              ItemStack casingStack,
                              ItemStack circuitStack,
                              long eut,
                              String researchId) {
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(recipeId)
                .inputItems(new ItemStack(casingStack.getItem(), 96))
                .inputItems(circuitStack)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 16))
                .outputItems(outputMachine.asStack())
                .duration(3600)
                .EUt(eut)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", recipeId, researchId);
    }
}
