package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.api.item.capability.ElectricItem;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=ElectricItem.class,remap=false)

public abstract class Hk3EggBatteryMixin {
    @Shadow @Final protected ItemStack itemStack;
    @Inject(method="charge",at=@At("RETURN"))private void hk3gtl$charge(long amount,int tier,boolean ignore,boolean simulate,CallbackInfoReturnable<Long> ci){com.sirin.hk3gtl.common.easter.Hk3EggTools.charged(itemStack,ci.getReturnValue(),simulate);}
}
