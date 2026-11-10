package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** 小型固定Pattern沿用原接口谓词；不从预览候选猜测可拆仓室。 */
@Mixin(value = BlockPattern.class, remap = false)
public interface Hk3BuildPatternAccess {
    @Accessor("blockMatches") TraceabilityPredicate[][][] hk3gtl$blockMatches();
}
