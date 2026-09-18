package com.sirin.hk3gtl.common.machine.multiblock.part;



import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;

/**
 * 本模组自定义的 PartAbility (仓室能力标识)。
 * 用于识别自定义的仓室（如崩坏能输入仓/输出仓等）。
 *
 * <p>符合 OCP 开闭原则，使用 PartAbility 挂载到原版多方块框架中，
 * 无需手写全新的多方块扫描系统，兼容 GTCEu 的所有扫描逻辑和渲染。</p>
 */
public class Hk3PartAbility {
    /** 崩坏能输入能力 */
    public static final PartAbility HONKAI_ENERGY_INPUT = new PartAbility("honkai_energy_input");
    /** 崩坏能输出能力 */
    public static final PartAbility HONKAI_ENERGY_OUTPUT = new PartAbility("honkai_energy_output");

    /** 无线崩坏能输入能力 */
    public static final PartAbility WIRELESS_HONKAI_INPUT = new PartAbility("wireless_honkai_input");
    /** 无线崩坏能输出能力 */
    public static final PartAbility WIRELESS_HONKAI_OUTPUT = new PartAbility("wireless_honkai_output");
}
