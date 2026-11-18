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
 */
public class Hk3I01CollectionPatternImpl {
    protected Hk3I01CollectionPatternImpl() {}

    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return Hk3ApprovedArchitecturePatterns.create(definition,"i01");
    }
}
