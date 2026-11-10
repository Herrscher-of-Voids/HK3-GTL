package com.sirin.hk3gtl.common.multiblock.build;

import net.minecraft.world.level.block.DaylightDetectorBlock;
import net.minecraft.world.level.block.state.BlockState;

/** 日光探测器亮度随时间变化，不改变舰体；反转模式和其他结构状态仍须精确匹配。 */
public final class Hk3BuildState {
    private Hk3BuildState() {}
    public static boolean matches(BlockState actual, BlockState expected) {
        if (actual == expected) return true;
        return actual.getBlock() == expected.getBlock() && actual.getBlock() instanceof DaylightDetectorBlock
                && actual.setValue(DaylightDetectorBlock.POWER, expected.getValue(DaylightDetectorBlock.POWER)) == expected;
    }
}
