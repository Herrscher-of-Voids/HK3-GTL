package com.sirin.hk3gtl.mixin.gtlcore;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

import java.math.BigInteger;

@Mixin(targets = "org.gtlcore.gtlcore.integration.ae2.graph.GraphPlanSummary$Group", remap = false)
public interface Hk3GraphPlanGroupAccess {
    @Accessor("missing") BigInteger hk3gtl$missing();
    @Accessor("stored") BigInteger hk3gtl$stored();
    @Accessor("crafted") BigInteger hk3gtl$crafted();
    @Accessor("runs") BigInteger hk3gtl$runs();
}
