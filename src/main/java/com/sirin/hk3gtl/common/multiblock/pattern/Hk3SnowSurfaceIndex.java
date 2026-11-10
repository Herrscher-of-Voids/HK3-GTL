package com.sirin.hk3gtl.common.multiblock.pattern;

import java.util.Arrays;

/** 只定位批准实体正上方的空格，不把建筑内部或包围盒周边列入除雪范围。 */
final class Hk3SnowSurfaceIndex {
    private Hk3SnowSurfaceIndex() {}

    static boolean exposed(long[] cells, int index, int width, int height) {
        int at = (int) (cells[index] >>> 16);
        if (at / width % height == height - 1) return true;
        long above = (long) (at + width) << 16;
        int found = Arrays.binarySearch(cells, above);
        int next = found < 0 ? -found - 1 : found;
        return next == cells.length || (cells[next] >>> 16) != (above >>> 16);
    }
}
