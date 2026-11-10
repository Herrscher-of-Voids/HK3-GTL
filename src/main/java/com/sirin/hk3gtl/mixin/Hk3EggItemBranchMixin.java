package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.common.blockentity.ItemPipeBlockEntity;
import com.gregtechceu.gtceu.common.pipelike.item.*;
import net.minecraft.core.Direction;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=ItemNetHandler.class,remap=false)
/** 【变更记录 #1】2026-10-01 13:36:23（修订128）：删除：无；新增/修改：GT物品网具体路线真实插入前后差额旁注，模拟传输不建立新分支凭据；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggItemBranchMixin {
    @Shadow private ItemPipeNet net;
    @Shadow private ItemPipeBlockEntity pipe;
    @Shadow @Final private Direction facing;
    @Unique private int hk3gtl$count;
    @Unique private ItemStack hk3gtl$input=ItemStack.EMPTY;
    @Inject(method="insert(Lcom/gregtechceu/gtceu/common/pipelike/item/ItemRoutePath;Lnet/minecraft/world/item/ItemStack;ZZ)Lnet/minecraft/world/item/ItemStack;",at=@At("HEAD"))private void hk3gtl$before(ItemRoutePath route,ItemStack item,boolean simulate,boolean ignoreLimit,CallbackInfoReturnable<ItemStack> ci){hk3gtl$count=item.getCount();hk3gtl$input=item.copy();}
    @Inject(method="insert(Lcom/gregtechceu/gtceu/common/pipelike/item/ItemRoutePath;Lnet/minecraft/world/item/ItemStack;ZZ)Lnet/minecraft/world/item/ItemStack;",at=@At("RETURN"))private void hk3gtl$after(ItemRoutePath route,ItemStack item,boolean simulate,boolean ignoreLimit,CallbackInfoReturnable<ItemStack> ci){com.sirin.hk3gtl.common.easter.Hk3EggLineBranch.delivered(net,pipe,facing,route,hk3gtl$input,hk3gtl$count,ci.getReturnValue().getCount(),simulate);hk3gtl$input=ItemStack.EMPTY;}
}
