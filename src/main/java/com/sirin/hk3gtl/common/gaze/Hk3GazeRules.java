package com.sirin.hk3gtl.common.gaze;

/**
 * 【文件职责】注视值边界与稳定锚覆盖的纯逻辑，供运行时及回归测试共用。
 * 【变更记录 #1】2026-09-30 15:50:54（内测5修订109）
 * 删除：无。新增：安全加减、64/128格球形覆盖与0.50/0.75抑制。
 * 修改：拒绝未运行、异队或超距来源；用途：按已批准R03参数计算有效抑制，不创建机器。
 */
public final class Hk3GazeRules {
    private Hk3GazeRules() {}
    /** 缓冲以主世界刻计时，到期刻立即失效；减免不修改个人原值。 */
    public static boolean bufferActive(long until, long now) { return until > now; }
    public static int effective(int raw, boolean buffer) { return Math.max(0, raw - (buffer ? 50 : 0)); }
    public static int growth(int amount, boolean buffer) {
        return amount <= 0 ? amount : Math.max(1, (int) Math.round(amount * (buffer ? .5 : 1)));
    }
    public static int add(int current, int delta, int maximum) {
        return (int) Math.max(0L, Math.min((long) maximum, (long) current + delta));
    }
    public static double suppression(boolean sameTeam, boolean working, boolean enhanced, double distanceSquared) {
        int radius = enhanced ? 128 : 64;
        return sameTeam && working && Double.isFinite(distanceSquared) && distanceSquared >= 0
                && distanceSquared <= (double) radius * radius ? (enhanced ? .75 : .5) : 0;
    }
}
