package com.sirin.hk3gtl.client;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.ConfigScreenHandler;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

/**
 * 【文件职责】仅客户端登记Forge模组配置按钮，专服不解析界面类。
 * 【变更记录 #1】2026-10-17 21:26:10（第1次备注 · 修订166）
 * - 删除：无。新增：高度设置界面工厂；修改：无其他系统配置。
 * - 用途：让新世界高度配置可见可校验，不在客户端自行改变同步后的维度。
 */
@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.MOD, value=Dist.CLIENT)
public final class Hk3HeightConfigSetup {
    private Hk3HeightConfigSetup() {}
    @SubscribeEvent public static void clientSetup(FMLClientSetupEvent event) {
        ModLoadingContext.get().registerExtensionPoint(ConfigScreenHandler.ConfigScreenFactory.class,
            () -> new ConfigScreenHandler.ConfigScreenFactory((minecraft, parent) -> new Hk3HeightConfigScreen(parent)));
    }
}
