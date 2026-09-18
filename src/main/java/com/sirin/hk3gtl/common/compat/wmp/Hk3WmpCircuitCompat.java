package com.sirin.hk3gtl.common.compat.wmp;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import java.math.BigInteger;
import java.util.Map;


public final class Hk3WmpCircuitCompat {

    private static final BigInteger FOUR = BigInteger.valueOf(4L);
    private static final Map<ResourceLocation, Integer> CIRCUIT_TIERS = Map.ofEntries(
            circuit("abyss_1_processor", 15),
            circuit("abyss_2_assembly", 16),
            circuit("abyss_3_computer", 17),
            circuit("abyss_4_processor_mainframe", 18),
            circuit("imaginary_1_processor", 19),
            circuit("imaginary_2_assembly", 20),
            circuit("imaginary_3_computer", 21),
            circuit("imaginary_4_processor_mainframe", 22),
            circuit("quantum_1_processor", 23),
            circuit("quantum_2_assembly", 24),
            circuit("quantum_3_computer", 25),
            circuit("quantum_4_processor_mainframe", 26),
            circuit("finality_1_processor", 27),
            circuit("finality_2_assembly", 28),
            circuit("finality_3_computer", 29),
            circuit("finality_4_processor_mainframe", 30)
    );

    private Hk3WmpCircuitCompat() {}

    public static boolean isHk3Circuit(ItemStack stack) {
        return getTier(stack) >= Hk3Tiers.ABYSS_1;
    }

    public static int getTier(ItemStack stack) {
        if (stack == null || stack.isEmpty()) return -1;
        ResourceLocation id = net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem());
        return id == null ? -1 : CIRCUIT_TIERS.getOrDefault(id, -1);
    }

    public static BigInteger getVoltage(int tier) {
        if (tier < Hk3Tiers.ABYSS_1 || tier > Hk3Tiers.FINALITY_4) return BigInteger.ZERO;
        return BigInteger.valueOf(8L).multiply(FOUR.pow(tier));
    }

    public static String getTierName(int tier) {
        if (tier < Hk3Tiers.ABYSS_1 || tier > Hk3Tiers.FINALITY_4) return "";
        return Hk3Tiers.VOLTAGE_KEYS[tier - Hk3Tiers.ABYSS_1].toUpperCase(java.util.Locale.ROOT);
    }

    private static Map.Entry<ResourceLocation, Integer> circuit(String path, int tier) {
        return Map.entry(new ResourceLocation("hk3gtl", path), tier);
    }
}
