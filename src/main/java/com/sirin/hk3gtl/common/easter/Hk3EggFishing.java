package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.projectile.FishingHook;
import net.minecraft.world.item.Items;
import net.minecraft.tags.BiomeTags;
import net.minecraftforge.event.entity.player.ItemFishedEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** 【变更记录 #1】2026-10-01 05:02:11（修订128）：删除无；新增原版钓获事件与retrieve完成配对；用途：读取最终取消状态，拉实体/空收竿/取消掉落不计，暂态在原调用结束清理。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggFishing {
    private static final ThreadLocal<Map<FishingHook,ItemFishedEvent>> ACTIVE=ThreadLocal.withInitial(HashMap::new);
    private Hk3EggFishing(){}
    public static void begin(FishingHook hook){ACTIVE.get().put(hook,null);}
    @SubscribeEvent(priority=EventPriority.LOWEST,receiveCanceled=true)public static void caught(ItemFishedEvent e){if(ACTIVE.get().containsKey(e.getHookEntity()))ACTIVE.get().put(e.getHookEntity(),e);}
    public static void end(FishingHook hook){
        var map=ACTIVE.get();var event=map.remove(hook);if(map.isEmpty())ACTIVE.remove();
        if(event==null||event.isCanceled()||event.getDrops().stream().allMatch(s->s.isEmpty())||!(hook.getPlayerOwner() instanceof ServerPlayer p))return;
        if(Hk3EggVanilla.increment(p,"fishingSuccesses",13)>=13)Hk3EggVanilla.caseEvent(p,293);
        Hk3EggRuntime.state(p).putBoolean("fishedAndReeled",true);
        if(p.isInWater()&&p.getY()<p.level().getSeaLevel()-30)Hk3EggVanilla.caseEvent(p,428);
        if(p.level().getBiome(hook.blockPosition()).is(BiomeTags.IS_OCEAN)&&event.getDrops().stream().anyMatch(s->s.is(Items.COD)||s.is(Items.SALMON)||s.is(Items.PUFFERFISH)||s.is(Items.TROPICAL_FISH)))Hk3EggVanilla.caseEvent(p,434);
    }
}
