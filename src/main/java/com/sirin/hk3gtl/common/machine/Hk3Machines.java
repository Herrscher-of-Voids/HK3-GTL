package com.sirin.hk3gtl.common.machine;



/**
 * 多方块机器注册的公开门面类。
 *
 * <h3>职责</h3>
 * 定义并注册所有 HK3GTL 多方块控制器，通过 GTRegistrate 绑定：
 * <ul>
 *   <li>配方类型（{@link com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes}）</li>
 *   <li>结构 Pattern（{@code pattern} 包下各 Pattern 类）</li>
 *   <li>外观方块与渲染贴图</li>
 * </ul>
 *
 * <h3>注册顺序</h3>
 * P1 核心 4 台 → Max 阶段 → 海渊 → 虚数 → 量子 → 终焉 → 奇观，
 * 由 {@link Hk3MachinesImpl#init()} 统一调度。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增机器 → 在对应阶段子类中添加（如 {@code Hk3MachinesAbyssStage}）</li>
 *   <li>切换正式结构 → 将 {@code Hk3TemporaryMultiblockPatterns} 替换为对应 Pattern 类</li>
 *   <li>所有多方块必须使用 {@code Hk3WorkableMultiblockMachine} 基类</li>
 * </ul>
 *
 * @see Hk3MachinesImpl
 */
public class Hk3Machines extends Hk3MachinesImpl {
}
