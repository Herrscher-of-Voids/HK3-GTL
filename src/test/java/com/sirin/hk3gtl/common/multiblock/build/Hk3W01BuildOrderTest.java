package com.sirin.hk3gtl.common.multiblock.build;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;

/**
 * 【文件职责】直接检查生产阶段排序、全部实体单次覆盖及忙闲预算，不启动游戏。
 * 【变更记录 #1】2026-10-30 00:26:34（第1次备注 · 内测5修订183）
 * - 删除：无；新增：十万格稳定顺序、单格边界和真实W01全量资源覆盖断言。
 * - 修改：无运行时逻辑；直接调用生产索引与预算函数，检查阶段优先和异常耗时回退。
 * - 用途：防止加速遗漏、重复实体或打乱支撑先后；不把纯逻辑测试当作游戏提速验收。
 */
public final class Hk3W01BuildOrderTest {
    private Hk3W01BuildOrderTest() {}

    public static void main(String[] args) {
        byte[] phases = {2, 0, 1};
        long[] cells = new long[100_000];
        for (int i = 0; i < cells.length; i++)
            cells[i] = Hk3W01HallLayout.pack(i / 1024, i % 7, i % 1024, i % 3);
        verify(cells, 7, phases);
        verify(new long[]{Hk3W01HallLayout.pack(4095, 0, 4095, 0)}, 1, new byte[]{0});
        var layout = Hk3W01HallLayout.load();
        require(layout.cells().length == 1_932_713 && layout.palette().size() == 276, "本轮资源数量或状态变化");
        byte[] materialPhases = new byte[layout.palette().size()];
        for (int i = 0; i < materialPhases.length; i++) materialPhases[i] = (byte) (i % 3);
        verify(layout.cells(), layout.height(), materialPhases);
        require(Hk3W01BuildBudget.nanos(0) == 12_000_000L, "空闲预算上限不符");
        require(Hk3W01BuildBudget.nanos(30) == 10_000_000L, "未扣除当前平均tick耗时");
        require(Hk3W01BuildBudget.nanos(38) == 2_000_000L
                && Hk3W01BuildBudget.nanos(80) == 2_000_000L, "繁忙服务器未收缩预算");
        require(Hk3W01BuildBudget.nanos(Float.NaN) == 4_000_000L
                && Hk3W01BuildBudget.nanos(Float.POSITIVE_INFINITY) == 4_000_000L
                && Hk3W01BuildBudget.nanos(-1) == 4_000_000L, "非法耗时未回退");
        System.out.println("W01阶段/高度稳定排序、1932713格单次覆盖及2–12毫秒预算回归通过；未执行实机性能验收。");
    }

    private static void verify(long[] cells, int height, byte[] phases) {
        var order = new Hk3W01BuildOrder(cells, height, phases);
        int steps = 1;
        while (!order.step()) { require(++steps <= cells.length * 2, "索引准备未有界结束"); }
        require(steps == cells.length * 2, "索引准备必须是两遍实体");
        int[] expectedNext = new int[height * 3];
        for (long cell : cells) expectedNext[bucket(cell, height, phases)]++;
        int start = 0;
        for (int i = 0; i < expectedNext.length; i++) {
            int count = expectedNext[i]; expectedNext[i] = start; start += count;
        }
        // 按原输入顺序逐一取其目标桶槽位，直接证明无遗漏、无重复和同桶保序。
        for (long original : cells) {
            int at = expectedNext[bucket(original, height, phases)]++;
            require(order.cell(at) == original, "阶段/高度顺序或方块状态不符");
        }
    }

    private static int bucket(long cell, int height, byte[] phases) {
        return phases[Hk3W01HallLayout.state(cell)] * height + Hk3W01HallLayout.y(cell);
    }
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
