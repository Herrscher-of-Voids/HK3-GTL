package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/**
 * 【文件职责】让紧凑巨构判定复用GT匹配上下文的清理与单格更新。
 * 【变更记录 #1】2026-10-26 19:36:08（第1次备注 · 内测5修订177）
 * - 删除：无；新增：两个受保护方法的调用桥；修改：无既有GT判定分支。
 * - 用途：保留真实部件、配方IO和错误定位，不为千万空气格建立对象。
 */
@Mixin(value = MultiblockState.class, remap = false)
public interface Hk3MultiblockStateAccess {
    @Invoker("clean") void hk3gtl$clean();
    @Invoker("update") boolean hk3gtl$update(BlockPos pos, TraceabilityPredicate predicate);
}
