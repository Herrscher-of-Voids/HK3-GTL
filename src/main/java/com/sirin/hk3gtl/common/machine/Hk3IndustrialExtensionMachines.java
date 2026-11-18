package com.sirin.hk3gtl.common.machine;


import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchProcessMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3IndustrialExtensionPatterns;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

/**
 * 正式注册I14–I18批准结构；复用玩家电网、研究身份和既有类型。
 */
public final class Hk3IndustrialExtensionMachines {
    public static MultiblockMachineDefinition SOULIUM_POLYMERIZATION_DIE_CASTER;
    public static MultiblockMachineDefinition SOULIUM_RECONSTRUCTION_ANNEALING_FURNACE;
    public static MultiblockMachineDefinition SOULIUM_PRECISION_PROCESSING_CENTER;
    public static MultiblockMachineDefinition HONKAI_FUEL_ROD_ENCAPSULATION_ARRAY;
    private static final ResourceLocation SHELL = new ResourceLocation("hk3gtl", "block/casings/industrial_controller_shell");

    private Hk3IndustrialExtensionMachines() {}

    public static void init() {
        SOULIUM_POLYMERIZATION_DIE_CASTER = register("soulium_polymerization_die_caster", "i14");
        SOULIUM_RECONSTRUCTION_ANNEALING_FURNACE = register("soulium_reconstruction_annealing_furnace", "i15");
        SOULIUM_PRECISION_PROCESSING_CENTER = register("soulium_precision_processing_center", "i16");
        HONKAI_FUEL_ROD_ENCAPSULATION_ARRAY = register("honkai_fuel_rod_encapsulation_array", "i18");
    }

    /** 保留原ID、类型和运行执行器，避免改变既有浓缩配方及输出研究结算。 */
    public static MultiblockMachineDefinition registerConcentration() {
        return Hk3Gtl.REGISTRATE.multiblock("honkai_fuel_concentration_plant", Hk3LiquidProcessMachine::new)
                .tier(GTValues.MAX).rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3IndustrialRecipeTypes.CONCENTRATION)
                .appearanceBlock(() -> Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3IndustrialExtensionPatterns.create(def, "i17"))
                .shapeInfo(def -> Hk3ApprovedArchitectureShapes.create(def, "i17"))
                .workableCasingRenderer(SHELL, new ResourceLocation("hk3gtl", "block/overlay/i17_unique_r178"))
                .tooltips(Component.translatable("hk3gtl.machine.honkai_fuel_concentration_plant.tooltip.0"),
                        Component.translatable("hk3gtl.machine.honkai_fuel_concentration_plant.tooltip.1"),
                        Component.translatable("hk3gtl.machine.honkai_fuel_concentration_plant.tooltip.2"),
                        Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();
    }

    private static MultiblockMachineDefinition register(String name, String layout) {
        return Hk3Gtl.REGISTRATE.multiblock(name, holder -> new Hk3ResearchProcessMachine(holder,
                        layout.toUpperCase(java.util.Locale.ROOT)))
                .tier(GTValues.MAX).rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3ResearchProcessTypes.get(layout.toUpperCase(java.util.Locale.ROOT)))
                .appearanceBlock(() -> Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3IndustrialExtensionPatterns.create(def, layout))
                .shapeInfo(def -> Hk3ApprovedArchitectureShapes.create(def, layout))
                .workableCasingRenderer(SHELL, new ResourceLocation("hk3gtl", "block/overlay/" + layout + "_unique_r178"))
                .tooltips(Component.translatable("hk3gtl.machine." + name + ".tooltip.0"),
                        Component.translatable("hk3gtl.machine." + name + ".tooltip.1"),
                        Component.translatable("hk3gtl.machine." + name + ".tooltip.2"),
                        Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();
    }
}
