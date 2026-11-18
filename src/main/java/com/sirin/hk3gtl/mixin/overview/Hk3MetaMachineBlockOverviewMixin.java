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
 * 从实际玩家放置和真实方块替换接入GT机器索引，不把区块卸载当拆除。
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
