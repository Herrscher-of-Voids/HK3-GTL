package com.sirin.hk3gtl.common.multiblock.pattern;














import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartAbility;













public class Hk3ResearchMatrixPatternImpl {

    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return Hk3ResearchInstitutePatterns.create(definition,"s01");
    }
}
