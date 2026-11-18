package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.*;

/**
 * 读取I14–I18批准逐格资源，生成严格空气、状态与真实仓能力的成型判定。
 */
public final class Hk3IndustrialExtensionPatterns {
    public static final Set<String> IDS = Set.of("i14", "i15", "i16", "i17", "i18");
    private Hk3IndustrialExtensionPatterns() {}

    public static BlockPattern create(MultiblockMachineDefinition definition, String id) {
        if (!IDS.contains(id)) throw new IllegalArgumentException("非工业扩展批准入口：" + id);
        var data = Hk3ApprovedArchitecture.get(id);
        int[] size = data.size(), controller = data.controller();
        char[][][] cells = new char[size[2]][size[1]][size[0]];
        for (var slice : cells) for (var row : slice) Arrays.fill(row, '#');
        Map<String, Character> palette = new LinkedHashMap<>();
        int controllers = 0;
        for (var cell : data.blocks()) {
            char symbol;
            if (Arrays.equals(cell.pos(), controller)) { symbol = 'S'; controllers++; }
            else symbol = palette.computeIfAbsent(cell.state(), ignored -> (char) (0xE000 + palette.size()));
            int[] p = cell.pos();
            cells[p[2]][p[1]][p[0]] = symbol;
        }
        if (controllers != 1) throw new IllegalStateException("批准主控数量异常：" + id);
        var builder = FactoryBlockPattern.start(RIGHT, UP, BACK);
        for (var slice : cells) {
            String[] rows = new String[size[1]];
            for (int y = 0; y < rows.length; y++) rows[y] = new String(slice[y]);
            builder.aisle(rows);
        }
        builder.where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('#', Hk3InterfacePredicates.clearance());
        var itemIn = ability(PartAbility.IMPORT_ITEMS);
        var itemOut = ability(PartAbility.EXPORT_ITEMS);
        var fluidIn = ability(PartAbility.IMPORT_FLUIDS);
        var fluidOut = ability(PartAbility.EXPORT_FLUIDS);
        var universal = Hk3InterfacePredicates.interfaces(itemIn.or(itemOut).or(fluidIn).or(fluidOut));
        for (var entry : palette.entrySet())
            builder.where(entry.getValue(), Predicates.states(state(entry.getKey())).or(universal));
        return builder.build();
    }

    private static TraceabilityPredicate ability(PartAbility ability) {
        return Hk3InterfacePredicates.abilities(ability).setMinGlobalLimited(1).setPreviewCount(1);
    }

    private static BlockState state(String text) {
        int start = text.indexOf('[');
        var block = Hk3StructureBlocks.require(start < 0 ? text : text.substring(0, start));
        BlockState result = block.defaultBlockState();
        if (start < 0) return result;
        if (!text.endsWith("]")) throw new IllegalStateException("非法批准状态：" + text);
        for (String entry : text.substring(start + 1, text.length() - 1).split(",")) {
            String[] pair = entry.split("=", 2);
            if (pair.length != 2) throw new IllegalStateException("非法批准属性：" + text);
            Property<?> property = block.getStateDefinition().getProperty(pair[0]);
            if (property == null) throw new IllegalStateException("批准材料缺少属性：" + text);
            result = property(result, property, pair[1]);
        }
        return result;
    }

    private static <T extends Comparable<T>> BlockState property(BlockState state, Property<T> property, String value) {
        T parsed = property.getValue(value).orElseThrow(() -> new IllegalStateException("非法批准属性值：" + value));
        return state.setValue(property, parsed);
    }
}
