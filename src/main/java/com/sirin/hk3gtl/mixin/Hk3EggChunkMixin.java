package com.sirin.hk3gtl.mixin;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(LevelChunk.class)
 
 
public abstract class Hk3EggChunkMixin {
    @Inject(method="setBlockState",at=@At("RETURN"))
    private void hk3gtl$changed(BlockPos pos,BlockState state,boolean moved,CallbackInfoReturnable<BlockState> cir){
        var old=cir.getReturnValue();if(old==null||old.getBlock()==state.getBlock())return;
        var level=((LevelChunk)(Object)this).getLevel();
        if(level instanceof ServerLevel server&&server.getServer().isSameThread()){com.sirin.hk3gtl.common.easter.Hk3EggObsidian.changed(server,pos,old,state);com.sirin.hk3gtl.common.easter.Hk3EggBuildMemory.get(server).changed(pos);}
    }
}
