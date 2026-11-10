package com.sirin.hk3gtl.mixin.gtmthings;
import com.lowdragmc.lowdraglib.side.fluid.*;
import java.util.function.Predicate;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=FluidTransferHelper.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:15:25（修订128）：删除无；新增实际传输返回后的归属旁注；修改无；用途：模拟/零接收不算交付，不修改传输函数。 */
/** 【变更记录 #2】2026-10-01 12:33:29（修订128）：删除：无；新增/修改：保存实际传输前的满容量状态，与返回实际量配对，不改传输原行为；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 13:40:41（修订128）：删除：无；新增/修改：移除全局传输布尔栈，满载观测仅属于受控覆盖板上下文；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggFluidTransferMixin {
    @Inject(method="transferFluids",at=@At("HEAD"))private static void hk3gtl$before(IFluidTransfer a,IFluidTransfer b,long max,Predicate<FluidStack> filter,CallbackInfoReturnable<Long> ci){com.sirin.hk3gtl.common.easter.Hk3EggFluidCapture.beforeTransfer(a,b,max);}
    @Inject(method="transferFluids",at=@At("RETURN"))private static void hk3gtl$transfer(IFluidTransfer a,IFluidTransfer b,long max,Predicate<FluidStack> filter,CallbackInfoReturnable<Long> ci){com.sirin.hk3gtl.common.easter.Hk3EggFluidCapture.afterTransfer(ci.getReturnValue());}
}
