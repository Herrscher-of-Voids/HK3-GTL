package com.sirin.hk3gtl.common.item.main;

 








import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.material.main.Hk3MainMaterialCatalog;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.RegistryObject;

public final class Hk3MainMaterialItems {
    private static volatile Map<String, RegistryObject<Item>> items = Map.of();
    private static boolean registered;

    private Hk3MainMaterialItems() {}

    public static synchronized void register() {
        if (registered) return;
        Map<String, RegistryObject<Item>> registeredItems = new LinkedHashMap<>();
        for (Hk3MainMaterialCatalog.Entry entry : Hk3MainMaterialCatalog.entries()) {
            for (Hk3MainMaterialCatalog.Form form : entry.forms()) {
                String path = Hk3MainMaterialCatalog.itemPath(entry.tier(), form.key());
                RegistryObject<Item> item = Hk3Items.ITEMS.register(path, () -> new Item(new Item.Properties()));
                if (registeredItems.put(path, item) != null) {
                    throw new IllegalStateException("重复主材料物品：" + path);
                }
            }
        }
        items = Collections.unmodifiableMap(registeredItems);
        registered = true;
    }

    public static ResourceLocation itemId(int tier, String form) {
        return new ResourceLocation(Hk3Constants.MOD_ID, Hk3MainMaterialCatalog.itemPath(tier, form));
    }

    public static ItemStack stack(int tier, String form, int count) {
        String path = Hk3MainMaterialCatalog.itemPath(tier, form);
        if (count < 1 || count > 64) throw new IllegalArgumentException("主材料物品数量必须为1至64：" + count);
        RegistryObject<Item> item = items.get(path);
        if (item == null) throw new IllegalStateException("主材料物品尚未完成注册：" + path);
        return new ItemStack(item.get(), count);
    }

    public static Map<String, RegistryObject<Item>> items() {
        return items;
    }
}
