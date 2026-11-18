package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3NativeWonderCheck;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3WonderPositionSet;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Collection;

@Mixin(value=MultiblockState.class,remap=false)
public abstract class Hk3NativeWonderStateMixin {
    @Inject(method="clean",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$resume(CallbackInfo callback){
        var check=Hk3NativeWonderCheck.current();
        if(check!=null&&check.started())callback.cancel();
    }
    @Inject(method="clean",at=@At("RETURN"))
    private void hk3gtl$initialize(CallbackInfo callback){
        var check=Hk3NativeWonderCheck.current();
        if(check!=null&&!check.started())check.initialize((MultiblockState)(Object)this);
    }
    @Inject(method="addPosCache",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$compress(BlockPos pos,CallbackInfo callback){
        var check=Hk3NativeWonderCheck.current();
        if(check!=null){check.cache(pos,(MultiblockState)(Object)this);callback.cancel();}
    }
    @Inject(method="isPosInCache",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$contains(BlockPos pos,CallbackInfoReturnable<Boolean> callback){
        var state=(MultiblockState)(Object)this;
        Hk3WonderPositionSet positions=state.getMatchContext().get(Hk3NativeWonderCheck.POSITIONS);
        if(positions!=null)callback.setReturnValue(positions.contains(pos));
    }
    @Inject(method="getCache",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$chunks(CallbackInfoReturnable<Collection<BlockPos>> callback){
        var state=(MultiblockState)(Object)this;
        Hk3NativeWonderCheck check=state.getMatchContext().get(Hk3NativeWonderCheck.CHECK);
        if(check!=null)callback.setReturnValue(check.chunkRepresentatives());
    }
}
