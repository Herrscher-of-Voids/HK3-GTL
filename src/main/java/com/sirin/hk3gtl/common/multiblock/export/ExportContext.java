package com.sirin.hk3gtl.common.multiblock.export;



import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;

import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 多方块导出流程中贯穿各 Writer 的不可变数据载体。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>承载扫描结果：三维字符矩阵、尺寸、图例（符号 → 方块 ID）</li>
 *   <li>承载控制器元信息：世界坐标 / 注册名 / 朝向 / 是否为 HK3 自己的控制器</li>
 *   <li>承载舱口能力汇总：供 Pattern 生成时决定 autoAbilities 组合</li>
 *   <li>承载诊断信息：WARN 列表（creative 仓 / 非标准方块）</li>
 * </ul>
 *
 * <h3>坐标系统</h3>
 * grid[z][y][x] 中：
 * <ul>
 *   <li>x 轴 = 控制器正面视角下的"右手方向"</li>
 *   <li>y 轴 = 世界 Y 对应的相对偏移（控制器 Y 为 0）</li>
 *   <li>z 轴 = 控制器"背面方向"（z=0 是控制器前脸，z=depth-1 是最后排）</li>
 * </ul>
 *
 * <h3>不可变约定</h3>
 * 本类所有字段均为 final，grid 数组内容扫描完成后不再修改；legend 与 abilities 使用
 * 构造时冻结的 map（LinkedHashMap 可序化，迭代顺序稳定）。
 */
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
    /** 舱口能力汇总（决定 Pattern 中使用 autoAbilities 的组合） */
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
