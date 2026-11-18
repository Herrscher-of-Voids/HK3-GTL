package com.sirin.hk3gtl.mixin.gtceu;

import com.sirin.hk3gtl.common.multiblock.loading.Hk3MultiblockLoading;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 实际区块写入刷新分批读取中的证据，包含直接写区块的第三方路径。 */
@Mixin(LevelChunk.class)
public abstract class Hk3PatternChunkChangeMixin {
    @Shadow public abstract Level getLevel();
    @Inject(method="setBlockState",at=@At("RETURN"))
    private void hk3gtl$changed(BlockPos pos,BlockState state,boolean moving,CallbackInfoReturnable<BlockState> callback){
        var old=callback.getReturnValue();
        if(old!=null&&getLevel() instanceof ServerLevel level)Hk3MultiblockLoading.changed(level,pos,old,state);
    }
}
