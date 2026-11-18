package com.sirin.hk3gtl.common.gaze;







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
