package com.sirin.hk3gtl.common.event;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameRules;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3NaturalSupplyDrops {
    private static final ResourceLocation GLACIAN_RAM = new ResourceLocation("ad_astra", "glacian_ram");
    private static final ResourceLocation GLACIO_SPIRIT = new ResourceLocation("kubejs", "glacio_spirit");
    private static final ResourceLocation ICE_SHARD = new ResourceLocation("ad_astra", "ice_shard");

    private Hk3NaturalSupplyDrops() {}

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onDrops(LivingDropsEvent event) {
        var entity = event.getEntity();
        if (!BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType()).equals(GLACIAN_RAM)
                || !entity.level().getGameRules().getBoolean(GameRules.RULE_DOMOBLOOT)) return;
        var spirit = BuiltInRegistries.ITEM.get(GLACIO_SPIRIT);
        var ice = BuiltInRegistries.ITEM.get(ICE_SHARD);
        if (event.getDrops().stream().anyMatch(drop -> drop.getItem().is(spirit) || drop.getItem().is(ice))) return;
        var item = entity.getRandom().nextInt(10) == 0 ? spirit : ice;
        event.getDrops().add(new ItemEntity(entity.level(), entity.getX(), entity.getY(), entity.getZ(), new ItemStack(item)));
    }
}
