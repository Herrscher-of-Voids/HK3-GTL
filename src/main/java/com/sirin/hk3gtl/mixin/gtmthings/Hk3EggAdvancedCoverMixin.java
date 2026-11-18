package com.sirin.hk3gtl.mixin.gtmthings;
import com.hepdd.gtmthings.common.cover.AdvancedWirelessTransferCover;
import com.gregtechceu.gtceu.api.cover.CoverBehavior;
import com.lowdragmc.lowdraglib.side.item.*;
import com.lowdragmc.lowdraglib.side.fluid.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.server.level.ServerPlayer;
import java.util.function.Predicate;
import com.sirin.hk3gtl.common.easter.*;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=AdvancedWirelessTransferCover.class,remap=false)
public abstract class Hk3EggAdvancedCoverMixin {
    @Redirect(method="moveInventoryItems",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/api/cover/filter/ItemFilter;test(Ljava/lang/Object;)Z"))
    private boolean hk3gtl$whitelist(com.gregtechceu.gtceu.api.cover.filter.ItemFilter filter,Object candidate){
        boolean accepted=filter.test((ItemStack)candidate);
        if(!accepted&&!filter.isBlackList()&&((AdvancedWirelessTransferCover)(Object)this).getFilterHandlerItem().isFilterPresent())Hk3EggCovers.whitelistRejected((CoverBehavior)(Object)this);
        return accepted;
    }
    @Inject(method="onAttached",at=@At("RETURN"))private void hk3gtl$attached(ItemStack stack,ServerPlayer p,CallbackInfo ci){Hk3EggCovers.attached((CoverBehavior)(Object)this,p);Hk3EggCovers.target((CoverBehavior)(Object)this,p,stack);}
    @Redirect(method="moveInventoryItems",at=@At(value="INVOKE",target="Lcom/lowdragmc/lowdraglib/side/item/ItemTransferHelper;insertItem(Lcom/lowdragmc/lowdraglib/side/item/IItemTransfer;Lnet/minecraft/world/item/ItemStack;Z)Lnet/minecraft/world/item/ItemStack;"))
    private ItemStack hk3gtl$insert(IItemTransfer target,ItemStack stack,boolean simulate){
        int count=stack.getCount();var remaining=ItemTransferHelper.insertItem(target,stack,simulate);
        if(!simulate&&remaining.getCount()<count&&!((AdvancedWirelessTransferCover)(Object)this).getFilterHandlerItem().getFilterItem().isEmpty())Hk3EggCovers.delivered((CoverBehavior)(Object)this,273);
        if(!simulate&&remaining.getCount()<count)Hk3EggCovers.targetDelivered((CoverBehavior)(Object)this);
        return remaining;
    }
    @Redirect(method="transferAny",at=@At(value="INVOKE",target="Lcom/lowdragmc/lowdraglib/side/fluid/FluidTransferHelper;transferFluids(Lcom/lowdragmc/lowdraglib/side/fluid/IFluidTransfer;Lcom/lowdragmc/lowdraglib/side/fluid/IFluidTransfer;JLjava/util/function/Predicate;)J"))
    private long hk3gtl$transfer(IFluidTransfer source,IFluidTransfer target,long max,Predicate<FluidStack> filter){long actual=FluidTransferHelper.transferFluids(source,target,max,filter);if(actual>0)Hk3EggCovers.delivered((CoverBehavior)(Object)this,274);return actual;}
}
