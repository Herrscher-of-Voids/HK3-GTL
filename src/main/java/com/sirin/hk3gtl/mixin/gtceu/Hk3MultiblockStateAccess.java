package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

 





@Mixin(value = MultiblockState.class, remap = false)
public interface Hk3MultiblockStateAccess {
    @Invoker("clean") void hk3gtl$clean();
    @Invoker("update") boolean hk3gtl$update(BlockPos pos, TraceabilityPredicate predicate);
}
