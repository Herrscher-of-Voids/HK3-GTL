package com.sirin.hk3gtl.common.data;


/**
 * 【文件职责】
 * - 维护 Hk3Constants 的核心功能实现。
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
/**
 * 常量入口（data 包下的重导出 / 兼容别名类）。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>仅做类型重导出，真正实现位于 {@link com.sirin.hk3gtl.common.constants.Hk3Constants}
 *       并继续向上委托到 {@link com.sirin.hk3gtl.common.constants.Hk3ConstantsImpl}</li>
 *   <li>历史包路径遗留：部分代码习惯从 common.data 包引用常量，保留此空壳以兼容</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增或修改常量：请去 {@link com.sirin.hk3gtl.common.constants.Hk3ConstantsImpl}</li>
 *   <li>本类严禁添加任何字段或方法，保持纯转发</li>
 *   <li>新代码推荐直接引用 {@link com.sirin.hk3gtl.common.constants.Hk3Constants}，减少多跳</li>
 * </ul>
 */
public class Hk3Constants extends com.sirin.hk3gtl.common.constants.Hk3Constants {
}
