package com.sirin.hk3gtl.mixin;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.Level;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Items;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import com.sirin.hk3gtl.common.easter.*;
@Mixin(BeehiveBlock.class)
/** 【变更记录 #1】2026-10-01 06:25:16（修订128）：删除无；新增真实阅读与操作记录；修改无；用途：服务器核对原始条件，失败或模拟不授予。 */
public abstract class Hk3EggHoneyMixin {
    @Inject(method="use",at=@At("HEAD"))private void hk3gtl$before(BlockState state,Level level,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit,CallbackInfoReturnable<InteractionResult> ci){
        if(player instanceof ServerPlayer p)Hk3EggRuntime.state(p).putBoolean("honeyBottleUse",p.getItemInHand(hand).is(Items.GLASS_BOTTLE));
    }
    @Inject(method="use",at=@At("RETURN"))private void hk3gtl$after(BlockState state,Level level,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit,CallbackInfoReturnable<InteractionResult> ci){
        if(!(player instanceof ServerPlayer p))return;var s=Hk3EggRuntime.state(p);boolean bottle=s.getBoolean("honeyBottleUse");s.remove("honeyBottleUse");
        if(!bottle||!ci.getReturnValue().consumesAction()||!state.is(Blocks.BEE_NEST)||state.getValue(BeehiveBlock.HONEY_LEVEL)<5||!level.getBlockState(pos).is(Blocks.BEE_NEST)||level.getBlockState(pos).getValue(BeehiveBlock.HONEY_LEVEL)!=0||!CampfireBlock.isSmokeyPos(level,pos))return;
        for(int y=1;y<=5;y++){var at=pos.below(y);var b=level.getBlockState(at);if(b.getBlock() instanceof CampfireBlock&&b.getValue(CampfireBlock.LIT)&&Hk3EggBuildMemory.get(p.serverLevel()).owns(p,at)){Hk3EggVanilla.caseEvent(p,433);return;}}
    }
}
