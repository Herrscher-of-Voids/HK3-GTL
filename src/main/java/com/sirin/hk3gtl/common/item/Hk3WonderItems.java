package com.sirin.hk3gtl.common.item;

import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderCatalog;
import net.minecraft.world.item.Item;

public final class Hk3WonderItems {
    private Hk3WonderItems() {}
    public static void register() {
        for (var entry : Hk3WonderCatalog.ALL)
            Hk3Items.ITEMS.register(entry.product(), () -> new Item(new Item.Properties()));
        Hk3Items.ITEMS.register("wonder_prefabricated_component", () -> new Item(new Item.Properties()));
        Hk3Items.ITEMS.register("cross_domain_validation_report", () -> new Item(new Item.Properties()));
    }
}
