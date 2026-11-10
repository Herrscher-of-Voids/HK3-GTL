package com.sirin.hk3gtl.mixin;
import com.sirin.hk3gtl.common.easter.Hk3EggVanilla;
import net.minecraft.server.level.*;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
/** 【变更记录 #1】2026-10-01 04:15:05（修订128）：删除无；新增成功采掘结果观察；修改无；用途：保护插件拒绝、权限不足和预测破坏不产生记录。 */
@Mixin(ServerPlayerGameMode.class)
/** 【变更记录 #2】2026-10-01 13:29:18（修订128）：删除：无；新增/修改：采掘开始读取本人生成黑曜石凭据，实际成功破坏后授予，取消或重放普通黑曜石不算；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggMiningMixin {
    @Shadow @Final protected ServerPlayer player;
    @Unique private BlockState hk3gtl$old;
    @Unique private boolean hk3gtl$madeObsidian;
    @Inject(method="destroyBlock",at=@At("HEAD"))private void hk3gtl$before(BlockPos pos,CallbackInfoReturnable<Boolean> ci){hk3gtl$old=player.level().getBlockState(pos);hk3gtl$madeObsidian=hk3gtl$old.is(net.minecraft.world.level.block.Blocks.OBSIDIAN)&&com.sirin.hk3gtl.common.easter.Hk3EggBuildMemory.get(player.serverLevel()).madeObsidian(player,pos);}
    @Inject(method="destroyBlock",at=@At("RETURN"))private void hk3gtl$after(BlockPos pos,CallbackInfoReturnable<Boolean> ci){
        if(Boolean.TRUE.equals(ci.getReturnValue())&&hk3gtl$old!=null){Hk3EggVanilla.broken(player,pos,hk3gtl$old);if(hk3gtl$madeObsidian&&!player.isCreative())Hk3EggVanilla.caseEvent(player,446);}hk3gtl$madeObsidian=false;hk3gtl$old=null;
    }
}
