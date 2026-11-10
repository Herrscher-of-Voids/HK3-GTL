package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.*;

/**
 * I01 采集塔的兼容 Pattern；几何与已确认蓝图保持不变。
 * 【变更记录 #2】2026-09-24 18:56:36（内测5修订67）
 * 修改：每种结构符号增加 MAX 海渊材料作为首选，并保留旧材料作为存档兼容分支。
 * 修改：物品槽和流体槽改为同类输入/输出能力可互换，避免端口方向绑定到单个坐标。
 */
/**
 * 【变更记录 #3】2026-09-25 02:18:00（内测5修订70）
 * 删除：旧结构退出正式入口，原实现已归档。新增：获批建筑的统一成型资源入口。
 * 修改：使用i01正式逐格结构，去除旧海渊建材依赖；用途：结构与确认预览一致，不更改机器工艺。
 */
public class Hk3I01CollectionPatternImpl {
    protected Hk3I01CollectionPatternImpl() {}

    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return Hk3ApprovedArchitecturePatterns.create(definition,"i01");
    }
}
