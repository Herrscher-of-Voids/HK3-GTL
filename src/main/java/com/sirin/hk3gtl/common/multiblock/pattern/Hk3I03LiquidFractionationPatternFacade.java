package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;

public final class Hk3I03LiquidFractionationPatternFacade {
    private Hk3I03LiquidFractionationPatternFacade() {}
    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return Hk3I03LiquidFractionationPattern.createPattern(definition);
    }
}
