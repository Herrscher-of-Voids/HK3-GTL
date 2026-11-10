package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;

/**
 * 稳定介质再生塔的历史入口兼容层。
 *
 * <p>旧实现使用基础机壳与原版装饰方块，和 MAX 工业线的材料契约不一致；
 * 现在统一转发到正式再生塔布局。</p>
 */
@Deprecated(forRemoval = false)
public final class Hk3StabilizationMediumRegenerationPattern {
    private Hk3StabilizationMediumRegenerationPattern() {}

    /** 返回 I05 的正式 MAX 再生塔布局。 */
    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return Hk3LiquidLinePatterns.create(definition, Hk3LiquidLineLayout.Kind.REGENERATION);
    }
}
