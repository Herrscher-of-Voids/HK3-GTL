package com.sirin.hk3gtl.test.industry;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.Tag;
import java.io.InputStreamReader;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.zip.GZIPOutputStream;



/**
 * 【文件职责】独立核验十份正式资源、控制器/接口替换与巨构通知范围。
 * 【变更记录 #1】2026-10-26 20:48:30（第1次备注 · 内测5修订177）
 * 删除：无。新增：逐实体坐标与材质、端口身份/外朝向、空气边界和区块代表点断言。
 * 修改：按单台释放NBT，不构建包围盒对象数组；用途：验证正式接入，不冒充游戏运行。
 * 【变更记录 #2】2026-10-26 21:57:03（修订178）
 * 删除：十台机器完整预览未被回归覆盖的缺口；新增：7297531条紧凑预览对正式NBT逐坐标、状态与实体数据比较。
 * 修改：测试共用生产串流解码入口且不额外构建大数组；用途：保证预览无裁剪、无替身并拒绝重复或截断记录。
 * 【变更记录 #3】2026-10-26 22:36:20（修订179）
 * 删除：巨构继承单主控预览回退的覆盖缺口；新增：完整getPreview入口必须由巨构类声明的断言。
 * 修改：无；用途：防止实际建筑正确而游戏预览退化成单个控制器。
 */
/**
 * 【变更记录 #4】2026-10-27 22:31:22（第4次备注 · 内测5修订181）
 * - 删除：无，原十台正式模板、真实仓室及损坏预览回归保留。
 * - 新增：283层紧凑预览顶层和跨255层通知边界断言。
 * - 修改：批准形态总数跟随第9批增加至46，不引入I37。
 * - 用途：证明生产解码与边界坐标没有8位高度截断，仍不宣称实机成型已通过。
 */
public final class LateIndustrialArchitectureTest {
    // 2026-10-30：正式形态计数跟随第10批扩为52；旧十台逐格验收保持。
    public static void main(String[] args) throws Exception {
        check(Hk3LargeStructurePattern.class.getDeclaredMethod("getPreview", int[].class).getReturnType()
                == com.lowdragmc.lowdraglib.utils.BlockInfo[][][].class, "巨构Pattern不可继承单主控预览回退");
        check(Hk3ApprovedArchitecture.IDS.size() == 52, "正式结构应有52种形态");
        long total = 0;
        for (int number = 19; number <= 28; number++) total += verify("i" + number);
        checkMalformedCompact();
        checkTallCompact();
        var bounds = new Hk3LargeStructurePattern.Bounds(new BlockPos(-17, -4, -1), new BlockPos(18, 210, 33));
        check(bounds.contains(new BlockPos(-17, -4, -1)) && bounds.contains(new BlockPos(18, 210, 33)), "边界实体被漏掉");
        check(bounds.contains(new BlockPos(0, 120, 0)), "内部空气无法通知");
        for (var pos : List.of(new BlockPos(-18, 0, 0), new BlockPos(19, 0, 0),
                new BlockPos(0, -5, 0), new BlockPos(0, 211, 0), new BlockPos(0, 0, -2), new BlockPos(0, 0, 34)))
            check(!bounds.contains(pos), "边界外方块被误认为结构");
        check(bounds.chunkRepresentatives().size() == 16, "跨正负坐标区块索引遗漏");
        check(new HashSet<>(bounds.chunkRepresentatives()).size() == 16, "区块代表点重复");
        System.out.println("I19–I28逐实体资源与正式仓室通过：" + total + "块；完整空气边界通知范围通过。实机尚未验收。");
    }

    private static int verify(String id) throws Exception {
        var data = Hk3ApprovedArchitecture.get(id);
        JsonObject manifest;
        try (var stream = LateIndustrialArchitectureTest.class.getResourceAsStream("/data/hk3gtl/structures/approved/" + id + ".json")) {
            check(stream != null, "缺少正式元数据：" + id);
            manifest = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
        }
        CompoundTag template;
        try (var stream = LateIndustrialArchitectureTest.class.getResourceAsStream("/data/hk3gtl/structures/approved/" + id + ".nbt")) {
            check(stream != null, "缺少正式模板：" + id);
            template = NbtIo.readCompressed(stream);
        }
        var size = template.getList("size", Tag.TAG_INT);
        for (int axis = 0; axis < 3; axis++) check(size.getInt(axis) == data.size()[axis], "尺寸不一致：" + id);
        String machine = manifest.get("machine").getAsString();
        check(machine.startsWith("hk3gtl:" + id + "_"), "控制器身份不符：" + id);
        check(!manifest.get("game_verified").getAsBoolean(), "不可预宣称实机通过：" + id);
        Map<Long, Hk3ApprovedArchitecture.Port> ports = new HashMap<>();
        for (var port : data.ports()) check(ports.put(pack(port.pos()), port) == null, "重复接口：" + id);
        var hatches = manifest.getAsJsonObject("installed_hatches");
        var palette = template.getList("palette", Tag.TAG_COMPOUND);
        var blocks = template.getList("blocks", Tag.TAG_COMPOUND);
        check(blocks.size() == data.blocks().size(), "实体数量改变：" + id);
        String[] texts = new String[palette.size()];
        for (int index = 0; index < texts.length; index++) texts[index] = state(palette.getCompound(index));
        int controllers = 0;
        Set<String> seen = new HashSet<>();
        for (int index = 0; index < blocks.size(); index++) {
            var block = blocks.getCompound(index);
            var pos = block.getList("pos", Tag.TAG_INT);
            int[] p = {pos.getInt(0), pos.getInt(1), pos.getInt(2)};
            var cell = data.blocks().get(index);
            check(Arrays.equals(p, cell.pos()), "坐标或顺序被改变：" + id + "/" + index);
            int stateId = block.getInt("state");
            var entry = palette.getCompound(stateId);
            if (Arrays.equals(p, data.controller())) {
                controllers++;
                check(cell.state().equals(machine), "正式布局仍为主控预览占位：" + id);
                check(entry.getString("Name").equals(machine), "正式主控未替换：" + id);
                check(block.getCompound("nbt").getString("id").equals(machine), "主控方块实体类型错误：" + id);
                check(entry.getCompound("Properties").getString("facing").equals("north"), "主控未北向：" + id);
            } else if (ports.containsKey(pack(p))) {
                var port = ports.get(pack(p)); seen.add(port.id());
                check(cell.state().equals("hk3gtl:industrial_port_casing"), "接口蓝图占位材料不符：" + id);
                String expected = hatches.has(port.id()) ? switch (hatches.get(port.id()).getAsString()) {
                    case "item_input" -> "gtceu:max_input_bus";
                    case "item_output" -> "gtceu:max_output_bus";
                    case "fluid_input" -> "gtceu:max_input_hatch";
                    case "fluid_output" -> "gtceu:max_output_hatch";
                    default -> throw new AssertionError("未知实际仓能力：" + port.id());
                } : "hk3gtl:industrial_port_casing";
                check(entry.getString("Name").equals(expected), "接口能力位置错配：" + id + "/" + port.id());
                if (!expected.equals("hk3gtl:industrial_port_casing")) {
                    check(entry.getCompound("Properties").getString("facing").equals(port.face()), "接口未朝批准外立面：" + id + "/" + port.id());
                    check(block.getCompound("nbt").getString("id").equals(expected), "接口方块实体类型错误：" + id + "/" + port.id());
                }
            } else check(texts[stateId].equals(cell.state()), "普通建筑状态被改变：" + id + "/" + index);
        }
        check(controllers == 1 && seen.size() == ports.size(), "主控或接口缺格：" + id);
        verifyCompact(id, data, template, texts);
        System.out.println(id + "：" + blocks.size() + "块、" + ports.size() + "接口正式身份通过");
        return blocks.size();
    }

    private static void verifyCompact(String id, Hk3ApprovedArchitecture.Layout data, CompoundTag template,
                                      String[] states) throws Exception {
        var blocks = template.getList("blocks", Tag.TAG_COMPOUND);
        int[] cursor = {0};
        Hk3LargeArchitectureShapes.Header[] header = {null};
        try (var stream = LateIndustrialArchitectureTest.class.getResourceAsStream(
                "/data/hk3gtl/structures/approved_preview/" + id + ".bin.gz")) {
            check(stream != null, "缺少完整巨构预览：" + id);
            Hk3LargeArchitectureShapes.read(stream, value -> {
                header[0] = value;
                check(Arrays.equals(new int[]{value.width(), value.height(), value.depth()}, data.size()), "预览尺寸或轴改变：" + id);
                check(Arrays.equals(new int[]{value.controllerX(), value.controllerY(), value.controllerZ()}, data.controller()), "预览主控坐标改变：" + id);
                check(value.count() == blocks.size(), "预览实体被缩减：" + id);
            }, (linear, palette, entity) -> {
                var expected = blocks.getCompound(cursor[0]++);
                var pos = expected.getList("pos", Tag.TAG_INT);
                var value = header[0];
                check(linear == value.linear(pos.getInt(0), pos.getInt(1), pos.getInt(2)), "预览坐标或顺序被改变：" + id);
                check(value.palette().get(palette).equals(states[expected.getInt("state")]), "预览普通建材或实际仓室状态改变：" + id);
                check(expected.contains("nbt", Tag.TAG_COMPOUND) ? expected.getCompound("nbt").equals(entity) : entity == null,
                        "预览主控或仓室NBT丢失：" + id);
            });
        }
        check(cursor[0] == blocks.size(), "预览没有覆盖完整实体集合：" + id);
    }

    private static void checkMalformedCompact() throws Exception {
        for (String damage : List.of("重复", "越界", "状态", "缺主控", "截断", "尾部")) {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            try (DataOutputStream out = new DataOutputStream(new GZIPOutputStream(bytes))) {
                out.writeInt(0x484B3350); out.writeInt(1);
                out.writeInt(2); out.writeInt(1); out.writeInt(1);
                out.writeInt(0); out.writeInt(0); out.writeInt(0);
                out.writeInt(damage.equals("重复") ? 2 : 1);
                out.writeShort(1); out.writeUTF("minecraft:stone");
                if (!damage.equals("截断")) {
                    out.writeInt(damage.equals("越界") ? 2 : damage.equals("缺主控") ? 1 : 0);
                    out.writeShort(damage.equals("状态") ? 1 : 0); out.writeInt(0);
                }
                if (damage.equals("重复")) { out.writeInt(0); out.writeShort(0); out.writeInt(0); }
                if (damage.equals("尾部")) out.writeByte(1);
            }
            try {
                Hk3LargeArchitectureShapes.read(new ByteArrayInputStream(bytes.toByteArray()), value -> {}, (linear, palette, entity) -> {});
                throw new AssertionError("损坏巨构预览未拒绝：" + damage);
            } catch (IOException expected) { }
        }
    }

    private static void checkTallCompact() throws Exception {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (DataOutputStream out = new DataOutputStream(new GZIPOutputStream(bytes))) {
            out.writeInt(0x484B3350); out.writeInt(1);
            out.writeInt(1); out.writeInt(283); out.writeInt(1);
            out.writeInt(0); out.writeInt(0); out.writeInt(0); out.writeInt(2);
            out.writeShort(1); out.writeUTF("minecraft:stone");
            for (int y : new int[]{0, 282}) { out.writeInt(y); out.writeShort(0); out.writeInt(0); }
        }
        Set<Integer> seen = new HashSet<>();
        Hk3LargeArchitectureShapes.read(new ByteArrayInputStream(bytes.toByteArray()), header -> {
            check(header.height() == 283 && header.volume() == 283, "完整预览高度发生截断");
            check(header.linear(0, 282, 0) == 282, "超过255层的预览坐标发生截断");
        }, (linear, palette, entity) -> seen.add(linear));
        check(seen.equals(Set.of(0, 282)), "完整预览丢失283层顶点");
        var tall = new Hk3LargeStructurePattern.Bounds(new BlockPos(0, -10, 0), new BlockPos(0, 272, 0));
        check(tall.contains(new BlockPos(0, 272, 0)) && !tall.contains(new BlockPos(0, 273, 0)),
                "严格Pattern通知边界发生高度截断");
    }

    private static long pack(int[] p) { return ((long) p[0] << 42) | ((long) p[1] << 21) | p[2]; }
    private static String state(CompoundTag palette) {
        String result = palette.getString("Name");
        var properties = palette.getCompound("Properties");
        if (properties.isEmpty()) return result;
        List<String> values = new ArrayList<>();
        for (String name : new TreeSet<>(properties.getAllKeys())) values.add(name + "=" + properties.getString(name));
        return result + "[" + String.join(",", values) + "]";
    }
    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
}
