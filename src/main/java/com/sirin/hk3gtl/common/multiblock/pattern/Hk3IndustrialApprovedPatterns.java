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
 * 【变更记录 #1】2026-10-15 01:12:48（内测5修订156）：正式接入批准的 I01 四阶 V8、I02–I08 V7 和 I09–I13 V6。
 * 删除：本轮工业入口对旧几何及任意能力通用槽的依赖；旧资源读取框架继续复用。
 * 新增：精确状态、实际主控和按工艺方向分组的六接口；必要能力共享全局最低数量。
 * 用途：壳体只封闭空余接口，不能冒充工作仓；玩家电网供能继续无需普通 GT 能源仓。
 */
public final class Hk3IndustrialApprovedPatterns {
    private static final Set<String> INDUSTRIAL_IDS = Set.of("i01", "i01_2", "i01_3", "i01_4",
            "i02", "i03", "i04", "i05", "i06", "i07", "i08", "i09", "i10", "i11", "i12", "i13");
    private Hk3IndustrialApprovedPatterns() {}

    /** 朝北时局部 X 向东、Y 向上、Z 向南；空腔和维护通道均严格要求空气。 */
    public static BlockPattern create(MultiblockMachineDefinition definition, String id) {
        if (!INDUSTRIAL_IDS.contains(id)) throw new IllegalArgumentException("非工业批准入口：" + id);
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
            int[] pos = cell.pos();
            cells[pos[2]][pos[1]][pos[0]] = symbol;
        }
        if (controllers != 1 || data.ports().size() != 6)
            throw new IllegalStateException("批准主控或六接口异常：" + id);
        Map<String, Character> groups = new LinkedHashMap<>();
        for (var port : data.ports()) {
            if (Arrays.equals(port.pos(), controller) || !"north".equals(port.face()))
                throw new IllegalStateException("批准接口方向或位置异常：" + id + "/" + port.id());
            char symbol = groups.computeIfAbsent(port.group(), ignored -> (char) ('a' + groups.size()));
            int[] pos = port.pos();
            cells[pos[2]][pos[1]][pos[0]] = symbol;
        }
        var builder = FactoryBlockPattern.start(RIGHT, UP, BACK);
        for (var slice : cells) {
            String[] rows = new String[size[1]];
            for (int y = 0; y < rows.length; y++) rows[y] = new String(slice[y]);
            builder.aisle(rows);
        }
        builder.where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('#', Hk3InterfacePredicates.clearance());
        for (var entry : palette.entrySet()) builder.where(entry.getValue(), Predicates.states(state(entry.getKey())));

        // 修订214：所有接口共享四种仓能力，位置不再限定方向；整机最低能力计数保持。
        boolean first = id.equals("i01"), dry = id.equals("i02") || id.equals("i07");
        var itemIn = ability(PartAbility.IMPORT_ITEMS, true);
        var itemOut = ability(PartAbility.EXPORT_ITEMS, !first);
        var fluidIn = ability(PartAbility.IMPORT_FLUIDS, !first && !dry);
        var fluidOut = ability(PartAbility.EXPORT_FLUIDS, !dry && !id.equals("i11"));
        var filler = Predicates.blocks(Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"));
        var parallel = Predicates.abilities(PartAbility.PARALLEL_HATCH).setMaxGlobalLimited(1).setPreviewCount(0);
        var universal = itemIn.or(itemOut).or(fluidIn).or(fluidOut).or(parallel).or(filler);
        for (var group : groups.entrySet()) {
            builder.where(group.getValue(), universal);
        }
        return builder.build();
    }

    private static TraceabilityPredicate ability(PartAbility ability, boolean required) {
        var predicate = Hk3InterfacePredicates.abilities(ability).setPreviewCount(required ? 1 : 0);
        return required ? predicate.setMinGlobalLimited(1) : predicate;
    }

    /** 完整解析批准状态；GT 的运行态切换由 states 谓词按 ActiveBlock 原生规则兼容。 */
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
