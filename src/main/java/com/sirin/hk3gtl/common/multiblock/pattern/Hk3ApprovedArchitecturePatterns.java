package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;

public final class Hk3ApprovedArchitecturePatterns {
    private Hk3ApprovedArchitecturePatterns() {}

    /** 将单台获批逐格资源编成模式；朝北时X向东、Y向上、Z向南，支持四个水平朝向。 */
    public static BlockPattern create(MultiblockMachineDefinition definition, String id) {
        return id.equals("s01") ? Hk3ResearchInstitutePatterns.create(definition, id)
                : Hk3IndustrialApprovedPatterns.create(definition, id);
    }
}
