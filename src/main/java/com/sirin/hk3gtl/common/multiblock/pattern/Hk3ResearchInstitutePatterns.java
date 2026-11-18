package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;

import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.BACK;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.RIGHT;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.UP;

 






/**
 * 五阶研究所正式成型模板。
 *
 * <p>建筑快照由 {@link Hk3ApprovedArchitecture} 读取；这里仅把已批准的逐格外观
 * 编译成 GTCEu Pattern。钻石核心被真实研究所控制器替换，六个外观接口默认仍是
 * 工业机壳，也可以由崩坏能能力部件替换，但不会凭外观强制物品、流体或能源仓。</p>
 */
public final class Hk3ResearchInstitutePatterns {
    private Hk3ResearchInstitutePatterns() {}

    /** S01–S05 共用同一坐标语义：X 向东、Y 向上、Z 向南，控制坞朝北。 */
    public static BlockPattern create(MultiblockMachineDefinition definition, String id) {
        if (!id.matches("s0[1-5]")) {
            throw new IllegalArgumentException("未知研究所建筑：" + id);
        }
        var layout = Hk3ApprovedArchitecture.get(id);
        int[] size = layout.size();
        char[][][] cells = new char[size[2]][size[1]][size[0]];
        for (var slice : cells) {
            for (var row : slice) Arrays.fill(row, '#');
        }

        Map<String, Character> palette = new LinkedHashMap<>();
        int[] controller = layout.controller();
        for (var cell : layout.blocks()) {
            int[] p = cell.pos();
            char symbol;
            if (Arrays.equals(p, controller)) {
                symbol = 'S';
            } else if ("minecraft:diamond_block".equals(cell.state())) {
                throw new IllegalStateException("研究所快照包含额外钻石核心：" + id);
            } else {
                symbol = palette.computeIfAbsent(cell.state(), state -> nextSymbol(palette));
            }
            cells[p[2]][p[1]][p[0]] = symbol;
        }

        var builder = FactoryBlockPattern.start(RIGHT, UP, BACK);
        for (char[][] slice : cells) {
            String[] rows = new String[size[1]];
            for (int y = 0; y < size[1]; y++) rows[y] = new String(slice[y]);
            builder.aisle(rows);
        }
        builder.where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('#', Hk3InterfacePredicates.clearance());
        var universal = Hk3InterfacePredicates.interfaces();
        for (var entry : palette.entrySet()) {
            String blockId = entry.getKey().split("\\[", 2)[0];
            builder.where(entry.getValue(), Predicates.blocks(Hk3StructureBlocks.require(blockId)).or(universal));
        }
        return builder.build();
    }

    private static char nextSymbol(Map<String, Character> palette) {
        int index = palette.size();
        // 私有区字符避免与结构字符冲突，且每个实际方块状态只占一个符号。
        if (index > 0xF8FF - 0xE000) {
            throw new IllegalStateException("研究所材料种类过多");
        }
        return (char) (0xE000 + index);
    }
}
