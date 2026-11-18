package com.sirin.hk3gtl.common.multiblock.pattern;

import java.util.Arrays;

public final class Hk3SnowClearanceTest {
    public static void main(String[] args) {
        // 两列及另一Z切片相邻，材料编号不同；不能把下一层切片误当作头顶支撑。
        long[] cells={cell(0,0,0,5),cell(0,1,0,9),cell(0,2,0,7),cell(1,0,0,2),cell(1,2,0,3),cell(0,0,1,8)};
        Arrays.sort(cells);
        for (int i=0;i<cells.length;i++) {
            int at=(int)(cells[i]>>>16),x=at%2,y=at/2%3,z=at/6;
            boolean expected=y==2 || Arrays.stream(cells).noneMatch(c->(c>>>16)==((z*3+y+1)*2+x));
            check(Hk3SnowSurfaceIndex.exposed(cells,i,2,3)==expected,"除雪表面与逐格独立判断不同");
        }
        System.out.println("稀疏除雪表面边界通过。");
    }
    private static long cell(int x,int y,int z,int state) { return (long)((z*3+y)*2+x)<<16|state; }
    private static void check(boolean ok,String message) { if(!ok)throw new AssertionError(message); }
}
