package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.*;

/**
 * I02 光谱分析阵列的兼容 Pattern；几何与已确认蓝图保持不变。
 */
public class Hk3I02SpectrumPatternImpl {
    protected Hk3I02SpectrumPatternImpl() {}

    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return Hk3ApprovedArchitecturePatterns.create(definition,"i02");
    }
}
