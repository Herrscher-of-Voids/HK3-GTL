package com.sirin.hk3gtl.common.item.main;

/**
 * 【文件职责】在现有物品注册器中登记十六阶主材料实体，并向配方提供校验后的物品栈。
 * 【变更记录 #1】2026-10-17 16:25:14（第 1 次备注 · 修订165）
 * - 删除：无；不注册抽象材料基础名，不注册任何方块或自动熔炼材料。
 * - 新增：十六阶十一类标准形态与五十五个工序中间件，统一物品路径及严格查询入口。
 * - 修改：注册期一次写入后发布不可变快照，重复调用不重复登记；物品栈数量限制为1至64。
 * - 用途：由Hk3Items在挂事件总线前调用，为生产、回收及同级消费者提供真实身份；美术资源仍待审批。
 */

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
