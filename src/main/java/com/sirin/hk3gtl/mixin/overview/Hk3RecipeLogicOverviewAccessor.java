package com.sirin.hk3gtl.mixin.overview;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * 【文件职责】只读取GT实际保存的等待原因，不用等待标记笼统猜测缺电。
 * 【变更记录 #1】2026-10-19 02:07:23（第1次备注 · 修订171）
 * 删除：无。新增：1.4.4 waitingReason只读访问器；修改无；用途：总览准确区分电能、物料及无法分类的等待。
 */
@Mixin(value = RecipeLogic.class, remap = false)
public interface Hk3RecipeLogicOverviewAccessor {
    @Accessor("waitingReason") Component hk3gtl$waitingReason();
}
