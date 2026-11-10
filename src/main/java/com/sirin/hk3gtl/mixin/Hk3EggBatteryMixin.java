package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.api.item.capability.ElectricItem;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=ElectricItem.class,remap=false)
/** 【变更记录 #1】2026-10-01 12:16:23（修订128）：删除：无；新增/修改：仅实际非模拟charge返回正数产生电池回执，预览不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggBatteryMixin {
    @Shadow @Final protected ItemStack itemStack;
    @Inject(method="charge",at=@At("RETURN"))private void hk3gtl$charge(long amount,int tier,boolean ignore,boolean simulate,CallbackInfoReturnable<Long> ci){com.sirin.hk3gtl.common.easter.Hk3EggTools.charged(itemStack,ci.getReturnValue(),simulate);}
}
