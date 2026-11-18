package com.sirin.hk3gtl.mixin.height;

import net.minecraft.world.level.dimension.DimensionType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * 仅供已冻结世界合同在Level创建前修改该注册表实例物理高度。
 */
@Mixin(DimensionType.class)
public interface Hk3DimensionTypeHeightAccessor {
    @Mutable
    @Accessor("height")
    void hk3gtl$setPhysicalHeight(int height);
}
