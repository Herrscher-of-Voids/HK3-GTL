package com.sirin.hk3gtl.common.capability;

public interface IHonkaiEnergyContainer {

    /** 当前已储存的崩坏能量 */
    long getAmount();

    /** 容量上限；{@link Long#MAX_VALUE} 表示"创造/无限" */
    long getCapacity();

    /**
     * 向容器注入崩坏能。
     * @param amount    请求注入量（必须 ≥ 0）
     * @param simulate  true 时仅模拟，不修改状态
     * @return 实际注入量（0..amount），可能小于请求值（容量已满）
     */
    long insert(long amount, boolean simulate);

    /**
     * 从容器抽取崩坏能。
     * @param amount    请求抽取量（必须 ≥ 0）
     * @param simulate  true 时仅模拟，不修改状态
     * @return 实际抽取量（0..amount），可能小于请求值（存量不足）
     */
    long extract(long amount, boolean simulate);

    /** 是否接受外部注入。例：输出仓返回 false，使机器层级快速拒绝无意义尝试 */
    default boolean canInsert() { return true; }

    /** 是否接受外部抽取。例：输入仓返回 false */
    default boolean canExtract() { return true; }

    /** 当前填充率（0.0 ~ 1.0）；容量为 Long.MAX_VALUE 时返回 1.0 避免除零 */
    default double fillRatio() {
        long cap = getCapacity();
        if (cap <= 0 || cap == Long.MAX_VALUE) return 1.0;
        return (double) getAmount() / (double) cap;
    }
}
