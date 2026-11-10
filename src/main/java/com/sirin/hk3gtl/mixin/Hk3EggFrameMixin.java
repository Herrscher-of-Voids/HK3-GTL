package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.decoration.ItemFrame;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
/** 【变更记录 #1】2026-10-01 04:51:18（修订128）：删除无；新增原生展示框成功装入回调；用途：空框变实物且实际交互成功才计，旋转旧物、失败交互不计。 */
@Mixin(ItemFrame.class)
public abstract class Hk3EggFrameMixin {
    @Unique private boolean hk3gtl$empty;
    @Inject(method="interact",at=@At("HEAD"))private void hk3gtl$before(Player p,InteractionHand hand,CallbackInfoReturnable<InteractionResult> ci){hk3gtl$empty=((ItemFrame)(Object)this).getItem().isEmpty();}
    @Inject(method="interact",at=@At("RETURN"))private void hk3gtl$after(Player p,InteractionHand hand,CallbackInfoReturnable<InteractionResult> ci){var f=(ItemFrame)(Object)this;if(p instanceof ServerPlayer server&&hk3gtl$empty&&!f.getItem().isEmpty()&&ci.getReturnValue().consumesAction())com.sirin.hk3gtl.common.easter.Hk3EggDecor.framed(server,f);hk3gtl$empty=false;}
}
