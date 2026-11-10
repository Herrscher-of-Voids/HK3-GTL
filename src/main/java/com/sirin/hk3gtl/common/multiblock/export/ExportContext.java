package com.sirin.hk3gtl.common.multiblock.export;


/**
 * 【文件职责】
 * - 维护 ExportContext 的核心功能实现。
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
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;

import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** 中文说明：该处说明已按当前代码行为整理。*/
public final class ExportContext {

    public final String exportName;
    public final int width;
    public final int height;
    public final int depth;
    public final char[][][] grid;
    /** 符号 → 方块注册 ID（保持插入顺序） */
    public final Map<Character, ResourceLocation> legend;
    /** 符号 → Ability（对应 GT 原生舱口时才有值，普通方块为 null） */
    public final Map<Character, HatchAbilityMap.Ability> abilityBySymbol;
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public final HatchAbilityMap.Summary abilitySummary;

    public final BlockPos controllerWorldPos;
    public final ResourceLocation controllerId;
    public final Direction controllerFacing;

    /** 导出期间收集的警告条目（如检测到创造仓），格式 "分类: 细节"，用于写入 txt 头部 */
    public final List<String> warnings;
    /** 被拒写入成型条件的方块集合（creative 仓等），后续 Writer 跳过其生成 */
    public final Set<ResourceLocation> rejectedBlocks;

    public ExportContext(String exportName,
                         int width, int height, int depth,
                         char[][][] grid,
                         Map<Character, ResourceLocation> legend,
                         Map<Character, HatchAbilityMap.Ability> abilityBySymbol,
                         BlockPos controllerWorldPos,
                         ResourceLocation controllerId,
                         Direction controllerFacing,
                         List<String> warnings,
                         Set<ResourceLocation> rejectedBlocks) {
        this.exportName = exportName;
        this.width = width;
        this.height = height;
        this.depth = depth;
        this.grid = grid;
        this.legend = new LinkedHashMap<>(legend);
        this.abilityBySymbol = new LinkedHashMap<>(abilityBySymbol);
        this.abilitySummary = HatchAbilityMap.summarize(abilityBySymbol.values());
        this.controllerWorldPos = controllerWorldPos;
        this.controllerId = controllerId;
        this.controllerFacing = controllerFacing;
        this.warnings = List.copyOf(warnings);
        this.rejectedBlocks = new LinkedHashSet<>(rejectedBlocks);
    }
}
