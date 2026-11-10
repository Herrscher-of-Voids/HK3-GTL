package com.sirin.hk3gtl.common.research;

/**
 * 【文件职责】工业执行刻的只读分段调度；不使用研究公式，不改变配方与资源。
 * 【变更记录 #1】2026-11-04 21:00:03（第1次备注 · 内测5修订200）
 * 删除：无。新增：既有工业100刻窗口的纯函数，供真实守卫与定向测试共用。
 * 修改：将原1、0.95、0.75、0.60、0.50倍率等价表示为100、95、75、60、50个允许刻。
 * 用途：验证分段边界、位置相位及重复守卫幂等；分开取模避免时间与位置相加溢出。
 */
public final class Hk3IndustrialGazeSchedule {
    private Hk3IndustrialGazeSchedule() {}

    public static boolean throttles(double gaze, long gameTime, long position) {
        int allowed = gaze < 200 ? 100 : gaze < 500 ? 95 : gaze < 800 ? 75 : gaze < 1000 ? 60 : 50;
        return (Math.floorMod(gameTime, 100L) + Math.floorMod(position, 100L)) % 100L >= allowed;
    }
}
