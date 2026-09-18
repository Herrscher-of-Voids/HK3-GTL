package com.sirin.hk3gtl.common.block.energy;



/**
 * 崩坏能仓的定义枚举 —— 把"是输入/输出/无线/创造"这种特征集中在一个值里，
 * 避免一份代码写 5 遍 Block + 5 遍 BlockEntity。
 *
 * <h3>字段含义</h3>
 * <ul>
 *   <li>{@link #id}：方块/物品注册 ID</li>
 *   <li>{@link #canInsertFromOutside}：外部能量能否注入（输入/创造 = true，纯输出 = false）</li>
 *   <li>{@link #canExtractFromOutside}：外部能量能否抽取（输出/创造 = true，纯输入 = false）</li>
 *   <li>{@link #wireless}：是否走无线网络（共享玩家池），true 时 capacity 使用池容量</li>
 *   <li>{@link #creative}：创造模式无限能量仓</li>
 *   <li>{@link #localCapacity}：本地缓冲容量（崩坏能单位）</li>
 * </ul>
 *
 * <h3>数值设计</h3>
 * <ul>
 *   <li>本地容量默认 10 万崩坏能（≈ 1 亿 EU），够 tier 15-18 机器稳定运行</li>
 *   <li>无线池由 {@code HonkaiWirelessNetwork} 使用 BigInteger 存储，容量无上限</li>
 *   <li>创造仓返回 {@link Long#MAX_VALUE}，标志"无限"</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增仓类型：在此枚举加常量 + 在 {@code Hk3HonkaiHatches} 中注册</li>
 *   <li>改容量：只改 {@link #localCapacity} 数值；如要给不同阶段不同容量，拆分成
 *       {@code HONKAI_INPUT_ABYSS / HONKAI_INPUT_IMAGINARY} 等多个变体</li>
 *   <li>改 insert / extract 语义：不要动枚举，去改 {@link HonkaiEnergyHatchBlockEntity}</li>
 * </ul>
 */
public enum HonkaiHatchType {
    /** 普通输入仓：外部→本仓的单向通道（机器从本仓抽电） */
    INPUT("honkai_energy_input_hatch", true, true, false, false, 100_000L),
    /** 普通输出仓：本仓→外部的单向通道（机器往本仓充电） */
    OUTPUT("honkai_energy_output_hatch", false, true, false, false, 100_000L),
    /** 无线输入仓：外部→玩家全局池 */
    WIRELESS_INPUT("wireless_honkai_input_hatch", true, false, true, false, 0L),
    /** 无线输出仓：玩家全局池→本地机器 */
    WIRELESS_OUTPUT("wireless_honkai_output_hatch", false, true, true, false, 0L),
    /** 创造仓：无限能量，不分方向，两端都能全速转移 */
    CREATIVE("creative_honkai_hatch", true, true, false, true, Long.MAX_VALUE);

    public final String id;
    public final boolean canInsertFromOutside;
    public final boolean canExtractFromOutside;
    public final boolean wireless;
    public final boolean creative;
    public final long localCapacity;

    HonkaiHatchType(String id, boolean canIn, boolean canOut, boolean wireless, boolean creative, long cap) {
        this.id = id;
        this.canInsertFromOutside = canIn;
        this.canExtractFromOutside = canOut;
        this.wireless = wireless;
        this.creative = creative;
        this.localCapacity = cap;
    }
}
