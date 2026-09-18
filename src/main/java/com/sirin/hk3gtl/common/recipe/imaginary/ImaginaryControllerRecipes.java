package com.sirin.hk3gtl.common.recipe.imaginary;



import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.machine.Hk3MachinesImaginaryStage;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 虚数阶段（v0.3）12 台控制器配方。
 */
public class ImaginaryControllerRecipes {

    private static final long IM1_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_1];
    private static final long IM2_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_2];

    public static void register(Consumer<FinishedRecipe> provider) {
        build(provider, "hk3gtl_imaginary_dimension_gateway", Hk3MachinesImaginaryStage.IMAGINARY_DIMENSION_GATEWAY,
                CasingBlocks.CASING_IMAGINARY_ANCHOR.get().asItem().getDefaultInstance(), "R-IM-001", IM2_EUT);
        // 死锁修复：本机器建成触发 E-FB-009，而 R-IM-001（虚数所有研究的前置根节点）
        // 又以 E-FB-009 为 requiredEvent。若门槛设为 R-IM-001 则"造机器需先解锁 R-IM-001、
        // 解锁 R-IM-001 又需先造机器"死锁。改绑上一阶段出口认证 R-AB-024（海渊毕业即可解锁），
        // 作为虚数阶段的无环入口锚点（与海渊入口研究矩阵无门槛同理）。
        build(provider, "hk3gtl_imaginary_tree_observation_array", Hk3MachinesImaginaryStage.IMAGINARY_TREE_OBSERVATION_ARRAY,
                CasingBlocks.CASING_IMAGINARY_TREE.get().asItem().getDefaultInstance(), "R-AB-024", IM1_EUT);
        build(provider, "hk3gtl_imaginary_anchor_device", Hk3MachinesImaginaryStage.IMAGINARY_ANCHOR_DEVICE,
                CasingBlocks.CASING_IMAGINARY_ANCHOR.get().asItem().getDefaultInstance(), "R-IM-004", IM1_EUT);
        build(provider, "hk3gtl_sea_of_quanta_observatory", Hk3MachinesImaginaryStage.SEA_OF_QUANTA_OBSERVATORY,
                CasingBlocks.CASING_IMAGINARY_TREE.get().asItem().getDefaultInstance(), "R-IM-005", IM2_EUT);
        build(provider, "hk3gtl_imaginary_circuit_computation_sanctum", Hk3MachinesImaginaryStage.IMAGINARY_CIRCUIT_COMPUTATION_SANCTUM,
                CasingBlocks.CASING_IMAGINARY_LATTICE.get().asItem().getDefaultInstance(), "R-IM-002", IM1_EUT);
        build(provider, "hk3gtl_soulium_superstructure_forge", Hk3MachinesImaginaryStage.SOULIUM_SUPERSTRUCTURE_FORGE,
                CasingBlocks.CASING_IMAGINARY_WEAVE.get().asItem().getDefaultInstance(), "R-IM-010", IM2_EUT);
        build(provider, "hk3gtl_civilization_exchange_council_hub", Hk3MachinesImaginaryStage.CIVILIZATION_EXCHANGE_COUNCIL_HUB,
                CasingBlocks.CASING_IMAGINARY_LATTICE.get().asItem().getDefaultInstance(), "R-IM-006", IM2_EUT);
        build(provider, "hk3gtl_precivilization_database_decoder", Hk3MachinesImaginaryStage.PRECIVILIZATION_DATABASE_DECODER,
                CasingBlocks.CASING_IMAGINARY_LATTICE.get().asItem().getDefaultInstance(), "R-IM-007", IM2_EUT);
        build(provider, "hk3gtl_honkai_phase_purification_plant", Hk3MachinesImaginaryStage.HONKAI_PHASE_PURIFICATION_PLANT,
                CasingBlocks.CASING_IMAGINARY_WEAVE.get().asItem().getDefaultInstance(), "R-IM-008", IM2_EUT);
        build(provider, "hk3gtl_dual_energy_stable_supply_station", Hk3MachinesImaginaryStage.DUAL_ENERGY_STABLE_SUPPLY_STATION,
                CasingBlocks.CASING_IMAGINARY_CORE.get().asItem().getDefaultInstance(), "R-IM-009", IM2_EUT);
        build(provider, "hk3gtl_imaginary_dream_furnace", Hk3MachinesImaginaryStage.IMAGINARY_DREAM_FURNACE,
                CasingBlocks.CASING_IMAGINARY_LATTICE.get().asItem().getDefaultInstance(), "R-IM-011", IM2_EUT);
        build(provider, "hk3gtl_imaginary_matter_weaver", Hk3MachinesImaginaryStage.IMAGINARY_MATTER_WEAVER,
                CasingBlocks.CASING_IMAGINARY_WEAVE.get().asItem().getDefaultInstance(), "R-IM-012", IM2_EUT);
    }

    private static void build(Consumer<FinishedRecipe> provider, String recipeId, MultiblockMachineDefinition output,
                              ItemStack casing, String researchId, long eut) {
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(recipeId)
                .inputItems(new ItemStack(casing.getItem(), 96))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 48))
                .inputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_4.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .outputItems(output.asStack())
                .duration(2400)
                .EUt(eut)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", recipeId, researchId);
    }
}
