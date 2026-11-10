package com.sirin.hk3gtl.common.multiblock.pattern;


/**
 * 【文件职责】
 * - 维护 Hk3TemporaryMultiblockPatternsImpl 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;

/** 中文说明：该处说明已按当前代码行为整理。*/
public class Hk3TemporaryMultiblockPatternsImpl {

    private Hk3TemporaryMultiblockPatternsImpl() {}

    /**
     * 创建仅控制器本体的临时结构。
     *
     * @param definition 多方块机器定义，用于绑定控制器方块
     * @return 供成型校验的 {@link BlockPattern}
     */
    public static BlockPattern createControllerOnly(MultiblockMachineDefinition definition) {
        return FactoryBlockPattern.start()
                .aisle("S")
                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .build();
    }

    /**
     * 兼容旧引用：旧临时结构入口，现在统一委托到仅控制器结构。
     */
    public static BlockPattern createDirtCube3x3x3(MultiblockMachineDefinition definition) {
        return createControllerOnly(definition);
    }
}
