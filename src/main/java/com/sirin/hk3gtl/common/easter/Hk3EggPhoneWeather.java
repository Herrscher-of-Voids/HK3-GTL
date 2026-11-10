package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
/** 【变更记录 #1】2026-10-01 05:56:06（修订128）：删除无；新增叶荫下首次打开手机与四月雨中关屏仰望；修改无；用途：天气、视向和上方遮挡由服务器核验，不改变界面或天气。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggPhoneWeather {
    private Hk3EggPhoneWeather(){}
    public static void opened(ServerPlayer p){
        Hk3EggRuntime.state(p).remove("aprilRainClosed");
        if(Hk3EggCalendar.now().getMonthValue()!=7)return;
        var at=p.blockPosition().above(2).mutable();
        for(int y=at.getY();y<p.level().getMaxBuildHeight();y++){
            at.setY(y);var block=p.level().getBlockState(at);if(block.isAir())continue;
            if(block.is(BlockTags.LEAVES))Hk3EggVanilla.caseEvent(p,357);return;
        }
    }
    public static void closed(ServerPlayer p){
        var now=Hk3EggCalendar.now();if(now.getMonthValue()==4&&p.level().isRaining())Hk3EggRuntime.state(p).putString("aprilRainClosed",now.toLocalDate().toString());
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%5!=0)return;var s=Hk3EggRuntime.state(p);if(!s.contains("aprilRainClosed"))return;
        if(s.getBoolean("phoneOpen")||!p.level().isRaining()||!s.getString("aprilRainClosed").equals(Hk3EggCalendar.now().toLocalDate().toString())){s.remove("aprilRainClosed");return;}
        if(p.getXRot()<-45&&p.level().canSeeSky(p.blockPosition().above())){Hk3EggVanilla.caseEvent(p,348);s.remove("aprilRainClosed");}
    }
}
