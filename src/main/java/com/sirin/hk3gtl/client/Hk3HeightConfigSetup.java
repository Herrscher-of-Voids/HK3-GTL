package com.sirin.hk3gtl.client;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.ConfigScreenHandler;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import dev.toma.configuration.Configuration;

/**
 * 仅客户端登记Forge模组配置按钮，专服不解析界面类。
 */
@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.MOD, value=Dist.CLIENT)
public final class Hk3HeightConfigSetup {
    private Hk3HeightConfigSetup() {}
    @SubscribeEvent public static void clientSetup(FMLClientSetupEvent event) {
        com.sirin.hk3gtl.common.config.Hk3ResearchSettings.setChangeListener(
                com.sirin.hk3gtl.client.compat.Hk3JeiLifecyclePlugin::refreshResearchVisibility);
        ModLoadingContext.get().registerExtensionPoint(ConfigScreenHandler.ConfigScreenFactory.class,
            () -> new ConfigScreenHandler.ConfigScreenFactory((minecraft, parent) ->
                    Configuration.getConfigScreenByGroup(com.sirin.hk3gtl.common.config.Hk3ConfigPages.GROUP, parent)));
        event.enqueueWork(com.sirin.hk3gtl.common.config.Hk3ConfigPages::applyClientSettings);
    }
}
