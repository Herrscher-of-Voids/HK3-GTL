package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(Entity.class)
 
public abstract class Hk3EggVoidItemMixin {
    @Inject(method="onBelowWorld",at=@At("RETURN"))private void hk3gtl$voided(CallbackInfo ci){
        if((Object)this instanceof ItemEntity item&&item.isRemoved()&&item.level() instanceof ServerLevel level&&item.getY()<level.getMinBuildHeight()-64&&net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(item.getItem().getItem()).toString().equals("hk3gtl:honkai_energy_crystal")){
            var owner=((Hk3EggItemThrowerAccessor)item).hk3gtl$thrower();if(owner!=null)com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(level.getServer()).produced(owner,"receipt:84",1);
        }
    }
}
