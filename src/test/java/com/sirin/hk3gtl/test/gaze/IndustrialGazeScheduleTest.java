package com.sirin.hk3gtl.test.gaze;

import com.sirin.hk3gtl.common.research.Hk3IndustrialGazeSchedule;
import java.math.BigInteger;

/**
 * 【变更记录 #1】2026-11-04 21:00:03（第1次备注 · 内测5修订200）
 * 删除：无。新增：真实工业调度函数边界、周期比例、重复入口及有符号溢出测试。
 * 修改：无。用途：防止工业分段误套研究公式；此测试不代表机器IO或游戏验收。
 */
public final class IndustrialGazeScheduleTest {
    public static void main(String[] args) {
        int[] gaze = {0, 199, 200, 499, 500, 799, 800, 999, 1000};
        int[] expected = {100, 100, 95, 95, 75, 75, 60, 60, 50};
        long[] offsets = {0, -1, 63, Long.MIN_VALUE, Long.MAX_VALUE};
        int checks = 0;
        for (int g = 0; g < gaze.length; g++) {
            for (long offset : offsets) {
                int allowed = 0;
                for (long time = -100; time < 0; time++) {
                    boolean first = Hk3IndustrialGazeSchedule.throttles(gaze[g], time, offset);
                    if (!first) allowed++;
                    if (first != Hk3IndustrialGazeSchedule.throttles(gaze[g], time, offset))
                        throw new AssertionError("同刻多入口不能重复减速");
                }
                if (allowed != expected[g]) throw new AssertionError("工业周期比例错误：" + gaze[g]);
                checks++;
            }
        }
        for (long time : new long[]{Long.MIN_VALUE, -1, 0, Long.MAX_VALUE}) {
            for (long position : offsets) {
                int phase = BigInteger.valueOf(time).add(BigInteger.valueOf(position))
                        .mod(BigInteger.valueOf(100)).intValue();
                if (Hk3IndustrialGazeSchedule.throttles(1000, time, position) != (phase >= 50))
                    throw new AssertionError("时间与位置相加溢出改变相位");
                checks++;
            }
        }
        System.out.println("工业注视调度通过：" + checks + "组；不代表机器执行验收");
    }
}
