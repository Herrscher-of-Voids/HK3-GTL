package com.sirin.hk3gtl.test.overview;

import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewAdapter;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData.State;
import net.minecraft.network.chat.Component;

/**
 * 【文件职责】验证总览等待原因的保守分类，防止空闲、输出阻塞或字面伪装被误报为缺电。
 * 【变更记录 #1】2026-10-19 02:09:59（第1次备注 · 修订171）
 * 删除：无。新增：GT能力键、嵌套原因、未知等待及开关优先级回归。
 * 修改：无；不构造机器、世界或玩家；用途为分类语义证据，不代表Mixin或领地权限已实机验收。
 */
public final class MachineOverviewAdapterTest {
    private static int checks;
    public static void main(String[] args) {
        expect(false, true, true, input("eu"), State.STOPPED, "工作开关关闭优先");
        expect(true, true, true, input("eu"), State.RUNNING, "真实运行优先");
        expect(true, false, false, null, State.UNKNOWN, "空闲不能推断缺料");
        expect(true, false, true, null, State.UNKNOWN, "等待不能推断缺电");
        expect(true, false, true, input("eu"), State.NEED_ENERGY, "GT输入电能不足");
        expect(true, false, true, input("item"), State.NEED_INPUT, "GT物品不足");
        expect(true, false, true, input("fluid"), State.NEED_INPUT, "GT流体不足");
        expect(true, false, true, input("cwu"), State.UNKNOWN, "算力不足不冒充缺电或物料");
        expect(true, false, true, Component.translatable("gtceu.recipe_logic.insufficient_fuel"), State.NEED_INPUT, "GT燃料不足");
        expect(true, false, true, Component.translatable("gtceu.recipe_logic.insufficient_out")
                .append(Component.translatable("recipe.capability.eu.name")), State.UNKNOWN, "能源输出阻塞不冒充缺电");
        expect(true, false, true, Component.literal("gtceu.recipe_logic.insufficient_in recipe.capability.eu.name"),
                State.UNKNOWN, "字面文字不能伪装能力键");
        expect(true, false, true, Component.translatable("addon.reason", input("eu")), State.NEED_ENERGY, "嵌套组件可读取GT真实原因");
        expect(true, false, true, Component.translatable("addon.reason", "gtceu.recipe_logic.insufficient_in", "recipe.capability.eu.name"),
                State.UNKNOWN, "字符串参数不当作能力键");
        Component large = Component.literal("未知");
        for (int i = 0; i < 1000; i++) large.getSiblings().add(Component.translatable("addon.reason." + i));
        large.getSiblings().add(input("eu"));
        expect(true, false, true, large, State.UNKNOWN, "超预算组件不无限遍历或猜测");
        System.out.println("MachineOverviewAdapterTest：" + checks + "项通过");
    }
    private static Component input(String capability) {
        return Component.translatable("gtceu.recipe_logic.insufficient_in").append(": ")
                .append(Component.translatable("recipe.capability." + capability + ".name"));
    }
    private static void expect(boolean enabled, boolean working, boolean waiting, Component reason, State state, String description) {
        if (Hk3MachineOverviewAdapter.recipeStatus(enabled, working, waiting, reason).state() != state)
            throw new AssertionError(description);
        checks++;
    }
}
