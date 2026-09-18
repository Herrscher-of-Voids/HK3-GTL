package com.sirin.hk3gtl.common.data;



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
