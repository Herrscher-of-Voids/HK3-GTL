package com.sirin.hk3gtl.common.compat.wmp;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import java.math.BigInteger;
import java.util.Map;

/**
 * 
 * - 维护 hk3gtl 16 个 canonical 高阶电路与 WMP GT 发电等级之间的稳定映射。
 * - 关键调用链：WMP GTEnergyHelper/VoltageHelper Mixin -> 本类 -> tier 15~30 与 BigInteger 电压。
 *
 */
public final class Hk3WmpCircuitCompat {

    private static final BigInteger FOUR = BigInteger.valueOf(4L);
    

    private Hk3WmpCircuitCompat() {}

    public static boolean isHk3Circuit(ItemStack stack) {
        return getTier(stack) >= Hk3Tiers.HBV;
    }

    public static int getTier(ItemStack stack) {
        if (stack == null || stack.isEmpty()) return -1;
        ResourceLocation id = net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem());
        return id == null ? -1 : com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tier(id);
    }

    public static BigInteger getVoltage(int tier) {
        if (tier < Hk3Tiers.HBV || tier > Hk3Tiers.CEV) return BigInteger.ZERO;
        return BigInteger.valueOf(8L).multiply(FOUR.pow(tier));
    }

    public static String getTierName(int tier) {
        if (tier < Hk3Tiers.HBV || tier > Hk3Tiers.CEV) return "";
        return Hk3Tiers.VOLTAGE_SYMBOLS[tier - Hk3Tiers.HBV];
    }

    private static Map.Entry<ResourceLocation, Integer> circuit(String path, int tier) {
        return Map.entry(new ResourceLocation("hk3gtl", path), tier);
    }
}
