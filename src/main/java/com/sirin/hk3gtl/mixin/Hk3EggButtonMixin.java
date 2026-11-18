package com.sirin.hk3gtl.mixin;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.Level;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(ButtonBlock.class)
 
public abstract class Hk3EggButtonMixin {
    @Inject(method="use",at=@At("RETURN"))private void hk3gtl$press(BlockState state,Level level,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit,CallbackInfoReturnable<InteractionResult> ci){if(player instanceof ServerPlayer p&&ci.getReturnValue().consumesAction()&&!state.getValue(ButtonBlock.POWERED)&&level.getBlockState(pos).getBlock() instanceof ButtonBlock&&level.getBlockState(pos).getValue(ButtonBlock.POWERED))com.sirin.hk3gtl.common.easter.Hk3EggDispenser.button(p,pos);}
}
