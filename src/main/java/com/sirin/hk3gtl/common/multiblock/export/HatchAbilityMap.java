package com.sirin.hk3gtl.common.multiblock.export;


/**
 * 【文件职责】
 * - 维护 HatchAbilityMap 的核心功能实现。
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

    /** 中文说明：该处说明已按当前代码行为整理。*/
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

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public record Summary(boolean hasItemOrFluidHatch, boolean hasEnergyHatch,
                          Map<String, Boolean> explicitAbilities) {}
}
