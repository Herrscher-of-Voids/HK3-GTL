package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.projectile.FishingHook;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
/** 【变更记录 #1】2026-10-01 05:02:11（修订128）：删除无；新增真实收竿完成观察；用途：不依赖只有鱼类才增加的原版FISH_CAUGHT统计，保留取消事件。 */
@Mixin(FishingHook.class)
public abstract class Hk3EggFishingMixin {
    @Inject(method="retrieve",at=@At("HEAD"))private void hk3gtl$before(ItemStack rod,CallbackInfoReturnable<Integer> ci){com.sirin.hk3gtl.common.easter.Hk3EggFishing.begin((FishingHook)(Object)this);}
    @Inject(method="retrieve",at=@At("RETURN"))private void hk3gtl$after(ItemStack rod,CallbackInfoReturnable<Integer> ci){com.sirin.hk3gtl.common.easter.Hk3EggFishing.end((FishingHook)(Object)this);}
}
