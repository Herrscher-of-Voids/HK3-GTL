package com.sirin.hk3gtl.mixin.gtmthings;
import com.hepdd.gtmthings.common.cover.WirelessTransferCover;
import com.gregtechceu.gtceu.api.cover.CoverBehavior;
import com.lowdragmc.lowdraglib.side.item.*;
import com.lowdragmc.lowdraglib.side.fluid.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.core.*;
import com.sirin.hk3gtl.common.easter.*;
import java.util.function.Predicate;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=WirelessTransferCover.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:15:25（修订128）：删除无；新增实际传输返回后的归属旁注；修改无；用途：模拟/零接收不算交付，不修改传输函数。 */
public abstract class Hk3EggWirelessCoverMixin {
    @Inject(method="onAttached",at=@At("RETURN"))private void hk3gtl$attached(ItemStack stack,ServerPlayer p,CallbackInfo ci){Hk3EggCovers.attached((CoverBehavior)(Object)this,p);}
    @Redirect(method="update",at=@At(value="INVOKE",target="Lcom/lowdragmc/lowdraglib/side/item/ItemTransferHelper;exportToTarget(Lcom/lowdragmc/lowdraglib/side/item/IItemTransfer;ILjava/util/function/Predicate;Lnet/minecraft/world/level/Level;Lnet/minecraft/core/BlockPos;Lnet/minecraft/core/Direction;)V"))
    private void hk3gtl$items(IItemTransfer source,int max,Predicate<ItemStack> filter,Level level,BlockPos pos,Direction side){
        long before=Hk3EggCovers.itemCount(source);ItemTransferHelper.exportToTarget(source,max,filter,level,pos,side);
        if(before>=0&&Hk3EggCovers.itemCount(source)<before)Hk3EggCovers.delivered((CoverBehavior)(Object)this,271);
    }
    @Redirect(method="update",at=@At(value="INVOKE",target="Lcom/lowdragmc/lowdraglib/side/fluid/FluidTransferHelper;exportToTarget(Lcom/lowdragmc/lowdraglib/side/fluid/IFluidTransfer;ILjava/util/function/Predicate;Lnet/minecraft/world/level/Level;Lnet/minecraft/core/BlockPos;Lnet/minecraft/core/Direction;)V"))
    private void hk3gtl$fluids(IFluidTransfer source,int max,Predicate<FluidStack> filter,Level level,BlockPos pos,Direction side){
        Hk3EggFluidCapture.begin((CoverBehavior)(Object)this,272);
        try{FluidTransferHelper.exportToTarget(source,max,filter,level,pos,side);}finally{Hk3EggFluidCapture.end();}
    }
}
