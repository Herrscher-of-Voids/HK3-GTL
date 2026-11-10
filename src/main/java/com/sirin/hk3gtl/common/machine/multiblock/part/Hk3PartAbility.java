package com.sirin.hk3gtl.common.machine.multiblock.part;


/**
 * 【文件职责】
 * - 定义 Hk3PartAbility 机器行为与结构逻辑。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
