package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import java.io.*;
import java.util.zip.GZIPOutputStream;

/** 全实体资源计数与损坏数据拒绝；不把纯数据测试冒充游戏内成型。 */
// 变更记录#1：2026-10-30 00:09:26，修订183：核对清理后的整份资源、叶块保留和新旧主控，不修改世界。
public final class W01HallLayoutTest {
    public static void main(String[] args) throws Exception {
        var data = Hk3W01HallLayout.load();
        check(data.cells().length == 1932713 && data.palette().size() == 276, "实体或状态总数改变");
        check(data.width() == 680 && data.height() == 383 && data.depth() == 767, "尺寸改变");
        check(data.controllerX() == 231 && data.controllerY() == 29 && data.controllerZ() == 383, "主控未移至西入口");
        check(stateAt(data, 231, 29, 383).equals("minecraft:chiseled_quartz_block"), "主控底材错误");
        check(stateAt(data, 293, 47, 359).equals("minecraft:smooth_quartz"), "旧主控未恢复石英");
        int leaves = 0;
        for (long cell : data.cells()) {
            String state = data.palette().get(Hk3W01HallLayout.state(cell));
            check(!state.contains("waterlogged=true") && !state.contains("white_concrete_powder")
                    && !state.contains("coral") && !state.contains("warped_roots") && !state.contains("nether_sprouts")
                    && !state.contains("rose_bush") && !state.contains("lilac") && !state.contains("pink_petals")
                    && !state.startsWith("minecraft:water[") && !state.equals("minecraft:water"), "禁用方块或含水状态残留：" + state);
            if (state.contains("_leaves[")) leaves++;
            int x = Hk3W01HallLayout.x(cell) - 286, y = Hk3W01HallLayout.y(cell) - 63,
                    z = Hk3W01HallLayout.z(cell) - 376;
            check(!(x >= -269 && x <= -267 && y >= 0 && y <= 1 && z >= 5 && z <= 8), "黄圈样件残留");
        }
        check(leaves == 1995, "叶块被误删");
        reject(new long[]{0, 0}, "重复坐标");
        reject(new long[]{1}, "状态越界");
        reject(new long[]{1L << 16}, "控制器缺格");
        System.out.println("W01HallLayoutTest PASS: 1,932,713格/276状态，主控[231,29,383]；无粉末/含水/指定植物/黄圈样件，1995格叶块保留。");
    }
    private static String stateAt(Hk3W01HallLayout data, int x, int y, int z) {
        long found = java.util.Arrays.stream(data.cells()).filter(c -> Hk3W01HallLayout.x(c) == x
                && Hk3W01HallLayout.y(c) == y && Hk3W01HallLayout.z(c) == z).findFirst().orElseThrow();
        return data.palette().get(Hk3W01HallLayout.state(found));
    }
    private static void reject(long[] cells, String kind) throws Exception {
        var bytes = new ByteArrayOutputStream();
        try (var out = new DataOutputStream(new GZIPOutputStream(bytes))) {
            out.writeInt(0x57303141); out.writeInt(1);
            for (int n : new int[]{2, 2, 2, 0, 0, 0, cells.length}) out.writeInt(n);
            out.writeShort(1); out.writeUTF("minecraft:stone");
            for (long cell : cells) out.writeLong(cell);
        }
        try { Hk3W01HallLayout.read(new ByteArrayInputStream(bytes.toByteArray())); throw new AssertionError("未拒绝" + kind); }
        catch (IOException expected) {}
    }
    private static void check(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
}
