package com.sirin.hk3gtl.mixin;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(LevelChunk.class)
/** 【变更记录 #1】2026-10-01 05:41:36（修订128）：删除无；新增方块成功替换时撤销归属，覆盖破坏、爆炸、活塞与他人替换；修改无；用途：只读当前已加载建筑，不生成结构或授予工程验收。 */
/** 【变更记录 #2】2026-10-01 13:29:18（修订128）：删除：无；新增/修改：源熔岩确变黑曜石后排入只读回执队列，仍先撤销旧方块归属；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggChunkMixin {
    @Inject(method="setBlockState",at=@At("RETURN"))
    private void hk3gtl$changed(BlockPos pos,BlockState state,boolean moved,CallbackInfoReturnable<BlockState> cir){
        var old=cir.getReturnValue();if(old==null||old.getBlock()==state.getBlock())return;
        var level=((LevelChunk)(Object)this).getLevel();
        if(level instanceof ServerLevel server&&server.getServer().isSameThread()){com.sirin.hk3gtl.common.easter.Hk3EggObsidian.changed(server,pos,old,state);com.sirin.hk3gtl.common.easter.Hk3EggBuildMemory.get(server).changed(pos);}
    }
}
