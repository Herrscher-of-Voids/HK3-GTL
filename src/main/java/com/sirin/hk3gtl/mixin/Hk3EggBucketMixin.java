package com.sirin.hk3gtl.mixin;
import net.minecraft.world.item.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.InteractionHand;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(BucketItem.class)
/** 【变更记录 #1】2026-10-01 05:28:18（修订128）：删除无；新增桶真实收水返回后的节日日历观察；修改无；用途：只读真实事件，保留取消结果，不授正式资格。 */
/** 【变更记录 #2】2026-10-01 06:23:20（修订128）：删除：无；新增/修改：只在水桶实际放水成功且源方块存在时记录同日耕作，地狱蒸发不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 12:32:24（修订128）：删除：无；新增/修改：真实放水成功后记录源方块归属，供挖脚下安全落水检测使用；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggBucketMixin {
    @Inject(method="checkExtraContent",at=@At("RETURN"))private void hk3gtl$water(Player player,Level level,ItemStack bucket,BlockPos pos,org.spongepowered.asm.mixin.injection.callback.CallbackInfo ci){
        if(player instanceof ServerPlayer p&&bucket.is(Items.WATER_BUCKET)&&level.getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER)&&level.getFluidState(pos).isSource()){com.sirin.hk3gtl.common.easter.Hk3EggPersonalScenes.farming(p,"water");com.sirin.hk3gtl.common.easter.Hk3EggWaterFall.placed(p,pos);}
    }

    @Redirect(method="use",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/block/BucketPickup;pickupBlock(Lnet/minecraft/world/level/LevelAccessor;Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;)Lnet/minecraft/world/item/ItemStack;"))
    private ItemStack hk3gtl$pickup(BucketPickup pickup,LevelAccessor access,BlockPos pos,BlockState state,Level level,Player player,InteractionHand hand){
        var result=pickup.pickupBlock(access,pos,state);
        if(player instanceof ServerPlayer p&&result.is(Items.WATER_BUCKET)&&state.getFluidState().isSource()&&state.getFluidState().is(net.minecraft.tags.FluidTags.WATER)){
            var date=com.sirin.hk3gtl.common.easter.Hk3EggCalendar.now();if(date.getMonthValue()==3&&date.getDayOfMonth()==22)com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,347);
        }return result;
    }
}
