package com.sirin.hk3gtl.mixin.gtceu;

import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine;
import com.sirin.hk3gtl.common.multiblock.build.Hk3BuildState;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 包含指令、活塞等实际方块写入；任一舰体变更立即撤销分批检查证据。 */
@Mixin(Level.class)
public abstract class Hk3HyperionHullChangeMixin {
    @WrapOperation(method="setBlock(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;II)Z",
            at=@At(value="INVOKE",target="Lnet/minecraft/world/level/chunk/LevelChunk;setBlockState(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;Z)Lnet/minecraft/world/level/block/state/BlockState;"))
    private BlockState hk3gtl$hullChange(LevelChunk chunk,BlockPos pos,BlockState state,boolean moving,Operation<BlockState> original) {
        BlockState old=original.call(chunk,pos,state,moving);
        if(old!=null && (Object)this instanceof ServerLevel level && !Hk3BuildState.matches(chunk.getBlockState(pos),old)){
            Hk3HyperionMachine.blockChanged(level,pos);
            if(!(com.sirin.hk3gtl.common.multiblock.pattern.Hk3InterfacePredicates.isClearance(old)
                    &&com.sirin.hk3gtl.common.multiblock.pattern.Hk3InterfacePredicates.isClearance(chunk.getBlockState(pos)))) {
                com.sirin.hk3gtl.common.machine.Hk3CommissionMachine.blockChanged(level,pos);
                com.sirin.hk3gtl.common.machine.w03.Hk3W03Machine.blockChanged(level,pos);
            }
        }
        return old;
    }
    @Inject(method="setBlock(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;II)Z",at=@At("RETURN"))
    private void hk3gtl$changed(BlockPos pos,BlockState state,int flags,int recursion,CallbackInfoReturnable<Boolean> cir) {
        if(cir.getReturnValueZ()&&(Object)this instanceof ServerLevel level){
            com.sirin.hk3gtl.common.farview.Hk3FarViewData.changed(level,pos,level.getBlockState(pos));
        }
    }
}
