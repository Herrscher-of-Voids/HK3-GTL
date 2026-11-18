package com.sirin.hk3gtl.mixin;

import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

 








@Pseudo
@Mixin(targets="committee.nova.mods.avaritia.init.handler.AbilityHandler",remap=false)
public abstract class AvaritiaAbilityHandlerMixin {
    @Shadow @Final @Mutable public static Map<String,Object> entitiesWithFlight;
    @Shadow @Final @Mutable public static Set<String> entitiesWithHelmets;
    @Shadow @Final @Mutable public static Set<String> entitiesWithLeggings;
    @Shadow @Final @Mutable public static Set<String> entitiesWithBoots;

    /** JVM类初始化锁内只替换一次，首次玩家tick开始前即完成；不在每刻重复复制。 */
    @Inject(method="<clinit>",at=@At("RETURN"),require=1)
    private static void hk3gtl$makeAbilityStateConcurrent(CallbackInfo callback){
        entitiesWithFlight=new ConcurrentHashMap<>(entitiesWithFlight);
        Set<String> helmets=ConcurrentHashMap.newKeySet();helmets.addAll(entitiesWithHelmets);entitiesWithHelmets=helmets;
        Set<String> leggings=ConcurrentHashMap.newKeySet();leggings.addAll(entitiesWithLeggings);entitiesWithLeggings=leggings;
        Set<String> boots=ConcurrentHashMap.newKeySet();boots.addAll(entitiesWithBoots);entitiesWithBoots=boots;
    }
}
