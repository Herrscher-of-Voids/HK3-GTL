package com.sirin.hk3gtl.common.data;



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
