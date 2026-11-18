package com.sirin.hk3gtl.client;

import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterColorHandlersEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class Hk3SouliumItemColors {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void registerColors(RegisterColorHandlersEvent.Item event) {
        event.register((stack, tintIndex) -> -1,
                ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM).getItem(),
                ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM).getItem(),
                ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM).getItem());
    }
}
