package com.sirin.hk3gtl.common.item;

import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

/** 彩蛋纪念物品。 */
public final class EasterEggItems {

    public static RegistryObject<Item> NON_QIU_CERTIFICATE;

    private EasterEggItems() {}

    public static void register() {
        NON_QIU_CERTIFICATE = Hk3Items.ITEMS.register("non_qiu_certificate",
                () -> new Item(new Item.Properties().stacksTo(1)));
    }
}
