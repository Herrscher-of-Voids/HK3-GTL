package com.sirin.hk3gtl.common.capability;



/**
 * 崩坏能容器接口（独立于 EU / FE 的新能源形式）。
 *
 * <h3>与 EU 的关系</h3>
 * <ul>
 *   <li>崩坏能与 EU 通过 {@code Hk3Constants.HONKAI_TO_EU_RATIO}（默认 1:1000）换算</li>
 *   <li>崩坏能仓 <b>不应</b> 自动从 EU 抽取能量，转换必须显式走"崩坏能-EU 双转换矩阵"机器</li>
 *   <li>EU 用 long 级数值 GT 已够用；崩坏能同样用 long，但数量级小 1000 倍</li>
 * </ul>
 *
 * <h3>实现契约</h3>
 * <ul>
 *   <li>{@link #insert} 与 {@link #extract} 必须原子性：返回值 = 实际成功转移的数量</li>
 *   <li>simulate = true 时不修改状态，仅返回"如果真的转移能转多少"</li>
 *   <li>禁止任何负数：调用方传入负数 / 实现返回负数都视为 bug</li>
 *   <li>{@link #canInsert} / {@link #canExtract} 给"仅输出" / "仅输入"类仓室一个快速拒绝的机会</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增"部分转移"语义（如转移率 80%）时：不要改本接口，去包装实现类</li>
 *   <li>新增持久化字段（如"最后交易时间"）：在 {@link HonkaiEnergyStorage} 扩展，接口保持最小</li>
 *   <li>不要把 Player / World 引用塞进本接口 —— Capability 应在"纯能量层"不依赖上下文</li>
 * </ul>
 */
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
