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
