package com.sirin.hk3gtl.mixin;
import net.minecraft.world.level.block.NoteBlock;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
/** 【变更记录 #1】2026-10-01 04:55:02（修订128）：删除无；新增原版音符请求、成功调音与实际奏响返回值适配；用途：保留Forge声音取消语义，不将仅右键或红石信号算奏响。 */
@Mixin(NoteBlock.class)
/** 【变更记录 #2】2026-10-01 05:02:11（修订128）：删除：旧固定上限或被替代的分支；新增/修改：调音入口原参数会被原方法重赋值，改存线程局部旧音高；避免客户端和服务器共用Block单例时串计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggNoteBlockMixin {
    @org.spongepowered.asm.mixin.Unique private static final ThreadLocal<Integer> hk3gtl$noteBefore=new ThreadLocal<>();
    @Inject(method="use",at=@At("HEAD"))private void hk3gtl$tuneBefore(BlockState state,Level level,BlockPos pos,Player p,InteractionHand hand,BlockHitResult hit,CallbackInfoReturnable<InteractionResult> ci){hk3gtl$noteBefore.set(state.getValue(NoteBlock.NOTE));}
    @Inject(method="playNote",at=@At("HEAD"))private void hk3gtl$queued(Entity actor,BlockState state,Level level,BlockPos pos,CallbackInfo ci){com.sirin.hk3gtl.common.easter.Hk3EggMusic.queued(actor,state,level,pos);}
    @Inject(method="use",at=@At("RETURN"))private void hk3gtl$tuned(BlockState state,Level level,BlockPos pos,Player p,InteractionHand hand,BlockHitResult hit,CallbackInfoReturnable<InteractionResult> ci){if(p instanceof ServerPlayer server&&ci.getReturnValue().consumesAction()&&level.getBlockState(pos).is(state.getBlock())&&hk3gtl$noteBefore.get()!=null&&hk3gtl$noteBefore.get()!=level.getBlockState(pos).getValue(NoteBlock.NOTE))com.sirin.hk3gtl.common.easter.Hk3EggMusic.tuned(server,pos);hk3gtl$noteBefore.remove();}
    @Inject(method="triggerEvent",at=@At("RETURN"))private void hk3gtl$played(BlockState state,Level level,BlockPos pos,int event,int param,CallbackInfoReturnable<Boolean> ci){com.sirin.hk3gtl.common.easter.Hk3EggMusic.played(state,level,pos,Boolean.TRUE.equals(ci.getReturnValue()));}
}
