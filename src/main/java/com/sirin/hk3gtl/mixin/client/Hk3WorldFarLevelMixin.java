package com.sirin.hk3gtl.mixin.client;

import com.sirin.hk3gtl.client.farview.Hk3WorldFarCapture;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;

/** 单块与多块网络更新同样重读真实分区；卸载仅撤销未完成采样。 */
@Mixin(ClientLevel.class)
public abstract class Hk3WorldFarLevelMixin {
    @Inject(method="setServerVerifiedBlockState",at=@At("RETURN"))
    private void hk3gtl$serverChange(BlockPos pos,BlockState state,int flags,CallbackInfo callback){
        Hk3WorldFarCapture.changed((ClientLevel)(Object)this,pos);
    }
    @Inject(method="setBlock(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;II)Z",at=@At("RETURN"))
    private void hk3gtl$localChange(BlockPos pos,BlockState state,int flags,int recursion,CallbackInfoReturnable<Boolean> callback){
        if(callback.getReturnValueZ())Hk3WorldFarCapture.changed((ClientLevel)(Object)this,pos);
    }
    @Inject(method="unload",at=@At("HEAD"))
    private void hk3gtl$unload(LevelChunk chunk,CallbackInfo callback){
        Hk3WorldFarCapture.unloaded((ClientLevel)(Object)this,chunk);
    }
}
