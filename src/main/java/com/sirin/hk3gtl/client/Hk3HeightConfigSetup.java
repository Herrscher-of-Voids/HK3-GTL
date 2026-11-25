package com.sirin.hk3gtl.client;

import com.sirin.hk3gtl.common.config.Hk3ConfigPages;
import dev.toma.configuration.Configuration;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.ConfigScreenHandler;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.MOD, value=Dist.CLIENT)
public final class Hk3HeightConfigSetup {
    private Hk3HeightConfigSetup() {}
    @SubscribeEvent public static void clientSetup(FMLClientSetupEvent event) {
        ModLoadingContext.get().registerExtensionPoint(ConfigScreenHandler.ConfigScreenFactory.class,
            () -> new ConfigScreenHandler.ConfigScreenFactory((minecraft, parent) ->
                    Configuration.getConfigScreenByGroup(Hk3ConfigPages.GROUP, parent)));
        event.enqueueWork(Hk3ConfigPages::applyClientSettings);
    }
}
