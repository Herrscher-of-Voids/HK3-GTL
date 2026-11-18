package com.sirin.hk3gtl.mixin.gtceu;

import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionJumpData;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.material.Fluid;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(ServerLevel.class)
public abstract class Hk3HyperionJumpScheduledTickMixin {
    @Inject(method="tickBlock",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$pauseBlock(BlockPos pos,Block block,CallbackInfo ci) {
        var level=(ServerLevel)(Object)this;
        if(Hk3HyperionJumpData.locked(level,pos)) {level.scheduleTick(pos,block,1);ci.cancel();}
    }
    @Inject(method="tickFluid",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$pauseFluid(BlockPos pos,Fluid fluid,CallbackInfo ci) {
        var level=(ServerLevel)(Object)this;
        if(Hk3HyperionJumpData.locked(level,pos)) {level.scheduleTick(pos,fluid,1);ci.cancel();}
    }
}
