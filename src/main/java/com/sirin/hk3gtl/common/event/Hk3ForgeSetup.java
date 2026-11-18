package com.sirin.hk3gtl.common.event;

import com.sirin.hk3gtl.common.bootstrap.Hk3ModHealthReport;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;

/**
 * 
 * - 公共阶段 setup：刷新模组注册健康快照（供进世界弹窗使用）。
 *
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class Hk3ForgeSetup {

    private Hk3ForgeSetup() {}

    @SubscribeEvent
    public static void onCommonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(Hk3ModHealthReport::refresh);
    }
}
