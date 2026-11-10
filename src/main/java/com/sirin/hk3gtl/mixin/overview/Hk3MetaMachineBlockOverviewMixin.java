package com.sirin.hk3gtl.mixin.overview;

import com.gregtechceu.gtceu.api.block.MetaMachineBlock;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewHooks;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 【文件职责】从实际玩家放置和真实方块替换接入GT机器索引，不把区块卸载当拆除。
 * 【变更记录 #1】2026-10-19 02:07:23（第1次备注 · 修订171）
 * 删除：无。新增：setPlacedBy返回登记与onRemove移除BE前注销。
 * 修改：无；只处理已加载ServerLevel，状态/朝向变更不会删除。用途：使用真实放置者，不附近认领旧机器。
 */
/**
 * 【变更记录 #2】2026-10-19 02:13:10（第2次备注 · 修订171）
 * 删除：继承自原版的两个方法沿GT自定义方法不映射的假定。
 * 新增：无；修改：两个注入点单独启用原版方法映射，实际生产包签名为m_6402_与m_6810_。
 * 用途：GT目标类本身不改名，但其原版覆盖方法必须经refmap映射，避免只在开发环境有效。
 */
@Mixin(value = MetaMachineBlock.class, remap = false)
public abstract class Hk3MetaMachineBlockOverviewMixin {
    @Inject(method = "setPlacedBy", at = @At("RETURN"), remap = true)
    private void hk3gtl$overviewPlaced(Level level, BlockPos pos, BlockState state, LivingEntity placer, ItemStack stack, CallbackInfo ci) {
        if (level instanceof ServerLevel && placer instanceof ServerPlayer actor && level.hasChunkAt(pos))
            Hk3MachineOverviewHooks.placed(MetaMachine.getMachine(level, pos), actor);
    }

    @Inject(method = "onRemove", at = @At("HEAD"), remap = true)
    private void hk3gtl$overviewRemoved(BlockState state, Level level, BlockPos pos, BlockState replacement, boolean moving, CallbackInfo ci) {
        if (level instanceof ServerLevel && !state.is(replacement.getBlock()) && level.hasChunkAt(pos))
            Hk3MachineOverviewHooks.removed(MetaMachine.getMachine(level, pos));
    }
}
