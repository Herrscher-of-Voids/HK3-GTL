package com.sirin.hk3gtl.client.gaze;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 客户端注视度状态生命周期：断开连接时复位缓存，防止下次进不同存档时残留旧数据。
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class Hk3ClientGazeEvents {

    private Hk3ClientGazeEvents() {}

    @SubscribeEvent
    public static void onLoggingOut(ClientPlayerNetworkEvent.LoggingOut event) {
        Hk3ClientGazeState.reset();
    }
}
