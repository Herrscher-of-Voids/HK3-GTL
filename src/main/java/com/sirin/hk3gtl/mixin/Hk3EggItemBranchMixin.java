package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.common.blockentity.ItemPipeBlockEntity;
import com.gregtechceu.gtceu.common.pipelike.item.*;
import net.minecraft.core.Direction;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=ItemNetHandler.class,remap=false)
public abstract class Hk3EggItemBranchMixin {
    @Shadow private ItemPipeNet net;
    @Shadow private ItemPipeBlockEntity pipe;
    @Shadow @Final private Direction facing;
    @Unique private int hk3gtl$count;
    @Unique private ItemStack hk3gtl$input=ItemStack.EMPTY;
    @Inject(method="insert(Lcom/gregtechceu/gtceu/common/pipelike/item/ItemRoutePath;Lnet/minecraft/world/item/ItemStack;ZZ)Lnet/minecraft/world/item/ItemStack;",at=@At("HEAD"))private void hk3gtl$before(ItemRoutePath route,ItemStack item,boolean simulate,boolean ignoreLimit,CallbackInfoReturnable<ItemStack> ci){hk3gtl$count=item.getCount();hk3gtl$input=item.copy();}
    @Inject(method="insert(Lcom/gregtechceu/gtceu/common/pipelike/item/ItemRoutePath;Lnet/minecraft/world/item/ItemStack;ZZ)Lnet/minecraft/world/item/ItemStack;",at=@At("RETURN"))private void hk3gtl$after(ItemRoutePath route,ItemStack item,boolean simulate,boolean ignoreLimit,CallbackInfoReturnable<ItemStack> ci){com.sirin.hk3gtl.common.easter.Hk3EggLineBranch.delivered(net,pipe,facing,route,hk3gtl$input,hk3gtl$count,ci.getReturnValue().getCount(),simulate);hk3gtl$input=ItemStack.EMPTY;}
}
