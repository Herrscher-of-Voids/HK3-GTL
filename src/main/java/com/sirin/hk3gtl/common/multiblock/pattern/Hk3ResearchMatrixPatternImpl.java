package com.sirin.hk3gtl.common.multiblock.pattern;


/**
 * 【文件职责】
 * - 维护 Hk3ResearchMatrixPatternImpl 的核心功能实现。
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
 * 【变更记录 #2】2026-07-03 01:25:00（第 2 次备注 · 内测三第 26 次更新）
 * - 删除：
 *   1) X 谓词中的 PartAbility.INPUT_ENERGY / SUBSTATION_INPUT_ENERGY / INPUT_LASER 三条能源仓谓词。
 *   2) 可删原因：研究矩阵扣电改走控制器 Hk3PlayerGridEnergyTrait（玩家电网直扣），
 *      consumeEnergy 反射到的 getEnergyContainer() 现在聚合的就是该特征，无需任何实体能源仓。
 *   3) 影响范围：研究矩阵结构中不再允许放置 GT 能源/激光仓；崩坏能仓保留。
 * - 新增：无。
 * - 修改：类 Javadoc 同步更新能量获取描述。
 * - 用途：落实"无能源仓 + 玩家 UUID 电网扣电"能源模型。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartAbility;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #3】2026-09-25 02:18:00（内测5修订70）
 * 删除：旧结构退出正式入口，原实现已归档。新增：获批建筑的统一成型资源入口。
 * 修改：使用s01正式逐格结构，去除旧海渊建材依赖；用途：结构与确认预览一致，不更改机器工艺。
 */
/**
 * 【变更记录 #4】2026-10-15 01:06:24（第4次备注 · 内测5修订156）
 * 删除：一阶研究所入口对工业线通用Pattern适配的依赖，历史资源和备注保留。
 * 新增：无新生产工艺；正式调用研究所专用Hk3ResearchInstitutePatterns。
 * 修改：沿batch-05确认院区替换s01几何，并保留六接口外观及既有可选崩坏能能力。
 * 用途：保证五阶研究院区使用同一正式成型规则，不将研究开题材料和EU改为仓室扣除。
 */
public class Hk3ResearchMatrixPatternImpl {

    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return Hk3ResearchInstitutePatterns.create(definition,"s01");
    }
}
