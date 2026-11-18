package com.sirin.hk3gtl.mixin.gtmthings;
import com.lowdragmc.lowdraglib.side.fluid.*;
import java.util.function.Predicate;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=FluidTransferHelper.class,remap=false)



public abstract class Hk3EggFluidTransferMixin {
    @Inject(method="transferFluids",at=@At("HEAD"))private static void hk3gtl$before(IFluidTransfer a,IFluidTransfer b,long max,Predicate<FluidStack> filter,CallbackInfoReturnable<Long> ci){com.sirin.hk3gtl.common.easter.Hk3EggFluidCapture.beforeTransfer(a,b,max);}
    @Inject(method="transferFluids",at=@At("RETURN"))private static void hk3gtl$transfer(IFluidTransfer a,IFluidTransfer b,long max,Predicate<FluidStack> filter,CallbackInfoReturnable<Long> ci){com.sirin.hk3gtl.common.easter.Hk3EggFluidCapture.afterTransfer(ci.getReturnValue());}
}
