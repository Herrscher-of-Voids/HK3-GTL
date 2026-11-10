package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;

/**
 * I03 分馏中心的历史入口兼容层。
 *
 * <p>旧版本这里生成的是使用 GTCEu 基础机壳的独立 Pattern，容易让 MAX 阶段
 * 重新落回低阶结构。正式注册已经统一使用 {@link Hk3LiquidLinePatterns}，
 * 因此保留类名和方法签名，但把旧入口转发到同一份 MAX 逐格布局。</p>
 */
@Deprecated(forRemoval = false)
public final class Hk3I03LiquidFractionationPattern {
    private Hk3I03LiquidFractionationPattern() {}

    /** 返回 I03 的正式 MAX 分馏布局，保证历史调用者不会重新启用旧低阶材料。 */
    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return Hk3LiquidLinePatterns.create(definition, Hk3LiquidLineLayout.Kind.SEPARATION);
    }
}
