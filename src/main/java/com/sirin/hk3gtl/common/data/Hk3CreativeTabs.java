package com.sirin.hk3gtl.common.data;



/**
 * 创造模式物品栏入口（data 包下的重导出 / 兼容别名类）。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>仅做类型重导出，真正实现位于 {@link com.sirin.hk3gtl.common.registration.Hk3CreativeTabs}
 *       并继续向上委托到 Impl 类</li>
 *   <li>为老代码提供 com.sirin.hk3gtl.common.data.Hk3CreativeTabs 路径的兼容引用</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增创造物品栏：请去对应 Impl 类（Hk3CreativeTabsImpl）中添加</li>
 *   <li>本类严禁添加任何字段或方法，保持纯转发</li>
 *   <li>新代码推荐使用 {@link com.sirin.hk3gtl.common.registration.Hk3CreativeTabs}</li>
 * </ul>
 */
public class Hk3CreativeTabs extends com.sirin.hk3gtl.common.registration.Hk3CreativeTabs {
}
