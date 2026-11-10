package com.sirin.hk3gtl.common.machine.research;

/** 【控制器材质变更 · 修订178】2026-10-26 22:02:44：按负责人“采用32套候选，保留4套原材质”接入独立三态面板；保留既有四套像素，不改建筑、控制器ID或工艺。 */

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

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-10-15 01:06:24（第1次备注 · 内测5修订156）
 * 删除：无；一阶研究所和研究点计算机原注册ID继续使用。
 * 新增：S02–S05固定阶级研究控制器、一次性注册入口和按阶级只读定义查询。
 * 修改：新控制器使用已批准院区Pattern、既有独立研究机器及四向水平旋转。
 * 用途：让五阶研究所实际承载既有研究队列，保持研究授权、玩家背包付款、玩家电网及槽位公式。
 */
/**
 * 【变更记录 #2】2026-10-15 02:00:40（内测5修订157）
 * 删除：S02–S05 默认预览逐空气格候选对象的生成路径。
 * 新增：保持完整院区尺寸和实际主控朝向的正式 NBT 显式形状。
 * 修改：定制稀疏预览环境省略空气映射；普通 GT 环境使用共享空气对象。
 * 用途：保留五阶研究所预览与严格成型约束，减少扩建院区的预览内存。
 */
public final class Hk3ResearchMachines {
    public static MachineDefinition RESEARCH_COMPUTER;
    public static MultiblockMachineDefinition MATTER_RECONSTRUCTION_INSTITUTE;
    public static MultiblockMachineDefinition QUANTUM_DOMAIN_INSTITUTE;
    public static MultiblockMachineDefinition WORLD_MAINTENANCE_INSTITUTE;
    public static MultiblockMachineDefinition CIVILIZATION_COGNITION_DOME;
    private static MultiblockMachineDefinition firstInstitute;
    private Hk3ResearchMachines() {}

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static void init() {
        RESEARCH_COMPUTER = Hk3Gtl.REGISTRATE.machine("research_point_computer", Hk3ResearchComputerMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .renderer(() -> new MachineRenderer(new ResourceLocation("hk3gtl", "block/research_point_computer")))
                .tooltips(Component.translatable("hk3gtl.research.computer.tooltip"))
                .register();
    }

    /** 一阶保留原注册 ID；其余四阶使用已批准院区和现有独立研究队列。 */
    public static void initInstitutes(MultiblockMachineDefinition stageOne) {
        if (firstInstitute != null) throw new IllegalStateException("研究所已经注册");
        firstInstitute = java.util.Objects.requireNonNull(stageOne, "一阶研究所尚未注册");
        MATTER_RECONSTRUCTION_INSTITUTE = institute("s02_matter_reconstruction_institute", 2);
        QUANTUM_DOMAIN_INSTITUTE = institute("s03_quantum_domain_institute", 3);
        WORLD_MAINTENANCE_INSTITUTE = institute("s04_world_maintenance_institute", 4);
        CIVILIZATION_COGNITION_DOME = institute("s05_civilization_cognition_dome", 5);
    }

    /** 供模板与诊断取得实际阶级定义，不允许以客户端数据改变研究所阶级。 */
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
                        Component.translatable("hk3gtl.research.lab.tooltip"))
                .register();
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
