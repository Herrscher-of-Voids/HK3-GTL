package com.sirin.hk3gtl.common.item;

import com.sirin.hk3gtl.common.constants.Hk3VoltagePalette;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/**
 * 【文件职责】八大件使用统一电压定义显示名称，注册键与显示名称分离。
 * 【变更记录 #1】2026-09-28 01:24:51（第 1 次备注 · 内测5修订92）
 * 删除：无。新增：稳定注册后缀到电压索引的校验及带色名称。
 * 修改：由四组部件注册器调用，不复制电压配色，不修改贴图。
 * 用途：名称采用部件名（电压缩写）；后续电压文字配色调整时自动跟随。
 */
/**
 * 【变更记录 #2】2026-09-30 02:17:47（第2次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/**
 * 【变更记录 #3】2026-09-30 03:22:21（内测5修订108）
 * 删除：旧配色引用。新增：批准的16档统一RGB色卡。
 * 修改：八大件电压缩写使用Component精确RGB。
 * 用途：配色统一；电压数值、注册和配方门槛不变。
 */
public final class Hk3ComponentItem extends Item {
    private final int tier;

    public Hk3ComponentItem(String registrationId) {
        super(new Item.Properties());
        int matched = -1;
        for (int i = 0; i < Hk3Tiers.VOLTAGE_KEYS.length; i++) {
            if (registrationId.endsWith("_" + Hk3Tiers.VOLTAGE_KEYS[i])) {
                matched = Hk3Tiers.HBV + i;
                break;
            }
        }
        if (matched < 0) throw new IllegalArgumentException("八大件电压注册后缀无效：" + registrationId);
        tier = matched;
    }

    @Override
    public Component getName(ItemStack stack) {
        // 电压缩写使用精确RGB样式，父名称与括号保持原样。
        return Component.translatable(getDescriptionId(),
                Component.literal(Hk3Tiers.VOLTAGE_SYMBOLS[tier - 15])
                        .withStyle(style -> style.withColor(Hk3VoltagePalette.text(tier)).withBold(true)));
    }
}
