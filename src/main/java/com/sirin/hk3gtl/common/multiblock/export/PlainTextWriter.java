package com.sirin.hk3gtl.common.multiblock.export;



import net.minecraft.resources.ResourceLocation;

import java.util.HashMap;
import java.util.Map;

/**
 * 生成人类可读的 {@code .txt} 结构可视化文件。
 *
 * <h3>输出内容</h3>
 * <ul>
 *   <li>头部元信息：名称、尺寸、控制器 ID、控制器坐标、朝向</li>
 *   <li>警告列表（WARN）：creative 仓、非本模组控制器等需要玩家手动确认的项</li>
 *   <li>方块图例（每个符号 = 注册 ID + 是否 GT 舱口）</li>
 *   <li>按 aisle 顺序打印的三维字符矩阵，每个 aisle 上方标注 Z 层号（与 FactoryBlockPattern 对齐）</li>
 *   <li>方块出现次数统计（按符号降序）</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增可视化维度：在生成正文区追加段落，建议保持以 {@code ==} 包裹段标题</li>
 *   <li>输出顺序：aisle 按 z 递增（与 FactoryBlockPattern 的 aisle 调用顺序一致，便于对照）</li>
 * </ul>
 */
public final class PlainTextWriter {

    private PlainTextWriter() {}

    public static String render(ExportContext ctx) {
        StringBuilder sb = new StringBuilder(4096);
        sb.append("# ========= HK3GTL Structure Export =========\n");
        sb.append("# name            : ").append(ctx.exportName).append('\n');
        sb.append("# size (WxHxD)    : ").append(ctx.width).append('x').append(ctx.height)
                .append('x').append(ctx.depth).append('\n');
        sb.append("# controller id   : ").append(ctx.controllerId).append('\n');
        sb.append("# controller pos  : ").append(ctx.controllerWorldPos.toShortString()).append('\n');
        sb.append("# controller face : ").append(ctx.controllerFacing).append('\n');
        sb.append("# aisle convention: aisle[0] = back plane, aisle[depth-1] = controller front\n");
        sb.append("# ============================================\n\n");

        if (!ctx.warnings.isEmpty()) {
            sb.append("## WARN\n");
            for (String w : ctx.warnings) {
                sb.append(" - ").append(w).append('\n');
            }
            sb.append('\n');
        }

        sb.append("## Legend\n");
        sb.append("   ").append(SymbolAllocator.CONTROLLER_SYMBOL).append(" = controller (")
                .append(ctx.controllerId).append(")\n");
        sb.append("   ").append(SymbolAllocator.AIR_SYMBOL).append(" = air\n");
        for (Map.Entry<Character, ResourceLocation> e : ctx.legend.entrySet()) {
            char c = e.getKey();
            sb.append("   ").append(c).append(" = ").append(e.getValue());
            HatchAbilityMap.Ability ab = ctx.abilityBySymbol.get(c);
            if (ab != null) {
                sb.append("  [abilities → ").append(ab.partAbility()).append(']');
            }
            sb.append('\n');
        }
        sb.append('\n');

        sb.append("## Aisles\n");
        for (int z = 0; z < ctx.depth; z++) {
            boolean front = (z == ctx.depth - 1);
            sb.append("== Z=").append(z);
            if (front) sb.append("  (controller front plane)");
            sb.append(" ==\n");
            for (int y = ctx.height - 1; y >= 0; y--) {
                sb.append("   ").append(new String(ctx.grid[z][y])).append('\n');
            }
            sb.append('\n');
        }

        sb.append("## Block count\n");
        Map<Character, Integer> counts = countSymbols(ctx.grid);
        counts.entrySet().stream()
                .sorted((a, b) -> Integer.compare(b.getValue(), a.getValue()))
                .forEach(e -> sb.append("   ").append(e.getKey()).append(" : ")
                        .append(e.getValue()).append('\n'));

        return sb.toString();
    }

    private static Map<Character, Integer> countSymbols(char[][][] grid) {
        Map<Character, Integer> counts = new HashMap<>();
        for (char[][] layer : grid) {
            for (char[] row : layer) {
                for (char c : row) {
                    counts.merge(c, 1, Integer::sum);
                }
            }
        }
        return counts;
    }
}
