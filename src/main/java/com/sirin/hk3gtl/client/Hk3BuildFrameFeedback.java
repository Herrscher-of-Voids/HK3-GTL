package com.sirin.hk3gtl.client;

import com.sirin.hk3gtl.common.network.Hk3BuildFramePacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 帧耗时反馈不改变玩家视距或帧率设置。 */
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3BuildFrameFeedback {
    private static long last;
    private static double average=16;
    private static int ticks;
    @SubscribeEvent public static void frame(TickEvent.RenderTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        long now=System.nanoTime();
        if(last!=0) {double ms=(now-last)/1_000_000.0;if(ms>0&&ms<1000)average=average*.9+ms*.1;}
        last=now;
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        if(mc.player==null||mc.level==null) {ticks=0;last=0;average=16;return;}
        if(++ticks%20==0)Hk3Network.CHANNEL.sendToServer(new Hk3BuildFramePacket((float)Math.max(1,average)));
    }
}
