package com.sirin.hk3gtl.mixin.height;

import net.minecraft.world.level.dimension.DimensionType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * 【文件职责】仅供已冻结世界合同在Level创建前修改该注册表实例物理高度。
 * 【变更记录 #1】2026-10-17 21:19:41（第1次备注 · 修订166）
 * - 删除：无。新增：height字段受控写入入口；修改：不注入DimensionType构造器。
 * - 用途：保留注册对象身份、minY、逻辑高度与原生同步编码，不触碰无合同旧世界。
 */
@Mixin(DimensionType.class)
public interface Hk3DimensionTypeHeightAccessor {
    @Mutable
    @Accessor("height")
    void hk3gtl$setPhysicalHeight(int height);
}
