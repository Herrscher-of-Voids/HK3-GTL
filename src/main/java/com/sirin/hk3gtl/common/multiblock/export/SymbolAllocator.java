package com.sirin.hk3gtl.common.multiblock.export;


/**
 * 【文件职责】
 * - 维护 SymbolAllocator 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import net.minecraft.resources.ResourceLocation;

import java.util.LinkedHashMap;
import java.util.Map;

/** 中文说明：该处说明已按当前代码行为整理。*/
public final class SymbolAllocator {

    public static final char CONTROLLER_SYMBOL = 'S';
    public static final char AIR_SYMBOL = '#';
    public static final char HATCH_SYMBOL = 'H';

    /** 字母池；不含 S / H / #，避免和保留/聚合符号冲突 */
    private static final char[] POOL = (
            "ABCDEFGIJKLMNOPQRTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@$%&+")
            .toCharArray();

    /** 已分配的 id → 符号映射（LinkedHashMap 保持插入顺序，便于生成 where 链稳定） */
    private final Map<ResourceLocation, Character> byId = new LinkedHashMap<>();
    /** 反向索引：符号 → id，用于判定首选符号是否已占用 */
    private final Map<Character, ResourceLocation> legend = new LinkedHashMap<>();
    /** 符号 → 识别到的舱口能力（若非 GT 原生舱口则为 null） */
    private final Map<Character, HatchAbilityMap.Ability> abilityBySymbol = new LinkedHashMap<>();
    /** 下一个从 POOL 取的游标 */
    private int poolCursor = 0;

    /**
     * 为指定方块 id 申请符号。相同 id 重复调用返回同一字符。
     *
     * @param id 方块注册名
     * @param ability 舱口识别结果（见 {@link HatchAbilityMap#lookup}），普通方块传 null
     * @return 分配的字符
     * @throws IllegalStateException 符号池耗尽时抛出
     */
    public char allocate(ResourceLocation id, HatchAbilityMap.Ability ability) {
        Character existing = byId.get(id);
        if (existing != null) return existing;

        // 所有 GT 原生舱口（非 creative）统一归为 H，多种舱口共用同一符号 → 成型用 abilities
        if (ability != null && ability != HatchAbilityMap.CREATIVE_MARKER) {
            byId.put(id, HATCH_SYMBOL);
            if (!legend.containsKey(HATCH_SYMBOL)) {
                legend.put(HATCH_SYMBOL, id);
            }
            abilityBySymbol.merge(HATCH_SYMBOL, ability, (a, b) -> a);
            return HATCH_SYMBOL;
        }

        char preferred = preferredFor(id);
        char chosen;
        if (preferred != 0 && !legend.containsKey(preferred)) {
            chosen = preferred;
        } else {
            chosen = nextFromPool();
        }

        byId.put(id, chosen);
        legend.put(chosen, id);
        abilityBySymbol.put(chosen, null);
        return chosen;
    }

    /** @return 不可变的符号 → 方块 id 映射（插入顺序） */
    public Map<Character, ResourceLocation> legend() {
        return legend;
    }

    /** @return 符号 → 舱口能力映射；普通方块对应值为 null */
    public Map<Character, HatchAbilityMap.Ability> abilityBySymbol() {
        return abilityBySymbol;
    }

    /** 基于方块路径关键字猜测首选符号；无推荐返回 0 */
    private static char preferredFor(ResourceLocation id) {
        String path = id.getPath();
        if (path.contains("casing")) return 'X';
        if (path.contains("glass")) return 'G';
        if (path.contains("coil")) return 'C';
        if (path.contains("frame") || path.contains("frame_box")) return 'F';
        return 0;
    }

    private char nextFromPool() {
        while (poolCursor < POOL.length) {
            char c = POOL[poolCursor++];
            if (!isReserved(c) && !legend.containsKey(c)) {
                return c;
            }
        }
        throw new IllegalStateException(
                "结构中方块种类过多，符号池已耗尽（当前上限 " + POOL.length + " 种）");
    }

    private static boolean isReserved(char c) {
        return c == CONTROLLER_SYMBOL || c == AIR_SYMBOL || c == HATCH_SYMBOL || c == ' ';
    }
}
