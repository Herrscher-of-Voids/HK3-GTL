package com.sirin.hk3gtl.common.gaze;

import net.minecraft.server.level.ServerPlayer;

/**
 * 注视增长修正器：统一处理增长侧的抑制规则，避免在事件/研究代码里重复乘法逻辑。
 */






public final class Hk3GazeGrowth {

    private Hk3GazeGrowth() {}

    /**
     * 对注视变化量做统一修正：
     * - 负值（降低注视）原样返回
     * - 不再把旁置净化控制器当作抑制设施；研究锚只影响压力公式
     * - 缓冲单元激活期间再降低 50%
     */
    public static int adjustGrowth(ServerPlayer player, int amount, String reason) {
        return Hk3GazeRules.growth(amount, Hk3GazeManager.isBufferActive(player));
    }
}
