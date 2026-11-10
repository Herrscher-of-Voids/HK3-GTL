package com.sirin.hk3gtl.mixin;
import com.sirin.hk3gtl.common.easter.Hk3EggVanilla;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
/** 【变更记录 #1】2026-10-01 04:15:05（修订128）：删除无；新增放置实际成功后的只读事实；修改无；用途：取消放置不计数，使用位置方块而不是放置后手持物。 */
@Mixin(BlockItem.class)
/** 【变更记录 #2】2026-10-01 04:21:47（修订128）：删除：旧固定上限或被替代的分支；新增/修改：将放置观察排到Forge放置取消/回滚处理之后；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggBlockItemMixin {
    @Unique private final ThreadLocal<BlockState> hk3gtl$before= new ThreadLocal<>();
    @Inject(method="place",at=@At("HEAD"))
    private void hk3gtl$before(BlockPlaceContext c,CallbackInfoReturnable<InteractionResult> ci){if(c.getPlayer() instanceof ServerPlayer)hk3gtl$before.set(c.getLevel().getBlockState(c.getClickedPos()));}
    @Inject(method="place",at=@At("RETURN"))
    private void hk3gtl$after(BlockPlaceContext c,CallbackInfoReturnable<InteractionResult> ci){
        var before=hk3gtl$before.get();hk3gtl$before.remove();
        if(before!=null&&c.getPlayer() instanceof ServerPlayer p&&ci.getReturnValue().consumesAction())Hk3EggVanilla.queuePlacement(p,c.getClickedPos(),before,c.getLevel().getBlockState(c.getClickedPos()));
    }
}
