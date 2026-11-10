package com.sirin.hk3gtl.test.industry;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LateIndustrialPatterns;
import com.sirin.hk3gtl.common.research.Hk3IndustrialExtensionPolicy;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;



/**
 * 【文件职责】低内存逐格核验第8批正式布局与完整游戏预览，避免展开百万NBT复合对象。
 * 【变更记录 #1】2026-10-27（修订180）：新增五台批准V1完整坐标、材料、仓室及任务边界回归。
 */
/**
 * 【变更记录 #2】2026-10-27 22:31:22（第2次备注 · 内测5修订181）
 * - 删除：无，第8批五台逐格比较继续执行。
 * - 新增：第9批五台的完整布局、端口、主控及紧凑预览回归，排除未批准I37。
 * - 修改：正式计数为46形态、20台巨构，按批次分别验证修订180与181。
 * - 用途：覆盖新旧资源完整性及I38超过255层的实际高度，不以静态通过冒充游戏验收。
 */
public final class BatchEightArchitectureTest {
    // 2026-10-30：正式数量随第10批扩为52/26，逐格核验供本批复用，避免重复加载千万级布局。
    public static void main(String[] args) throws Exception {
        long blocks = 0;
        for (int number = 29; number <= 33; number++) blocks += verify("i" + number, 180);
        for (String key : List.of("i34", "i35", "i36", "i38", "i39")) blocks += verify(key, 181);
        check(Hk3ApprovedArchitecture.IDS.size() == 52, "正式形态数量应为52");
        check(Hk3LateIndustrialPatterns.IDS.size() == 26, "巨构正式Pattern数量应为26");
        check(!Hk3ApprovedArchitecture.IDS.contains("i37") && !Hk3LateIndustrialPatterns.IDS.contains("i37"),
                "未批准I37不得随批接入");
        System.out.println("第8–9批10台完整布局、真实仓室及预览逐格通过：" + blocks + "块；不代表游戏内验收。");
    }

    static long verify(String key, int revision) throws Exception {
        return verify(key, revision, layout -> {});
    }

    static long verify(String key, int revision, java.util.function.Consumer<Hk3ApprovedArchitecture.Layout> validate) throws Exception {
        check(Hk3LateIndustrialPatterns.IDS.contains(key), "未接入正式Pattern：" + key);
        String role = key.toUpperCase(Locale.ROOT);
        check(!Hk3IndustrialExtensionPolicy.permits(role, true), "暂定工艺被开放：" + key);
        check(Hk3IndustrialExtensionPolicy.permits(role, false), "误锁已批准工艺入口：" + key);
        var layout = Hk3ApprovedArchitecture.get(key);
        validate.accept(layout);
        JsonObject manifest;
        try (var stream = BatchEightArchitectureTest.class.getResourceAsStream(
                "/data/hk3gtl/structures/approved/" + key + ".json")) {
            check(stream != null, "缺少正式元数据：" + key);
            manifest = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
        }
        check(!manifest.get("game_verified").getAsBoolean(), "不可预记游戏验收：" + key);
        check(manifest.get("revision").getAsInt() == revision, "本批修订错误：" + key);
        if (key.equals("i38")) check(layout.size()[1] == 283, "I38批准高度不得截成255层");
        check(layout.blocks().size() == manifest.get("blocks").getAsInt(), "实体数不一致：" + key);
        String machine = manifest.get("machine").getAsString();
        check(machine.startsWith("hk3gtl:" + key + "_"), "控制器身份错误：" + key);
        var hatches = manifest.getAsJsonObject("installed_hatches");
        Map<Long, Hk3ApprovedArchitecture.Port> ports = new HashMap<>();
        for (var port : layout.ports()) check(ports.put(pack(port.pos()), port) == null, "重复接口：" + key);
        int[] cursor = {0}, controllers = {0};
        Set<String> seen = new HashSet<>();
        Hk3LargeArchitectureShapes.Header[] header = {null};
        try (var stream = BatchEightArchitectureTest.class.getResourceAsStream(
                "/data/hk3gtl/structures/approved_preview/" + key + ".bin.gz")) {
            check(stream != null, "缺少完整预览：" + key);
            Hk3LargeArchitectureShapes.read(stream, value -> {
                header[0] = value;
                check(Arrays.equals(new int[]{value.width(), value.height(), value.depth()}, layout.size()), "预览尺寸改变：" + key);
                check(Arrays.equals(new int[]{value.controllerX(), value.controllerY(), value.controllerZ()}, layout.controller()), "预览主控坐标改变：" + key);
                check(value.count() == layout.blocks().size(), "预览实体被缩减：" + key);
            }, (linear, paletteIndex, entity) -> {
                var cell = layout.blocks().get(cursor[0]++);
                int[] pos = cell.pos();
                var value = header[0];
                check(linear == value.linear(pos[0], pos[1], pos[2]), "预览坐标或顺序改变：" + key);
                String expected = cell.state(), face = null;
                if (Arrays.equals(pos, layout.controller())) {
                    controllers[0]++;
                    check(expected.equals(machine), "正式布局仍为主控占位：" + key);
                    face = "north";
                } else if (ports.containsKey(pack(pos))) {
                    var port = ports.get(pack(pos));
                    seen.add(port.id());
                    check(expected.equals("hk3gtl:industrial_port_casing"), "原位接口壳错误：" + key);
                    if (hatches.has(port.id())) {
                        expected = switch (hatches.get(port.id()).getAsString()) {
                            case "item_input" -> "gtceu:max_input_bus";
                            case "item_output" -> "gtceu:max_output_bus";
                            case "fluid_input" -> "gtceu:max_input_hatch";
                            case "fluid_output" -> "gtceu:max_output_hatch";
                            default -> throw new AssertionError("未知真实仓能力：" + port.id());
                        };
                        face = port.face();
                    }
                }
                if (face != null) {
                    check(entity != null && entity.getString("id").equals(expected), "主控或仓室实体身份错误：" + key);
                    expected += "[facing=" + face + "]";
                } else check(entity == null, "普通建材被附加实体：" + key);
                check(value.palette().get(paletteIndex).equals(expected), "预览建材或仓室状态错误：" + key + "/" + cursor[0]);
            });
        }
        check(cursor[0] == layout.blocks().size() && controllers[0] == 1 && seen.size() == ports.size(), "主控、接口或实体遗漏：" + key);
        System.out.println(key + "：" + cursor[0] + "块，" + seen.size() + "原位接口，完整预览通过");
        return cursor[0];
    }

    private static long pack(int[] p) { return ((long) p[0] << 42) | ((long) p[1] << 21) | p[2]; }
    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
}
