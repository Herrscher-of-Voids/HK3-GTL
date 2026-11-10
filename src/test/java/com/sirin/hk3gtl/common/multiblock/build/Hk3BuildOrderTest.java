package com.sirin.hk3gtl.common.multiblock.build;

/**
 * 【文件职责】直接验证生产排序的阶段优先、负高度、稳定顺序与分步读取上限。
 * 【变更记录 #1】2026-10-30（修订184）：新增顺序与未完成读取保护回归，不启动世界或写存档。
 * 【变更记录 #2】2026-10-30（修订184）：删除Minecraft引导与假蓝图，直接用整数读取器验证同一生产算法。
 */
public final class Hk3BuildOrderTest {
    private Hk3BuildOrderTest() {}

    public static void main(String[] args) {
        int[] heights = {-4, -2, -5, -5, -5, -1, -2, -5};
        int[] phases = {2, 0, 1, 0, 0, 2, 1, 2};
        int[] reads = {0};
        Hk3BuildOrder order = new Hk3BuildOrder(heights.length, 5, -5,
                i -> heights[i], i -> { reads[0]++; return phases[i]; });
        check(reads[0] == 0, "构造排序不得无预算读取全部实体");
        try { order.index(0); throw new AssertionError("准备完成前不得读取索引"); }
        catch (IllegalStateException expected) { }
        int steps = 0;
        boolean done;
        do {
            int before = reads[0];
            done = order.step();
            check(reads[0] - before <= 1, "每步最多读取一个实体阶段");
            check(++steps <= 2 * heights.length + 3 * 5, "排序必须有界完成");
        } while (!done);
        int[] expected = {3, 4, 1, 2, 6, 7, 0, 5};
        for (int i = 0; i < expected.length; i++)
            check(order.index(i) == expected[i], "支撑、重力、附着及同高稳定顺序错误：" + i);
        check(order.step(), "已完成排序可重复确认");
        int[] cy={1,0,0,1,0,0}, cp={0,0,1,0,0,2}, ck={1,1,0,0,0,0};
        Hk3BuildOrder chunked=new Hk3BuildOrder(6,2,0,i->cy[i],i->cp[i],2,i->ck[i]);
        while(!chunked.step()) { }
        int[] chunkExpected={4,3,1,0,2,5};
        for(int i=0;i<chunkExpected.length;i++)check(chunked.index(i)==chunkExpected[i],"区块集中施工必须保留支撑阶段及区块内自底向上");
        int[] nextChunk={2,2,4,4,5,6};
        for(int i=0;i<nextChunk.length;i++)check(chunked.nextChunkIndex(i)==nextChunk[i],"预加载必须跳过本阶段的整段区块");
        try {
            new Hk3BuildOrder(1, 1, 0, i -> 0, i -> 3).step();
            throw new AssertionError("非法阶段必须拒绝");
        } catch (IllegalStateException expectedFailure) { }
        try {
            new Hk3BuildOrder(1, 1, -5, i -> -4, i -> 0).step();
            throw new AssertionError("越界高度必须拒绝");
        } catch (IllegalStateException expectedFailure) { }
        System.out.println("统一建造排序检查通过；未执行游戏搭建或成型验收。");
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

}
