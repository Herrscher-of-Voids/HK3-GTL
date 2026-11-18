package com.sirin.hk3gtl.mixin.stargate;

import com.sirin.hk3gtl.common.compat.stargate.Hk3StargateQuestEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.povstalec.sgjourney.common.blocks.stargate.ClassicStargateBaseBlock;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = ClassicStargateBaseBlock.class, remap = false)
public abstract class Hk3ClassicStargateActivationMixin {
    @Inject(method = "use", at = @At("RETURN"), remap = true)
    private void hk3gtl$activated(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit,
                                 CallbackInfoReturnable<InteractionResult> result) {
        if (player instanceof ServerPlayer serverPlayer && result.getReturnValue().consumesAction())
            Hk3StargateQuestEvents.activated(serverPlayer, pos);
    }
}
