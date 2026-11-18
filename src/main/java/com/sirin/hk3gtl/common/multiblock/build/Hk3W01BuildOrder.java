package com.sirin.hk3gtl.common.multiblock.build;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;

/** 对已有实体坐标作按高度稳定排序；每格仅增加一个int索引，不展开空气。 */
 






final class Hk3W01BuildOrder {
    private final long[] cells;
    private final int[] counts;
    private final int[] order;
    private final byte[] phases;
    private final int height;
    private int cursor;
    private boolean filling;

    Hk3W01BuildOrder(long[] cells, int height, byte[] phases) {
        this.cells = cells;
        this.height = height;
        this.phases = phases;
        counts = new int[height * 3];
        order = new int[cells.length];
    }

    boolean step() {
        if (!filling) {
            counts[bucket(cells[cursor++])]++;
            if (cursor == cells.length) {
                int start = 0;
                for (int y = 0; y < counts.length; y++) {
                    int count = counts[y]; counts[y] = start; start += count;
                }
                cursor = 0; filling = true;
            }
            return false;
        }
        order[counts[bucket(cells[cursor])]++] = cursor;
        return ++cursor == cells.length;
    }

    long cell(int index) { return cells[order[index]]; }
    private int bucket(long cell) {
        return phases[Hk3W01HallLayout.state(cell)] * height + Hk3W01HallLayout.y(cell);
    }
}
