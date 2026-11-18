package com.sirin.hk3gtl.common.item;

import com.sirin.hk3gtl.common.constants.Hk3VoltagePalette;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/**
 * 八大件使用统一电压定义显示名称，注册键与显示名称分离。
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
