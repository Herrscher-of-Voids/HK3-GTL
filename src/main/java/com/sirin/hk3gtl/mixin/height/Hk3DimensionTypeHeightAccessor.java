package com.sirin.hk3gtl.mixin.height;

import net.minecraft.world.level.dimension.DimensionType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.gen.Accessor;







@Mixin(DimensionType.class)
public interface Hk3DimensionTypeHeightAccessor {
    @Mutable
    @Accessor("height")
    void hk3gtl$setPhysicalHeight(int height);
}
