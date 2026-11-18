package com.sirin.hk3gtl.mixin;
import net.minecraft.world.level.block.CakeBlock;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(CakeBlock.class)
public abstract class Hk3EggCakeMixin {
    @Inject(method="eat",at=@At("RETURN"))private static void hk3gtl$ate(LevelAccessor level,BlockPos pos,BlockState state,Player p,CallbackInfoReturnable<InteractionResult> ci){if(p instanceof ServerPlayer server&&ci.getReturnValue().consumesAction())com.sirin.hk3gtl.common.easter.Hk3EggDecor.ateCake(server,pos);}
}
