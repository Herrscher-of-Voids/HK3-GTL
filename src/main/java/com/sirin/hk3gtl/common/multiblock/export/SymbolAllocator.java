package com.sirin.hk3gtl.common.multiblock.export;



import net.minecraft.resources.ResourceLocation;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 导出时将方块注册 ID 映射为单字符符号的分配器。
 *
 * <h3>分配策略（按优先级）</h3>
 * <ol>
 *   <li>同一 ID 必须返回同一字符（通过 {@code byId} 缓存保证）</li>
 *   <li>若该方块被识别为 GT 原生舱口（{@link HatchAbilityMap#lookup} 非 null 且非创造），
 *       统一归为 {@link #HATCH_SYMBOL} {@code 'H'}，成型时走 abilities 抽象</li>
 *   <li>按方块路径关键字的首选符号：
 *       <ul>
 *         <li>casing → X</li>
 *         <li>glass → G</li>
 *         <li>coil → C</li>
 *         <li>frame / frame_box → F</li>
 *       </ul>
 *       若首选符号已被占用 → 回退到字母池顺序分配</li>
 *   <li>其他按 {@link #POOL} 顺序分配：A→Z → a→z → 0→9 → 其他符号</li>
 * </ol>
 *
 * <h3>保留字符</h3>
 * <ul>
 *   <li>{@code 'S'} = 控制器（由扫描器单独处理）</li>
 *   <li>{@code '#'} = 空气</li>
 *   <li>{@code ' '} = Pattern 中 {@code Predicates.any()} 的自由位（本分配器不使用）</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>扩展符号池：修改 {@link #POOL}。当前 64 字符，重构结构密度更大时需扩充</li>
 *   <li>调整首选符号：改 {@link #preferredFor}。首选符号只在"首次遇到"且未占用时生效</li>
 *   <li>新增保留字符：在 {@link #isReserved} 与 {@link #POOL} 中同步调整</li>
 * </ul>
 */
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
