package com.sirin.hk3gtl.common.item;

import net.minecraft.world.item.Item;

public final class Hk3CompressedCobblestoneItems {
    private Hk3CompressedCobblestoneItems() {}

    public static void register() {
        for (int tier = 1; tier <= 20; tier++) {
            Hk3Items.ITEMS.register("compressed_cobblestone_" + tier,
                    () -> new Item(new Item.Properties()));
        }
    }
}
