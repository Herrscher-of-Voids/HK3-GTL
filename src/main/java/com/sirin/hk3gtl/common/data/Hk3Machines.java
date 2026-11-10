package com.sirin.hk3gtl.common.data;


/**
 * 【文件职责】
 * - 维护 Hk3Machines 的核心功能实现。
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
 * 多方块机器定义入口（data 包下的重导出 / 兼容别名类）。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>仅做类型重导出，真正实现位于 {@link com.sirin.hk3gtl.common.machine.Hk3Machines}</li>
 *   <li>为老代码提供 com.sirin.hk3gtl.common.data 路径下的兼容引用</li>
 *   <li>外部引用 MultiblockMachineDefinition 常量（如 HONKAI_ABSORPTION_TOWER 等）均通过本类或其实现类访问</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增机器：请去 {@link com.sirin.hk3gtl.common.machine.Hk3Machines} 中按注册流程添加</li>
 *   <li>本类严禁添加任何字段或方法，保持纯转发</li>
 *   <li>新代码推荐直接使用 common.machine 包下的原始类</li>
 * </ul>
 */
public class Hk3Machines extends com.sirin.hk3gtl.common.machine.Hk3Machines {
}
