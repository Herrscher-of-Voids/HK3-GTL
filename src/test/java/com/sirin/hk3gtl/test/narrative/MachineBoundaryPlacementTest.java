package com.sirin.hk3gtl.test.narrative;

import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.easter.Hk3EggMachineBoundaryFacts;
import com.sirin.hk3gtl.common.easter.Hk3EggMachineBoundaryFacts.Box;
import com.sirin.hk3gtl.common.easter.Hk3EggMachineBoundaries;
import com.sirin.hk3gtl.common.easter.Hk3EggRules;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.ChunkPos;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.*;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

public final class MachineBoundaryPlacementTest {
    private static int checks;

    public static void main(String[] args) {
        var box = new Box(-95, 0, -20, 95, 122, 154);
        for (int[] pos : List.of(new int[]{99, 80, 150}, new int[]{-99, 0, -20}, new int[]{0, 126, 0},
                new int[]{0, -4, 0}, new int[]{0, 50, -24}, new int[]{0, 50, 158}, new int[]{97, 125, 0}))
            check(box.nearOutside(pos[0], pos[1], pos[2]), "外侧四格边界被漏判");
        for (int[] pos : List.of(new int[]{100, 80, 150}, new int[]{0, 127, 0}, new int[]{0, 0, 159},
                new int[]{98, 125, 0}, new int[]{95, 122, 154}, new int[]{0, 80, 50},
                new int[]{Integer.MAX_VALUE, 0, Integer.MIN_VALUE}))
            check(!box.nearOutside(pos[0], pos[1], pos[2]), "内部空腔、边界成员或超距位置误触发");
        String caster = "hk3gtl:soulium_polymerization_die_caster", reactor = "hk3gtl:i19_small_honkai_reactor";
        check(Hk3EggMachineBoundaryFacts.caseFor("minecraft:crafting_table", caster, true, false, box, 99, 80, 150) == 78,
                "远离控制器的真实外沿应触发工作台旁注");
        check(Hk3EggMachineBoundaryFacts.caseFor("minecraft:tnt", reactor, true, false, box, 99, 80, 150) == 80,
                "未点燃TNT方块应触发反应设备旁注");
        check(Hk3EggMachineBoundaryFacts.caseFor("minecraft:crafting_table", caster, false, false, box, 99, 80, 150) == 0,
                "未成型设备不能触发");
        check(Hk3EggMachineBoundaryFacts.caseFor("minecraft:tnt", reactor, true, true, box, 99, 80, 150) == 0,
                "失效成型缓存不能触发");
        check(Hk3EggMachineBoundaryFacts.caseFor("minecraft:tnt", reactor, true, false, null, 99, 80, 150) == 0,
                "缺真实边界时保持休眠");
        for (String block : List.of("minecraft:air", "minecraft:fire", "minecraft:stone", "minecraft:crafting_table"))
            check(Hk3EggMachineBoundaryFacts.layout(block, reactor) == null, "点燃、替换或错类方块不能冒充TNT放置");
        for (String machine : List.of("gtceu:large_chemical_reactor", "hk3gtl:honkai_reactor", "hk3gtl:i23_honkai_phase_transition_generator"))
            check(Hk3EggMachineBoundaryFacts.layout("minecraft:tnt", machine) == null, "旧ID及其他设备不得借用正式反应设备身份");
        verifyMetadataAndTurns();
        var bounds = new Hk3LargeStructurePattern.Bounds(new BlockPos(-190, 0, -190), new BlockPos(190, 200, 190));
        var farChunk = new ChunkPos(new BlockPos(190, 80, 190));
        check(bounds.chunkRepresentatives().stream().anyMatch(pos -> new ChunkPos(pos).equals(farChunk)),
                "巨构索引必须覆盖远离主控的外沿区块");
        verifyAttributionAndLocality();
        for (int id : List.of(78, 80)) {
            var rule = Hk3EggRules.all().stream().filter(r -> r.id().equals("E-EG-0" + id)).findFirst().orElseThrow();
            check(rule.matches("vanilla_case", Map.of("case", Integer.toString(id))), "新增批准条目未绑定真实事实");
            check(!rule.matches("block_placed", Map.of("case", Integer.toString(id))), "普通放置事件不能绕过设备边界核对");
        }
        System.out.println("设备外沿放置回归：" + checks + "项通过；自然触发仍待游戏验收。");
    }

    private static void verifyMetadataAndTurns() {
        for (String layout : List.of("i14", "i15", "i16", "i19", "i20", "i21", "i22")) {
            try (var input = MachineBoundaryPlacementTest.class.getResourceAsStream("/data/hk3gtl/structures/approved/" + layout + ".json")) {
                check(input != null, "缺少正式设备边界元数据：" + layout);
                var metadata = JsonParser.parseReader(new InputStreamReader(input, StandardCharsets.UTF_8)).getAsJsonObject();
                String block = layout.compareTo("i19") < 0 ? "minecraft:crafting_table" : "minecraft:tnt";
                check(layout.equals(Hk3EggMachineBoundaryFacts.layout(block, metadata.get("machine").getAsString())),
                        "批准元数据与正式设备角色不一致：" + layout);
                var sizeJson = metadata.getAsJsonArray("size_xyz");
                var controllerJson = metadata.getAsJsonArray("controller");
                int[] size = {sizeJson.get(0).getAsInt(), sizeJson.get(1).getAsInt(), sizeJson.get(2).getAsInt()};
                int[] controller = {controllerJson.get(0).getAsInt(), controllerJson.get(1).getAsInt(), controllerJson.get(2).getAsInt()};
                for (int turn = 0; turn < 4; turn++) {
                    var front = List.of(Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST).get(turn);
                    var box = Hk3EggMachineBoundaries.transform(size, controller, new BlockPos(1234, 64, -2222), front, Direction.NORTH, false);
                    check(box.nearOutside(box.maxX() + 4, box.maxY(), box.maxZ()), "旋转后设备远端四格外沿被遗漏");
                    check(!box.nearOutside(1234, 64, -2222), "控制器位置不是边界外");
                    check(box.maxY() - box.minY() + 1 == size[1], "旋转不应改变设备高度");
                    check(box.maxX() - box.minX() + 1 == size[turn % 2 == 0 ? 0 : 2], "四向变换宽深错误");
                    int localX = size[0] - 1 - controller[0], localZ = size[2] - 1 - controller[2];
                    int rx = switch (turn) { case 1 -> -localZ; case 2 -> -localX; case 3 -> localZ; default -> localX; };
                    int rz = switch (turn) { case 1 -> localX; case 2 -> -localZ; case 3 -> -localX; default -> localZ; };
                    check(!box.nearOutside(1234 + rx, 64 + size[1] - 1 - controller[1], -2222 + rz),
                            "批准布局变换后的边界成员不应触发");
                }
            } catch (Exception failure) { throw new AssertionError("读取正式边界失败：" + layout, failure); }
        }
        int[] size = {3, 5, 7}, controller = {0, 1, 2};
        var origin = new BlockPos(10, 20, 30);
        check(Hk3EggMachineBoundaries.transform(size, controller, origin, Direction.NORTH, Direction.EAST, false)
                .equals(new Box(7, 20, 28, 11, 22, 34)), "GT扩展朝向应绕前轴旋转");
        check(Hk3EggMachineBoundaries.transform(size, controller, origin, Direction.NORTH, Direction.EAST, true)
                .equals(new Box(7, 18, 28, 11, 20, 34)), "GT镜像应沿旋转后的右轴翻转");
        for (var front : List.of(Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST))
            for (var up : List.of(Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST))
                for (boolean flipped : List.of(false, true)) {
                    var box = Hk3EggMachineBoundaries.transform(size, controller, origin, front, up, flipped);
                    check((box.maxX() - box.minX() + 1) * (box.maxY() - box.minY() + 1) * (box.maxZ() - box.minZ() + 1) == 105,
                            "扩展朝向或镜像不得损失成型包络体积");
                    check(!box.nearOutside(10, 20, 30), "任意合法朝向的主控仍在成型包络内部");
                }
    }

    private static void verifyAttributionAndLocality() {
        var callback = method("com/sirin/hk3gtl/common/easter/Hk3EggVanilla", "placed");
        var boundary = method("com/sirin/hk3gtl/common/easter/Hk3EggMachineBoundaries", "placed");
        boolean hooked = false, attributed = false, loadedOnly = false, rechecked = false;
        for (var instruction : callback.instructions) {
            if (instruction instanceof MethodInsnNode call && call.owner.endsWith("/Hk3EggMachineBoundaries") && call.name.equals("placed")) {
                var state = previous(call);
                var pos = previous(state);
                var actor = previous(pos);
                hooked = load(state, 3) && load(pos, 1) && load(actor, 0);
            }
        }
        for (var instruction : boundary.instructions) {
            if (!(instruction instanceof MethodInsnNode call)) continue;
            check(!call.name.equals("getOwnerUUID") && !call.name.equals("getPlayerList"), "旁注不得改投机器所有者或其他玩家");
            check(!List.of("getChunk", "getChunkAt", "getChunkNow", "getAllLoadedChunks").contains(call.name),
                    "边界观察不得强载或遍历整片世界");
            if (call.name.equals("hasChunk")) loadedOnly = true;
            if (call.name.equals("getBlockState")) rechecked = true;
            if (call.owner.endsWith("/Hk3EggVanilla") && call.name.equals("caseEvent")) attributed = load(previous(previous(call)), 0);
        }
        check(hooked, "成功放置回调必须传入原放置者、位置和确认后的方块状态");
        check(attributed, "收藏必须归原放置者");
        check(loadedOnly && rechecked, "设备观察前必须保留区块及当前方块复核");
    }

    private static MethodNode method(String owner, String name) {
        try (var input = MachineBoundaryPlacementTest.class.getClassLoader().getResourceAsStream(owner + ".class")) {
            if (input == null) throw new AssertionError("缺少编译类：" + owner);
            var node = new ClassNode();
            new ClassReader(input).accept(node, 0);
            return node.methods.stream().filter(method -> method.name.equals(name)).findFirst().orElseThrow();
        } catch (Exception failure) { throw new AssertionError("读取放置链字节码失败", failure); }
    }

    private static AbstractInsnNode previous(AbstractInsnNode instruction) {
        do { instruction = instruction.getPrevious(); } while (instruction != null && instruction.getOpcode() < 0);
        return instruction;
    }

    private static boolean load(AbstractInsnNode instruction, int slot) {
        return instruction instanceof VarInsnNode variable && variable.getOpcode() == Opcodes.ALOAD && variable.var == slot;
    }

    private static void check(boolean value, String message) {
        checks++;
        if (!value) throw new AssertionError(message);
    }
}
