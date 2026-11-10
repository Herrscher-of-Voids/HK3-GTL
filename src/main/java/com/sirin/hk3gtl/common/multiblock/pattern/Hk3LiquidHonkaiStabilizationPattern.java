package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;

/**
 * 液态崩坏能稳定塔的历史入口兼容层。
 *
 * <p>正式结构由第一条工业线统一布局管理；保留旧类名是为了避免旧存档或
 * 外部扩展在编译期失去入口，同时禁止旧的低阶机壳 Pattern 再被调用。</p>
 */
@Deprecated(forRemoval = false)
public final class Hk3LiquidHonkaiStabilizationPattern {
    private Hk3LiquidHonkaiStabilizationPattern() {}

    /** 返回 I04 的正式 MAX 稳定塔布局。 */
    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return Hk3LiquidLinePatterns.create(definition, Hk3LiquidLineLayout.Kind.STABILIZATION);
    }
}
