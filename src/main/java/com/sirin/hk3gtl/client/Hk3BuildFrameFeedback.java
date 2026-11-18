package com.sirin.hk3gtl.client;

import com.sirin.hk3gtl.common.network.Hk3BuildFramePacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 反馈包处理、逻辑tick与渲染的忙碌耗时，排除垂直同步和限帧等待。 */
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3BuildFrameFeedback {
    private static double average=16;
    private static int ticks;
    public static void recordFrame(long nanos) {
        double ms=Math.min(1000,nanos/1_000_000.0);
        average=average*.9+ms*.1;
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        if(mc.player==null||mc.level==null) {ticks=0;average=16;return;}
        if(++ticks%20==0)Hk3Network.CHANNEL.sendToServer(new Hk3BuildFramePacket((float)Math.max(1,average)));
    }
}
