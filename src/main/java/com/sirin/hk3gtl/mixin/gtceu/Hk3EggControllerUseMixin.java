package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.block.MetaMachineBlock;
import com.sirin.hk3gtl.common.easter.Hk3EggNativeMachineScenes;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 本人直接交互控制器返回成功后核对所用手；远程打开菜单不等价。 */
@Mixin(value = MetaMachineBlock.class, remap = false)
public abstract class Hk3EggControllerUseMixin {
    @Inject(method = "use", at = @At("RETURN"), remap = true)
    private void hk3gtl$used(BlockState block, Level level, BlockPos pos, Player player, InteractionHand hand,
                            BlockHitResult hit, CallbackInfoReturnable<InteractionResult> result) {
        if (player instanceof ServerPlayer serverPlayer && level == serverPlayer.serverLevel())
            Hk3EggNativeMachineScenes.controllerUsed(serverPlayer, pos, hand, result.getReturnValue().consumesAction());
    }
}
