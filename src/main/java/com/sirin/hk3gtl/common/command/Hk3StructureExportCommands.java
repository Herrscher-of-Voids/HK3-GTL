package com.sirin.hk3gtl.common.command;


/**
 * 【文件职责】
 * - 维护 Hk3StructureExportCommands 的核心功能实现。
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
 * 多方块结构导出命令的公开门面类（Facade）。
 *
 * <h3>命令语义</h3>
 * <ul>
 *   <li>{@code /hk3export save <name>} — 将当前结构导出棒的选区保存为 txt + Java 草稿</li>
 *   <li>{@code /hk3export info}        — 聊天框打印当前选区状态</li>
 *   <li>{@code /hk3export clear}       — 清空结构导出棒的 pos1 / pos2 / controller 三项 NBT</li>
 * </ul>
 *
 * <h3>使用流程</h3>
 * <ol>
 *   <li>{@code /give @s hk3gtl:structure_export_wand}</li>
 *   <li>潜行+右键某个方块 = pos1（选区对角点 A）</li>
 *   <li>右键控制器方块（带水平朝向、非外壳/玻璃/线圈）= ctrl</li>
 *   <li>右键另一个方块 = pos2（选区对角点 B）</li>
 *   <li>{@code /hk3export save my_machine_name}</li>
 *   <li>到 {@code <serverDir>/hk3gtl_exports/} 获取 txt 产物</li>
 * </ol>
 *
 * <h3>产物说明</h3>
 * <ul>
 *   <li>{@code <name>.txt} — 可视化结构 + 图例 + WARN</li>
 *   <li>{@code <name>_pattern_impl.txt} — 复制到 {@code common/multiblock/pattern/Hk3XxxPatternImpl.java}</li>
 *   <li>{@code <name>_pattern_facade.txt} — 复制到 {@code Hk3XxxPattern.java}（门面）</li>
 *   <li>{@code <name>_machine.txt} — 字段声明 + init() 片段，复制到对应 {@code Hk3Machines<Stage>Impl.java}</li>
 * </ul>
 *
 * <p>真正的实现位于 {@link Hk3StructureExportCommandsImpl}。本类仅作继承门面，方便在
 * 不破坏继承关系的前提下扩展 / Mock。</p>
 *
 * @see Hk3StructureExportCommandsImpl
 */
public class Hk3StructureExportCommands extends Hk3StructureExportCommandsImpl {
}
