package com.sirin.hk3gtl.common.multiblock.build;

/**
 * 【文件职责】依据服务器最近平均tick耗时计算本次W01搭建主线程限额，不改TPS或方块行为。
 * 【变更记录 #1】2026-10-29 23:48:50（第1次备注 · 内测5修订183）
 * - 删除：无；新增：2至12毫秒自适应限额及非有限平均值的4毫秒回退。
 * - 修改：从40毫秒预算扣除当前平均耗时，繁忙时缩小、空闲时扩大；50毫秒目标仍留余量。
 * - 用途：避免始终4毫秒的人为限速；单次Minecraft/Forge调用不可抢占，不能保证每tick绝不超额。
 */
final class Hk3W01BuildBudget {
    static final int BUILD_STEPS = 32768;
    static final int PREPARATION_STEPS = 65536;
    private Hk3W01BuildBudget() {}

    static long nanos(float averageTickMillis) {
        if (!Float.isFinite(averageTickMillis) || averageTickMillis < 0) return 4_000_000L;
        double availableMillis = Math.max(2.0, Math.min(12.0, 40.0 - averageTickMillis));
        return (long) (availableMillis * 1_000_000L);
    }

    static long nanos(float serverMillis,float frameMillis) {
        long clientLimit=frameMillis>40?1_000_000L:frameMillis>25?3_000_000L:frameMillis>16.7?6_000_000L:12_000_000L;
        return Math.min(nanos(serverMillis),clientLimit);
    }

    static int placementLimit(float frameMillis) {
        return frameMillis>40?256:frameMillis>25?1024:frameMillis>16.7?4096:16384;
    }
}
