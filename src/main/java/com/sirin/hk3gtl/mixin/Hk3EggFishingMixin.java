package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.projectile.FishingHook;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(FishingHook.class)
public abstract class Hk3EggFishingMixin {
    @Inject(method="retrieve",at=@At("HEAD"))private void hk3gtl$before(ItemStack rod,CallbackInfoReturnable<Integer> ci){com.sirin.hk3gtl.common.easter.Hk3EggFishing.begin((FishingHook)(Object)this);}
    @Inject(method="retrieve",at=@At("RETURN"))private void hk3gtl$after(ItemStack rod,CallbackInfoReturnable<Integer> ci){com.sirin.hk3gtl.common.easter.Hk3EggFishing.end((FishingHook)(Object)this);}
}
