package com.sirin.hk3gtl.common.compat.wmp;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import java.math.BigInteger;
import java.util.Map;

/**
 * 【文件职责】
 * - 维护 hk3gtl 16 个 canonical 高阶电路与 WMP GT 发电等级之间的稳定映射。
 * - 关键调用链：WMP GTEnergyHelper/VoltageHelper Mixin -> 本类 -> tier 15~30 与 BigInteger 电压。
 *
 * 【变更记录 #1】2026-07-19 20:14:25（第 1 次备注 · 内测四第 33 次更新）
 * - 删除：
 *   1) 无；本文件为 WMP 1.7.0 可选联动新增。
 * - 新增：
 *   1) 新增 16 个正式电路物品 ID 到 Tier 15~30 的一对一映射，不包含 48 个归档占位形态。
 *   2) 新增公式电压 8×4^tier 的 BigInteger 查询，避免 WMP 原 0~14 数组钳制和 long 溢出。
 * - 修改：
 *   1) 无历史逻辑。
 * - 用途：
 *   1) 让海渊、虚数、量子、终焉四阶段电路板进入 WMP 电路槽，并按其真实高阶电压参与发电计算。
 */
/**
 * 【变更记录 #2】2026-09-25 03:57:37（第 2 次备注 · 内测5修订71）
 * 删除：单一电路形态或旧电压显示限制。新增：统一系列及电压映射。
 * 修改：WMP识别全部28种电路并显示已确认的电压标识。
 * 用途：保持同级电路可替换、资源与游戏行为一致。
 */
/**
 * 【变更记录 #3】2026-09-30 02:17:47（第3次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
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
