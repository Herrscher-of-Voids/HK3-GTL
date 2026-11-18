package com.sirin.hk3gtl.common.machine.research;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MachineDefinition;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.client.renderer.machine.MachineRenderer;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ResearchInstitutePatterns;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

public final class Hk3ResearchMachines {
    public static MachineDefinition RESEARCH_COMPUTER;
    public static MultiblockMachineDefinition MATTER_RECONSTRUCTION_INSTITUTE;
    public static MultiblockMachineDefinition QUANTUM_DOMAIN_INSTITUTE;
    public static MultiblockMachineDefinition WORLD_MAINTENANCE_INSTITUTE;
    public static MultiblockMachineDefinition CIVILIZATION_COGNITION_DOME;
    private static MultiblockMachineDefinition firstInstitute;
    private Hk3ResearchMachines() {}

    public static void init() {
        RESEARCH_COMPUTER = Hk3Gtl.REGISTRATE.machine("research_point_computer", Hk3ResearchComputerMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .renderer(() -> new MachineRenderer(new ResourceLocation("hk3gtl", "block/research_point_computer_r12")))
                .tooltips(Component.translatable("hk3gtl.research.computer.tooltip"),
                        Component.translatable("hk3gtl.research.computer.tooltip.circuit"),
                        Component.translatable("hk3gtl.research.computer.tooltip.rate"),
                        Component.translatable("hk3gtl.research.computer.tooltip.power"))
                .register();
    }

    public static void initInstitutes(MultiblockMachineDefinition stageOne) {
        if (firstInstitute != null) throw new IllegalStateException("研究所已经注册");
        firstInstitute = java.util.Objects.requireNonNull(stageOne, "一阶研究所尚未注册");
        MATTER_RECONSTRUCTION_INSTITUTE = institute("s02_matter_reconstruction_institute", 2);
        QUANTUM_DOMAIN_INSTITUTE = institute("s03_quantum_domain_institute", 3);
        WORLD_MAINTENANCE_INSTITUTE = institute("s04_world_maintenance_institute", 4);
        CIVILIZATION_COGNITION_DOME = institute("s05_civilization_cognition_dome", 5);
    }

    public static MultiblockMachineDefinition institute(int lab) {
        return switch (lab) {
            case 1 -> firstInstitute;
            case 2 -> MATTER_RECONSTRUCTION_INSTITUTE;
            case 3 -> QUANTUM_DOMAIN_INSTITUTE;
            case 4 -> WORLD_MAINTENANCE_INSTITUTE;
            case 5 -> CIVILIZATION_COGNITION_DOME;
            default -> throw new IllegalArgumentException("未知研究所阶级：" + lab);
        };
    }

    private static MultiblockMachineDefinition institute(String name, int lab) {
        String key = String.format(java.util.Locale.ROOT, "s%02d", lab);
        return Hk3Gtl.REGISTRATE.multiblock(name, holder -> new Hk3ResearchInstituteMachine(holder, lab))
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypes.ABYSS_RESEARCH_ANALYSIS_RECIPES)
                .appearanceBlock(() -> Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(definition -> Hk3ResearchInstitutePatterns.create(definition, key))
                .shapeInfo(definition -> Hk3ApprovedArchitectureShapes.create(definition, key))
                .workableCasingRenderer(new ResourceLocation("hk3gtl", "block/casings/industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/" + key + "_unique_r178"))
                .tooltips(Component.translatable("hk3gtl.research.lab.grade." + lab),
                        Component.translatable("hk3gtl.research.lab.tooltip"),
                        Component.translatable("hk3gtl.machine.controller.research_required"),
                        Component.translatable("hk3gtl.research.lab.tooltip.payment"),
                        Component.translatable("hk3gtl.research.lab.tooltip.supply"),
                        Component.translatable("hk3gtl.research.lab.tooltip.slots",
                                com.sirin.hk3gtl.common.research.Hk3ResearchMath.slots(lab)),
                        Component.translatable("hk3gtl.research.lab.tooltip.pressure"))
                .register();
    }
}

