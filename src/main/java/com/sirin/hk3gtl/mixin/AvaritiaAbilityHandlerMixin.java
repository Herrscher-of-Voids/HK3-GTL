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

/**
 * 【文件职责】修复Re-Avaritia能力状态集合被单人客户端与服务端线程同时修改的问题。
 * 【变更记录 #1】2026-09-30 17:52:49（内测5修订111）
 * 删除：无；不取消装备能力检查，不吞掉游戏tick异常。
 * 新增：静态初始化结束时将共享HashMap/HashSet替换为并发集合，保留原有记录引用。
 * 修改：仅改变集合实现；FlightInfo按原来的玩家名＋逻辑端键隔离，能力规则保持原样。
 * 用途：修复AbilityHandler.handleChestStateChange中computeIfAbsent抛ConcurrentModificationException。
 * 边界：插件仅在avaritia存在时启用；字段名及描述符已对照1.3.8.3原始字节码核验。
 */
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
