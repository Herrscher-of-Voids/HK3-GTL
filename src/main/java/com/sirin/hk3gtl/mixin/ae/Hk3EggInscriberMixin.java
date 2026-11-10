package com.sirin.hk3gtl.mixin.ae;
import appeng.blockentity.misc.InscriberBlockEntity;
import appeng.api.networking.IGridNode;
import appeng.api.networking.ticking.TickRateModulation;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
/** 【变更记录 #1】2026-10-01 04:45:29（修订128）：删除无；新增压印完成时输入槽真实消耗确认；用途：成功输出并扣除输入后才记账，自动导出不使回执丢失，模拟分支无输入消耗不计。 */
@Mixin(value=InscriberBlockEntity.class,remap=false)
public abstract class Hk3EggInscriberMixin {
    @Shadow private int finalStep;
    @Unique private ItemStack hk3gtl$input=ItemStack.EMPTY,hk3gtl$output=ItemStack.EMPTY;
    @Inject(method="tickingRequest",at=@At("HEAD"),remap=false)
    private void hk3gtl$before(IGridNode node,int elapsed,CallbackInfoReturnable<TickRateModulation> cir){
        hk3gtl$input=ItemStack.EMPTY;hk3gtl$output=ItemStack.EMPTY;
        var machine=(InscriberBlockEntity)(Object)this;
        if(machine.isSmash()&&finalStep==7&&machine.getTask()!=null){hk3gtl$input=machine.getInternalInventory().getStackInSlot(2).copy();hk3gtl$output=machine.getTask().getResultItem().copy();}
    }
    @Inject(method="tickingRequest",at=@At("RETURN"),remap=false)
    private void hk3gtl$after(IGridNode node,int elapsed,CallbackInfoReturnable<TickRateModulation> cir){
        var machine=(InscriberBlockEntity)(Object)this;var after=machine.getInternalInventory().getStackInSlot(2);
        if(!hk3gtl$input.isEmpty()&&hk3gtl$input.getCount()==after.getCount()+1&&(after.isEmpty()||ItemStack.isSameItemSameTags(hk3gtl$input,after)))com.sirin.hk3gtl.common.easter.Hk3EggAe.inscribed(machine,hk3gtl$input,hk3gtl$output);
        hk3gtl$input=ItemStack.EMPTY;hk3gtl$output=ItemStack.EMPTY;
    }
}
