package com.sirin.hk3gtl.common.multiblock.export;



import net.minecraft.resources.ResourceLocation;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * GT / GTMThings 原生舱口方块 ID → {@code PartAbility} 抽象能力的映射表。
 *
 * <h3>设计目的</h3>
 * 导出器扫描到具体的 {@code gtceu:lv_input_bus} 等方块时，会通过本表把"具体方块"抽象成
 * "能力条目"（如 {@code PartAbility.IMPORT_ITEMS}），最终生成 Pattern 的时候，
 * 这些具体舱口不会直接塞到 {@code Predicates.blocks(...)} 里，而是统一用
 * {@code Predicates.autoAbilities(...)} 自动覆盖，让玩家可以接任何等级的同类舱口。
 *
 * <h3>返回值约定</h3>
 * <ul>
 *   <li>非 null：建议使用的 {@link Ability}（含 PartAbility 枚举名 + 是否推荐用 autoAbilities）</li>
 *   <li>null：不是已知的 GT 舱口，按普通方块处理（保留 {@code Predicates.blocks} 直引用）</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增 GT 衍生舱口：在 {@link #lookup} 中追加 endsWithAny 判定 + 返回 {@link Ability}</li>
 *   <li>区分是否被 autoAbilities 自动覆盖：{@link Ability#coveredByAuto}。
 *       被覆盖的不需要在 Pattern 中显式 {@code or(abilities(...))}，直接丢进 autoAbilities 即可。</li>
 *   <li>识别 creative 舱口：返回 {@link #CREATIVE_MARKER}，调用方会拒绝写入成型条件</li>
 *   <li>判断顺序重要：更具体的前置判定要放在前面（如 wireless 要排在普通 energy 前面）</li>
 * </ul>
 */
public final class HatchAbilityMap {

    /** 控制器约定命名空间（用于判断是否 HK3 自身的舱口，一般不会走到 lookup） */
    private static final String NS_GTCEU = "gtceu";
    private static final String NS_GTMTHINGS = "gtmthings";

    /** 创造模式舱口统一标记，遇到此返回值应拒绝导出，项目硬约束。 */
    public static final Ability CREATIVE_MARKER = new Ability("__CREATIVE__", false);

    private HatchAbilityMap() {}

    /**
     * 尝试把某个方块 ID 映射为 PartAbility。
     *
     * @param id 方块注册名
     * @return 映射结果；null 表示不是已知 GT 舱口，按普通方块处理
     */
    public static Ability lookup(ResourceLocation id) {
        if (id == null) return null;
        String ns = id.getNamespace();
        String path = id.getPath();

        // 创造仓（所有 mod 都可能带）严禁进入成型
        if (path.contains("creative_") &&
                (path.contains("hatch") || path.contains("bus") || path.contains("source"))) {
            return CREATIVE_MARKER;
        }

        if (!NS_GTCEU.equals(ns) && !NS_GTMTHINGS.equals(ns)) {
            return null;
        }

        // ── 物品总线 ──
        if (contains(path, "item_input_bus") || contains(path, "item_import_bus")
                || contains(path, "huge_item_input_bus")) {
            return new Ability("IMPORT_ITEMS", true);
        }
        if (contains(path, "item_output_bus") || contains(path, "item_export_bus")
                || contains(path, "huge_item_output_bus")) {
            return new Ability("EXPORT_ITEMS", true);
        }

        // ── 流体仓 ──
        if (contains(path, "fluid_input_hatch") || contains(path, "fluid_import_hatch")
                || contains(path, "huge_fluid_input_hatch")) {
            return new Ability("IMPORT_FLUIDS", true);
        }
        if (contains(path, "fluid_output_hatch") || contains(path, "fluid_export_hatch")
                || contains(path, "huge_fluid_output_hatch")) {
            return new Ability("EXPORT_FLUIDS", true);
        }

        // ── 激光仓（要在 energy 判定之前，否则会被吞）──
        if (contains(path, "laser_source_hatch") || contains(path, "laser_input_hatch")) {
            return new Ability("INPUT_LASER", false);
        }
        if (contains(path, "laser_target_hatch") || contains(path, "laser_output_hatch")) {
            return new Ability("OUTPUT_LASER", false);
        }

        // ── 能源仓（含无线能源仓：走通用 INPUT_ENERGY / OUTPUT_ENERGY）──
        if (contains(path, "energy_input_hatch") || contains(path, "wireless_energy_input_hatch")
                || path.endsWith("_energy_hatch") || contains(path, "substation_hatch")) {
            return new Ability("INPUT_ENERGY", false);
        }
        if (contains(path, "energy_output_hatch") || contains(path, "wireless_energy_output_hatch")
                || path.endsWith("_dynamo_hatch")) {
            return new Ability("OUTPUT_ENERGY", false);
        }

        // ── 特殊仓 ──
        if (contains(path, "parallel_hatch")) {
            return new Ability("PARALLEL_HATCH", false);
        }
        if (contains(path, "maintenance_hatch")) {
            return new Ability("MAINTENANCE", false);
        }
        if (contains(path, "muffler_hatch")) {
            return new Ability("MUFFLER", false);
        }
        if (contains(path, "optical_data_hatch_input")) {
            return new Ability("DATA_ACCESS_HATCH", false);
        }
        if (contains(path, "computation_hatch")) {
            return new Ability("COMPUTATION_DATA_TRANSMISSION", false);
        }

        return null;
    }

    /**
     * 按 coveredByAuto 分组统计所有 Ability。
     * 调用方用此结果决定：
     * <ul>
     *   <li>是否在 Pattern 里添加 {@code autoAbilities(definition.getRecipeTypes())}</li>
     *   <li>是否追加 {@code autoAbilities(true, false, false)} 以覆盖能源仓</li>
     *   <li>哪些 Ability 需要显式 {@code or(abilities(PartAbility.XXX))}</li>
     * </ul>
     */
    public static Summary summarize(Iterable<Ability> abilities) {
        boolean hasIO = false;
        boolean hasEnergy = false;
        Map<String, Boolean> explicit = new LinkedHashMap<>();
        for (Ability a : abilities) {
            if (a == null || a == CREATIVE_MARKER) continue;
            switch (a.partAbility) {
                case "IMPORT_ITEMS", "EXPORT_ITEMS", "IMPORT_FLUIDS", "EXPORT_FLUIDS" -> hasIO = true;
                case "INPUT_ENERGY", "OUTPUT_ENERGY" -> hasEnergy = true;
                default -> explicit.put(a.partAbility, Boolean.TRUE);
            }
        }
        return new Summary(hasIO, hasEnergy, explicit);
    }

    private static boolean contains(String haystack, String needle) {
        return haystack.contains(needle);
    }

    /**
     * 单个舱口能力条目。
     *
     * @param partAbility GT {@code PartAbility} 枚举常量名，如 "IMPORT_ITEMS"
     * @param coveredByAuto 是否可以被 {@code autoAbilities(definition.getRecipeTypes())} 自动覆盖
     *                     （物品/流体仓=true；能源/激光/并行/维护=false）
     */
    public record Ability(String partAbility, boolean coveredByAuto) {}

    /**
     * 能力汇总，供 Pattern 生成器决定要用哪套 autoAbilities + 显式 or 链。
     *
     * @param hasItemOrFluidHatch 选区中出现过物品/流体仓 → 需要 autoAbilities(recipeTypes)
     * @param hasEnergyHatch 选区中出现过能源仓 → 需要 autoAbilities(true, false, false)
     * @param explicitAbilities 其他需要显式 or(abilities(...)) 的能力集合
     */
    public record Summary(boolean hasItemOrFluidHatch, boolean hasEnergyHatch,
                          Map<String, Boolean> explicitAbilities) {}
}
