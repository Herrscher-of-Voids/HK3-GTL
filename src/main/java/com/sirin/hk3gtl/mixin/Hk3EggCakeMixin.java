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
/** 【变更记录 #1】2026-10-01 04:51:18（修订128）：删除无；新增蛋糕实际吃片返回成功回调；用途：仅本人放置的蛋糕，饱食无法食用不计。 */
@Mixin(CakeBlock.class)
public abstract class Hk3EggCakeMixin {
    @Inject(method="eat",at=@At("RETURN"))private static void hk3gtl$ate(LevelAccessor level,BlockPos pos,BlockState state,Player p,CallbackInfoReturnable<InteractionResult> ci){if(p instanceof ServerPlayer server&&ci.getReturnValue().consumesAction())com.sirin.hk3gtl.common.easter.Hk3EggDecor.ateCake(server,pos);}
}
