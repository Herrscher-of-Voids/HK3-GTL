package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.damagesource.DamageSource;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(LivingEntity.class)
/** 【变更记录 #1】2026-10-01 13:27:41（修订128）：删除：无；新增/修改：伤害实际返回且生命下降后记录命名普通僵尸，取消伤害不产生隔离前置；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggZombieDamageMixin {
    @Unique private float hk3gtl$beforeHealth;
    @Inject(method="hurt",at=@At("HEAD"))private void hk3gtl$before(DamageSource source,float amount,CallbackInfoReturnable<Boolean> ci){hk3gtl$beforeHealth=((LivingEntity)(Object)this).getHealth();}
    @Inject(method="hurt",at=@At("RETURN"))private void hk3gtl$after(DamageSource source,float amount,CallbackInfoReturnable<Boolean> ci){if(ci.getReturnValue())com.sirin.hk3gtl.common.easter.Hk3EggLocalScenes.hurt((LivingEntity)(Object)this,source,hk3gtl$beforeHealth);}
}
