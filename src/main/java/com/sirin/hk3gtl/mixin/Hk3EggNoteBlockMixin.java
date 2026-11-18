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
 
@Mixin(NoteBlock.class)
 
public abstract class Hk3EggNoteBlockMixin {
    @org.spongepowered.asm.mixin.Unique private static final ThreadLocal<Integer> hk3gtl$noteBefore=new ThreadLocal<>();
    @Inject(method="use",at=@At("HEAD"))private void hk3gtl$tuneBefore(BlockState state,Level level,BlockPos pos,Player p,InteractionHand hand,BlockHitResult hit,CallbackInfoReturnable<InteractionResult> ci){hk3gtl$noteBefore.set(state.getValue(NoteBlock.NOTE));}
    @Inject(method="playNote",at=@At("HEAD"))private void hk3gtl$queued(Entity actor,BlockState state,Level level,BlockPos pos,CallbackInfo ci){com.sirin.hk3gtl.common.easter.Hk3EggMusic.queued(actor,state,level,pos);}
    @Inject(method="use",at=@At("RETURN"))private void hk3gtl$tuned(BlockState state,Level level,BlockPos pos,Player p,InteractionHand hand,BlockHitResult hit,CallbackInfoReturnable<InteractionResult> ci){if(p instanceof ServerPlayer server&&ci.getReturnValue().consumesAction()&&level.getBlockState(pos).is(state.getBlock())&&hk3gtl$noteBefore.get()!=null&&hk3gtl$noteBefore.get()!=level.getBlockState(pos).getValue(NoteBlock.NOTE))com.sirin.hk3gtl.common.easter.Hk3EggMusic.tuned(server,pos);hk3gtl$noteBefore.remove();}
    @Inject(method="triggerEvent",at=@At("RETURN"))private void hk3gtl$played(BlockState state,Level level,BlockPos pos,int event,int param,CallbackInfoReturnable<Boolean> ci){com.sirin.hk3gtl.common.easter.Hk3EggMusic.played(state,level,pos,Boolean.TRUE.equals(ci.getReturnValue()));}
}
