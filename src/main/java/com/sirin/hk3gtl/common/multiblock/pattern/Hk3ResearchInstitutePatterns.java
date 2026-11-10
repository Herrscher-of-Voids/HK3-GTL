package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartAbility;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;

import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.BACK;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.RIGHT;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.UP;

/**
 * 【变更记录 #1】2026-10-15 01:06:24（第1次备注 · 内测5修订156）
 * 删除：无；批准院区原始交付与归档保持不变。
 * 新增：五阶研究所专用逐格Pattern编译入口，真实控制器和六格可选崩坏能接口谓词。
 * 修改：正式结构读取batch-05确认资源，全部其余方块按注册ID匹配，空腔严格为空气。
 * 用途：把已批准科研院区接入GT成型，保留玩家背包付款和无线电网扣电；大穹顶扫描性能待游戏实测。
 */
/**
 * 五阶研究所正式成型模板。
 *
 * <p>建筑快照由 {@link Hk3ApprovedArchitecture} 读取；这里仅把已批准的逐格外观
 * 编译成 GTCEu Pattern。钻石核心被真实研究所控制器替换，六个外观接口默认仍是
 * 工业机壳，也可以由崩坏能能力部件替换，但不会凭外观强制物品、流体或能源仓。</p>
 */
public final class Hk3ResearchInstitutePatterns {
    private static final String PORT = "hk3gtl:industrial_port_casing";

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
            } else if (PORT.equals(cell.state())) {
                symbol = 'H';
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
        for (var entry : palette.entrySet()) {
            String blockId = entry.getKey().split("\\[", 2)[0];
            builder.where(entry.getValue(), Predicates.blocks(Hk3StructureBlocks.require(blockId)));
        }

        // 研究机的物品和材料由玩家交互处理；接口只保留外观及可选崩坏能输入能力。
        builder.where('H', Predicates.blocks(Hk3StructureBlocks.require(PORT))
                .or(Hk3InterfacePredicates.abilities(com.gregtechceu.gtceu.api.machine.multiblock.PartAbility.IMPORT_ITEMS,
                        com.gregtechceu.gtceu.api.machine.multiblock.PartAbility.EXPORT_ITEMS,
                        com.gregtechceu.gtceu.api.machine.multiblock.PartAbility.IMPORT_FLUIDS,
                        com.gregtechceu.gtceu.api.machine.multiblock.PartAbility.EXPORT_FLUIDS).setPreviewCount(0))
                .or(Predicates.abilities(Hk3PartAbility.HONKAI_ENERGY_INPUT,
                        Hk3PartAbility.WIRELESS_HONKAI_INPUT).setPreviewCount(0)));
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
