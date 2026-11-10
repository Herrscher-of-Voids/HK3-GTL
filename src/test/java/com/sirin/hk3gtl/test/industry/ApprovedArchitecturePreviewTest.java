package com.sirin.hk3gtl.test.industry;

import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitectureShapes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.IntTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.Tag;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.BitSet;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.function.Consumer;

/**
 * 【变更记录 #1】2026-10-15 02:00:40（内测5修订157）
 * 删除：无，不修改批准模板、正式尺寸或逐块继承验收。
 * 新增：21 个预览的完整坐标、空气兼容、实际仓室、主控朝向及损坏模板拒绝断言。
 * 修改：同一生产烘焙入口使用纯状态替身测试，不依赖游戏注册或客户端初始化。
 * 用途：防止稀疏预览造成转轴、裁剪、遗漏实体或误改批准几何。
 */
/**
 * 【变更记录 #2】2026-10-23T13:37:15+08:00（内测5修订175）
 * 删除：21形态预览旧总数与仅固定物品/流体方向组的限制；保留损坏模板回归。
 * 新增：26形态全体素回归，input/output接口组对真实仓方向的核验。
 * 修改：总实体数采用批准V2及原研究所快照的独立预期；空气共享与全部坐标检查保持。
 * 用途：确保新放置模板与JEI预览同源；不代表客户端或游戏运行验收。
 */
public final class ApprovedArchitecturePreviewTest {
    /**
     * 【变更记录 #3】2026-10-26 20:50:18（修订177）
     * 删除：旧预览入口绑定全局集合与I05旧版总量；新增：原26形态范围与I05 V5独立总量预期。
     * 修改：I05高度39变49、实体7233变7519，其余逐体素材料、主控、仓室与损坏模板回归保留。
     * 用途：验收真实批准V5，避免新增十台改变旧26形态的独立预期。
     */
    private static final String AIR = new String("minecraft:air");

    public static void main(String[] args) throws Exception {
        long totalVolume = 0, totalSolids = 0;
        var legacyIds = ApprovedArchitectureTest.legacyIds();
        check(legacyIds.size() == 26, "原批准预览形态数量");
        for (String id : legacyIds) {
            var layout = Hk3ApprovedArchitecture.get(id);
            CompoundTag template;
            try (var stream = ApprovedArchitecturePreviewTest.class.getResourceAsStream(
                    "/data/hk3gtl/structures/approved/" + id + ".nbt")) {
                check(stream != null, "缺少正式预览模板：" + id);
                template = NbtIo.readCompressed(stream);
            }
            Map<CompoundTag, String> palette = new IdentityHashMap<>();
            for (var raw : template.getList("palette", Tag.TAG_COMPOUND))
                palette.put((CompoundTag) raw, stateText((CompoundTag) raw));
            String[][][] sparse = Hk3ApprovedArchitectureShapes.bakeTemplate(template, String.class, null,
                    (state, entity) -> palette.get(state));
            String[][][] dense = Hk3ApprovedArchitectureShapes.bakeTemplate(template, String.class, AIR,
                    (state, entity) -> palette.get(state));
            int[] size = layout.size(), controller = layout.controller();
            check(sparse.length == size[0] && sparse[0].length == size[1] && sparse[0][0].length == size[2],
                    "预览转轴或裁剪尺寸：" + id);
            int volume = size[0] * size[1] * size[2];
            BitSet expected = new BitSet(volume), ports = new BitSet(volume);
            for (var port : layout.ports()) ports.set(index(port.pos(), size));
            for (var block : layout.blocks()) {
                int[] p = block.pos();
                expected.set(index(p, size));
                check(sparse[p[0]][p[1]][p[2]] != null, "预览丢失批准方块：" + id + Arrays.toString(p));
                if (!Arrays.equals(p, controller) && !ports.get(index(p, size)))
                    check(block.state().equals(sparse[p[0]][p[1]][p[2]]),
                            "预览变更批准材料或坐标：" + id + Arrays.toString(p));
            }
            int solids = 0;
            for (int x = 0; x < size[0]; x++) for (int y = 0; y < size[1]; y++) for (int z = 0; z < size[2]; z++) {
                boolean solid = expected.get((x * size[1] + y) * size[2] + z);
                if (solid) {
                    solids++;
                    check(sparse[x][y][z] != null && sparse[x][y][z] == dense[x][y][z], "兼容模式改变实体：" + id);
                } else {
                    check(sparse[x][y][z] == null, "稀疏模式生成额外空气或建筑：" + id);
                    check(dense[x][y][z] == AIR, "普通 GT 空气未使用共享实例：" + id);
                }
            }
            check(solids == layout.blocks().size(), "预览实体数量：" + id);
            try (var stream = ApprovedArchitecturePreviewTest.class.getResourceAsStream(
                    "/data/hk3gtl/structures/approved/" + id + ".json")) {
                check(stream != null, "缺少正式模板清单：" + id);
                var manifest = JsonParser.parseString(new String(stream.readAllBytes(), StandardCharsets.UTF_8)).getAsJsonObject();
                check((manifest.get("machine").getAsString() + "[facing=north]")
                        .equals(sparse[controller[0]][controller[1]][controller[2]]), "预览主控 ID 或朝向：" + id);
                Set<String> abilities = new HashSet<>();
                for (var port : layout.ports()) {
                    int[] p = port.pos();
                    String state = sparse[p[0]][p[1]][p[2]];
                    if (state.equals("hk3gtl:industrial_port_casing")) continue;
                    check(state.endsWith("[facing=north]"), "预览真实仓室朝向：" + id + port.id());
                    String ability = switch (state.substring(0, state.indexOf('['))) {
                        case "gtceu:max_input_bus" -> "item_input";
                        case "gtceu:max_output_bus" -> "item_output";
                        case "gtceu:max_input_hatch", "gtceu:max_input_hatch_4x" -> "fluid_input";
                        case "gtceu:max_output_hatch", "gtceu:max_output_hatch_4x" -> "fluid_output";
                        default -> throw new AssertionError("预览包含未知工作仓：" + id + state);
                    };
                    check(port.group().equals(ability) || (port.group().equals("item") && ability.startsWith("item_"))
                            || (port.group().equals("fluid") && ability.startsWith("fluid_"))
                            || (port.group().equals("input") && ability.endsWith("_input"))
                            || (port.group().equals("output") && ability.endsWith("_output")), "预览工作仓接口组：" + id);
                    abilities.add(ability);
                }
                if (manifest.has("required_abilities")) {
                    for (var required : manifest.getAsJsonArray("required_abilities"))
                        check(abilities.contains(required.getAsString()), "预览缺少实际工作能力：" + id);
                } else {
                    check(id.startsWith("s") && abilities.isEmpty(), "研究所预览加入额外工作仓：" + id);
                }
            }
            totalVolume += volume;
            totalSolids += solids;
        }
        check(totalVolume == 3804587 && totalSolids == 437765, "原26形态含I05 V5预览总体积或实体总数漂移");
        checkMalformedTemplates();
        System.out.println("26 个批准预览通过：完整体积=" + totalVolume + "，实体=" + totalSolids
                + "，稀疏模式省略空气=" + (totalVolume - totalSolids));
    }

    private static void checkMalformedTemplates() {
        rejects(template -> template.getList("size", Tag.TAG_INT).set(0, IntTag.valueOf(0)), "零尺寸");
        rejects(template -> template.getList("blocks", Tag.TAG_COMPOUND).add(
                template.getList("blocks", Tag.TAG_COMPOUND).getCompound(0).copy()), "重复坐标");
        rejects(template -> template.getList("blocks", Tag.TAG_COMPOUND).getCompound(0)
                .getList("pos", Tag.TAG_INT).set(0, IntTag.valueOf(3)), "越界坐标");
        rejects(template -> template.getList("blocks", Tag.TAG_COMPOUND).getCompound(0).putInt("state", 1), "越界状态");
        rejects(template -> template.getList("blocks", Tag.TAG_COMPOUND).getCompound(0).remove("state"), "缺少状态");
        rejects(template -> template.getList("blocks", Tag.TAG_COMPOUND).getCompound(0).putString("nbt", "坏数据"), "实体标签类型");
        var template = smallTemplate();
        var entity = new CompoundTag();
        entity.putString("标记", "保留原始方块实体数据");
        template.getList("blocks", Tag.TAG_COMPOUND).getCompound(0).put("nbt", entity);
        String[][][] shape = Hk3ApprovedArchitectureShapes.bakeTemplate(template, String.class, null,
                (state, tag) -> { check(tag != null && entity.equals(tag), "方块实体数据丢失"); return state.getString("Name"); });
        check(shape[2][1][0].equals("minecraft:stone") && shape[0][1][2] == null, "非对称模板转轴");
    }

    private static void rejects(Consumer<CompoundTag> damage, String description) {
        var template = smallTemplate();
        damage.accept(template);
        try {
            Hk3ApprovedArchitectureShapes.bakeTemplate(template, String.class, null, (state, tag) -> state.getString("Name"));
        } catch (IllegalStateException expected) {
            return;
        }
        throw new AssertionError("损坏模板未被拒绝：" + description);
    }

    private static CompoundTag smallTemplate() {
        var template = new CompoundTag();
        template.put("size", ints(3, 2, 3));
        var state = new CompoundTag(); state.putString("Name", "minecraft:stone");
        var palette = new ListTag(); palette.add(state); template.put("palette", palette);
        var block = new CompoundTag(); block.put("pos", ints(2, 1, 0)); block.putInt("state", 0);
        var blocks = new ListTag(); blocks.add(block); template.put("blocks", blocks);
        return template;
    }

    private static ListTag ints(int... values) {
        var list = new ListTag();
        for (int value : values) list.add(IntTag.valueOf(value));
        return list;
    }

    private static String stateText(CompoundTag state) {
        String text = state.getString("Name");
        var properties = state.getCompound("Properties");
        if (properties.isEmpty()) return text;
        var pairs = new java.util.ArrayList<String>();
        for (String key : new TreeSet<>(properties.getAllKeys())) pairs.add(key + "=" + properties.getString(key));
        return text + "[" + String.join(",", pairs) + "]";
    }

    private static int index(int[] p, int[] size) { return (p[0] * size[1] + p[1]) * size[2] + p[2]; }
    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
}
