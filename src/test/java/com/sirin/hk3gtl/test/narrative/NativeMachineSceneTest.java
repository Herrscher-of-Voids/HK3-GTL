package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.easter.Hk3EggNativeMachineFacts;
import com.sirin.hk3gtl.common.easter.Hk3EggNativeMachineFacts.Box;
import com.sirin.hk3gtl.common.easter.Hk3EggRules;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.*;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

public final class NativeMachineSceneTest {
    private static int checks;

    public static void main(String[] args) {
        var box = new Box(-120, 20, -160, 120, 180, 160);
        for (int radius : new int[]{4, 8}) {
            for (int[] point : List.of(new int[]{120 + radius, 20, 0}, new int[]{-120 - radius, 80, 160},
                    new int[]{0, 180 + radius, 0}, new int[]{0, 20 - radius, 0}, new int[]{0, 80, 160 + radius},
                    new int[]{0, 80, -160 - radius}))
                check(box.nearOutside(point[0], point[1], point[2], radius), "六向批准外边界包含阈值");
            for (int[] point : List.of(new int[]{121 + radius, 20, 0}, new int[]{0, 181 + radius, 0},
                    new int[]{120 + radius, 20, 161}, new int[]{120, 180, 160}, new int[]{0, 100, 0},
                    new int[]{Integer.MAX_VALUE, Integer.MIN_VALUE, 0}))
                check(!box.nearOutside(point[0], point[1], point[2], radius), "超距、斜角、内部、成员及整数溢出反例");
        }
        check(!box.nearOutside(121, 80, 0, 1), "不引入未批准半径");
        check(box.nearOutside(122, 183, 160, 4), "球形距离内斜角可达");
        check(!box.nearOutside(123, 183, 160, 4), "立方范围不能代替球形距离");
        var extreme = new Box(Integer.MIN_VALUE, 0, 0, Integer.MIN_VALUE, 0, 0);
        check(!extreme.nearOutside(Integer.MAX_VALUE, 0, 0, 8), "两端整数差不得溢出");
        for (boolean spawned : new boolean[]{false, true})
            for (boolean boat : new boolean[]{false, true})
                for (boolean water : new boolean[]{false, true})
                    for (boolean formed : new boolean[]{false, true})
                        for (boolean error : new boolean[]{false, true}) {
                            check(Hk3EggNativeMachineFacts.boat(spawned, boat, water,
                                            Hk3EggNativeMachineFacts.QUANTUM_MACHINE, formed, error, box, 128, 80, 0)
                                            == (spawned && boat && water && formed && !error),
                                    "091只接受真实船、水面及当前有效成型设备");
                        }
        for (String id : List.of("hk3gtl:quantum_observer", "gtceu:quantum_chest", Hk3EggNativeMachineFacts.FLAGSHIP_MACHINE))
            check(!Hk3EggNativeMachineFacts.boat(true, true, true, id, true, false, box, 128, 80, 0),
                    "旧名或其他量子设备不能冒充I24");
        check(!Hk3EggNativeMachineFacts.boat(true, true, true, Hk3EggNativeMachineFacts.QUANTUM_MACHINE,
                true, false, null, 128, 80, 0), "I24无真实包络保持休眠");
        check(!Hk3EggNativeMachineFacts.boat(true, true, true, Hk3EggNativeMachineFacts.QUANTUM_MACHINE,
                true, false, box, 129, 80, 0), "放船九格不能冒充八格");
        for (boolean ice : new boolean[]{false, true})
            for (boolean fusion : new boolean[]{false, true})
                for (boolean formed : new boolean[]{false, true})
                    for (boolean error : new boolean[]{false, true})
                        check(Hk3EggNativeMachineFacts.ice(ice, fusion, formed, error, box, 124, 80, 0)
                                        == (ice && fusion && formed && !error), "095不接受其他方块或其他高温机器");
        check(!Hk3EggNativeMachineFacts.ice(true, true, true, false, null, 124, 80, 0), "聚变缺边界不猜测");
        check(!Hk3EggNativeMachineFacts.ice(true, true, true, false, box, 125, 80, 0), "聚变外五格拒绝");
        for (boolean success : new boolean[]{false, true})
            for (boolean flagship : new boolean[]{false, true})
                for (boolean soulium : new boolean[]{false, true})
                    for (int count : new int[]{-1, 0, 1, 64})
                        check(Hk3EggNativeMachineFacts.flagship(success, flagship, Hk3EggNativeMachineFacts.FLAGSHIP_MACHINE,
                                        soulium, count) == (success && flagship && soulium && count > 0),
                                "096成功、实名旗舰、魂钢与正数量缺一不可");
        check(!Hk3EggNativeMachineFacts.flagship(true, true, "hk3gtl:hyperion", true, 1), "旧旗舰ID不能代替当前注册身份");
        check(!Hk3EggNativeMachineFacts.flagship(true, true, null, true, 1), "缺设备身份拒绝");
        for (float height : new float[]{0.125f, 0.5f, 8f / 9f, 1f}) {
            check(Hk3EggNativeMachineFacts.waterSurface(true, 64d + height, 64, height), "流动水与静水真实表面");
            check(!Hk3EggNativeMachineFacts.waterSurface(false, 64d + height, 64, height), "岩浆或旱地不计水面");
            check(!Hk3EggNativeMachineFacts.waterSurface(true, 64d + height - 0.1, 64, height), "水下不是水面放船");
            check(!Hk3EggNativeMachineFacts.waterSurface(true, 64d + height + 0.1, 64, height), "水上实体或垫块不计水面");
        }
        for (double y : new double[]{Double.NaN, Double.NEGATIVE_INFINITY, Double.POSITIVE_INFINITY})
            check(!Hk3EggNativeMachineFacts.waterSurface(true, y, 64, 1), "非法实体高度拒绝");
        for (float height : new float[]{Float.NaN, Float.POSITIVE_INFINITY, -1, 0, 1.1f})
            check(!Hk3EggNativeMachineFacts.waterSurface(true, 65, 64, height), "非法液体高度拒绝");
        try (var input = NativeMachineSceneTest.class.getResourceAsStream("/data/hk3gtl/structures/approved/i24.json")) {
            check(input != null, "量子设备必须已有正式批准资源");
            var metadata = com.google.gson.JsonParser.parseReader(new InputStreamReader(input, StandardCharsets.UTF_8)).getAsJsonObject();
            check(metadata.get("machine").getAsString().equals(Hk3EggNativeMachineFacts.QUANTUM_MACHINE),
                    "I24真实批准元数据身份与规则一致");
        } catch (Exception failure) { throw new AssertionError("读取I24批准资源失败", failure); }
        verifyProductionWiring();
        for (int id : new int[]{91, 95, 96}) {
            var rule = Hk3EggRules.all().stream().filter(r -> r.id().equals("E-EG-0" + id)).findFirst().orElseThrow();
            check(rule.matches("vanilla_case", Map.of("case", Integer.toString(id))), "成功事实连接原批准条目");
            check(!rule.matches("vanilla_case", Map.of("case", "0")), "其他操作不得借用条目");
            check(!rule.matches("vanilla_case", Map.of()), "缺成功事实拒绝");
            check(!rule.matches("machine_nearby", Map.of("case", Integer.toString(id))), "附近或持有不能替代真实成功事件");
        }
        System.out.println("设备原生场景：" + checks + "项检查通过；未做游戏放船、放冰与旗舰交互验收。");
    }

    private static void verifyProductionWiring() {
        var boatMixin = node("com/sirin/hk3gtl/mixin/Hk3EggBoatMixin");
        var spawn = method(boatMixin, "hk3gtl$spawn");
        check(calls(spawn, "addFreshEntity") == 1 && calls(spawn, "boatSpawned") == 1,
                "原生成调用恰好执行一次并传递真实结果");
        check(type(spawn, "net/minecraft/server/level/ServerPlayer"), "放船归属保留原服务端操作者");
        check(calls(spawn, "setReturnValue") == 0, "旁注不能改写原版交互返回值");
        var last = previous(spawn.instructions.getLast());
        check(last.getOpcode() == Opcodes.IRETURN && previous(last.getPrevious()) instanceof VarInsnNode result
                && result.getOpcode() == Opcodes.ILOAD, "原生成布尔结果原样返回");
        var controllerMixin = node("com/sirin/hk3gtl/mixin/gtceu/Hk3EggControllerUseMixin");
        var use = method(controllerMixin, "hk3gtl$used");
        check(calls(use, "consumesAction") == 1 && calls(use, "controllerUsed") == 1, "控制器只连接真实交互成功回执");
        check(calls(use, "setReturnValue") == 0 && calls(use, "cancel") == 0, "控制器旁注不改变交互");
        var injection = use.visibleAnnotations.stream().filter(a -> a.desc.endsWith("/Inject;")).findFirst().orElseThrow();
        check(annotationValue(injection, "remap").equals(Boolean.TRUE), "GT覆盖的原版use方法仍需生产映射");
        var scenes = node("com/sirin/hk3gtl/common/easter/Hk3EggNativeMachineScenes");
        var boat = method(scenes, "boatSpawned");
        check(type(boat, "net/minecraft/world/entity/vehicle/Boat") && calls(boat, "isSameThread") > 0,
                "实际入口校验船实体与服务端线程");
        var boatBody = body(scenes, "boatSpawned", "getEntity");
        check(calls(boatBody, "getEntity") > 0 && calls(boatBody, "isRemoved") > 0, "生成成功仍复核实体留在当前世界");
        check(calls(boatBody, "getFluidState") > 0 && calls(boatBody, "waterSurface") > 0, "水面判定接在真实实体与液体上");
        var controllerBody = body(scenes, "controllerUsed", "getItemInHand");
        check(type(controllerBody, "com/sirin/hk3gtl/common/machine/hyperion/Hk3HyperionMachine"), "必须是实际旗舰类");
        check(calls(controllerBody, "getItemInHand") == 1 && calls(controllerBody, "get") > 0,
                "按实际传入手取得正式材料注册魂钢");
        check(field(controllerBody, "com/gregtechceu/gtceu/api/data/tag/TagPrefix", "ingot")
                && field(controllerBody, "com/sirin/hk3gtl/common/material/SouliumMaterial", "SOULIUM"), "不得猜魂钢物品ID");
        check(!field(controllerBody, "net/minecraft/world/InteractionHand", "MAIN_HAND")
                && !field(controllerBody, "net/minecraft/world/InteractionHand", "OFF_HAND"), "不硬编码主副手");
        var near = method(scenes, "near");
        check(calls(near, "hasChunk") > 0 && calls(near, "hasChunkAt") > 0
                && calls(near, "getControllerInChunk") > 0, "只查已加载局部成型索引");
        check(calls(near, "isFormed") > 0 && calls(near, "hasError") > 0
                && calls(near, "getMultiblockState") > 0, "失效或换代成型缓存拒绝");
        check(type(near, "com/gregtechceu/gtceu/common/machine/multiblock/electric/FusionReactorMachine"), "聚变设备按依赖真实类型识别");
        var bounds = method(scenes, "bounds");
        check(field(bounds, "com/gregtechceu/gtceu/api/pattern/MultiblockState", "cache") && calls(bounds, "of") > 0,
                "原生聚变使用实际成型位置缓存求边界");
        var placed = method(node("com/sirin/hk3gtl/common/easter/Hk3EggVanilla"), "placed");
        check(calls(placed, "icePlaced") == 1, "冰放置接既有回滚后确认链");
        for (var method : scenes.methods) for (var instruction : method.instructions)
            if (instruction instanceof MethodInsnNode call) {
                check(!List.of("getChunk", "getChunkAt", "getAllLoadedChunks", "getPlayerList", "getOwnerUUID")
                                .contains(call.name), "不强载、不全服扫描、不转投其他玩家");
                check(!List.of("shrink", "setCount", "setItem", "setBlock", "setBlockAndUpdate", "hurtAndBreak", "onStructureFormed")
                                .contains(call.name), "旁注不消耗、不改世界或成型");
            }
    }

    private static ClassNode node(String owner) {
        try (var input = NativeMachineSceneTest.class.getClassLoader().getResourceAsStream(owner + ".class")) {
            if (input == null) throw new AssertionError("缺编译入口：" + owner);
            var node = new ClassNode();
            new ClassReader(input).accept(node, ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
            return node;
        } catch (Exception failure) { throw new AssertionError("真实入口读取失败", failure); }
    }

    private static MethodNode method(ClassNode node, String name) {
        return node.methods.stream().filter(m -> m.name.equals(name)).findFirst().orElseThrow(() -> new AssertionError("缺生产方法：" + name));
    }

    private static MethodNode body(ClassNode node, String operation, String call) {
        return node.methods.stream().filter(m -> m.name.startsWith("lambda$" + operation + "$") && calls(m, call) > 0)
                .findFirst().orElseThrow(() -> new AssertionError("缺生产观察体：" + operation));
    }

    private static int calls(MethodNode method, String name) {
        int count = 0;
        for (var instruction : method.instructions) if (instruction instanceof MethodInsnNode call && call.name.equals(name)) count++;
        return count;
    }

    private static Object annotationValue(AnnotationNode annotation, String key) {
        if (annotation.values != null) for (int i = 0; i < annotation.values.size(); i += 2)
            if (annotation.values.get(i).equals(key)) return annotation.values.get(i + 1);
        return null;
    }

    private static boolean type(MethodNode method, String name) {
        for (var instruction : method.instructions) if (instruction instanceof TypeInsnNode type && type.desc.equals(name)) return true;
        return false;
    }

    private static boolean field(MethodNode method, String owner, String name) {
        for (var instruction : method.instructions)
            if (instruction instanceof FieldInsnNode field && field.owner.equals(owner) && field.name.equals(name)) return true;
        return false;
    }

    private static AbstractInsnNode previous(AbstractInsnNode node) {
        if (node != null && node.getOpcode() >= 0) return node;
        do { node = node.getPrevious(); } while (node != null && node.getOpcode() < 0);
        return node;
    }

    private static void check(boolean value, String reason) {
        checks++;
        if (!value) throw new AssertionError(reason);
    }
}
