package com.sirin.hk3gtl.test.api;

import com.sirin.hk3gtl.api.stage.Hk3StageApi;

import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 【文件职责】核验公开查询签名及真实阶段返回值；研究和事件的玩家状态另由服务端夹具验收。
 * 【变更记录 #1】2026-10-31 17:44:19（第1次备注 · 内测5修订189）
 * - 删除：无。新增：三类只读查询签名、16档正式电压键、四阶段及数值越界回归。
 * - 修改：无生产行为变更；用途：防止旧电压键、长整型截断或额外写入入口混入兼容查询。
 */
public final class PublicApiContractTest {
    private static int checks;

    public static void main(String[] args) throws Exception {
        querySurface("research.Hk3ResearchApi", Set.of(
                "isResearchCompleted(net.minecraft.server.level.ServerPlayer,java.lang.String):boolean"));
        querySurface("event.Hk3EventApi", Set.of(
                "hasTriggered(net.minecraft.server.level.ServerPlayer,java.lang.String):boolean"));
        querySurface("stage.Hk3StageApi", Set.of("isExtendedTier(int):boolean", "getVoltageKey(int):java.lang.String",
                "getPhaseNameCn(int):java.lang.String", "getRecipeVoltage(int):long"));

        String[] keys = {"hbv", "hcv", "hrv", "hdv", "qsv", "qcv", "qev", "qav",
                "imv", "icv", "irv", "iwv", "wfv", "wsv", "civ", "cev"};
        String[] phases = {"海渊", "虚数", "量子", "终焉"};
        for (int tier = 15; tier <= 30; tier++) {
            check(Hk3StageApi.isExtendedTier(tier), "扩展档位：" + tier);
            check(Hk3StageApi.getVoltageKey(tier).equals(keys[tier - 15]), "正式电压键：" + tier);
            check(Hk3StageApi.getPhaseNameCn(tier).equals(phases[(tier - 15) / 4]), "阶段分界：" + tier);
            long voltage = tier == 30 ? Long.MAX_VALUE : 8_053_063_680L << (2 * (tier - 15));
            check(Hk3StageApi.getRecipeVoltage(tier) == voltage, "长整型电压：" + tier);
        }
        check(Hk3StageApi.getRecipeVoltage(0) == 7L, "保留原版低档配方电压");
        check(Hk3StageApi.getRecipeVoltage(14) == 2_013_265_920L, "原版最高档配方电压");
        check(Hk3StageApi.getPhaseNameCn(14).equals("原版"), "原版阶段名");
        check(Hk3StageApi.getPhaseNameCn(31).equals("未知"), "超出阶段上界");
        for (int tier : new int[]{Integer.MIN_VALUE, -1, 14, 31, Integer.MAX_VALUE}) {
            check(!Hk3StageApi.isExtendedTier(tier), "拒绝非扩展档位：" + tier);
            boolean rejected = false;
            try {
                Hk3StageApi.getVoltageKey(tier);
            } catch (IllegalArgumentException expected) {
                rejected = true;
            }
            check(rejected, "越界电压键必须报错：" + tier);
            if (tier < 0 || tier > 30) {
                check(Hk3StageApi.getRecipeVoltage(tier) == 0L, "越界配方电压返回零：" + tier);
            }
        }
        System.out.println("PublicApiContractTest：" + checks + "项通过；玩家状态与权限以服务端夹具验收为准。");
    }

    private static void querySurface(String name, Set<String> expected) throws Exception {
        Class<?> type = Class.forName("com.sirin.hk3gtl.api." + name, false,
                PublicApiContractTest.class.getClassLoader());
        Set<String> actual = Arrays.stream(type.getDeclaredMethods())
                .filter(method -> Modifier.isPublic(method.getModifiers()))
                .peek(method -> check(Modifier.isStatic(method.getModifiers()), "公开查询为静态方法"))
                .map(method -> method.getName() + "(" + Arrays.stream(method.getParameterTypes())
                        .map(Class::getName).collect(Collectors.joining(",")) + "):" + method.getReturnType().getName())
                .collect(Collectors.toSet());
        check(actual.equals(expected), "公开查询契约：" + name);
        check(Arrays.stream(type.getDeclaredConstructors()).allMatch(constructor ->
                Modifier.isPrivate(constructor.getModifiers())), "查询门面禁止实例化：" + name);
        check(Arrays.stream(type.getDeclaredFields()).noneMatch(field -> Modifier.isPublic(field.getModifiers())),
                "查询门面不暴露可写字段：" + name);
    }

    private static void check(boolean ok, String message) {
        checks++;
        if (!ok) throw new AssertionError(message);
    }
}
