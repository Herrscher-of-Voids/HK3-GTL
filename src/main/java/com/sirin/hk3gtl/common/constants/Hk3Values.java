package com.sirin.hk3gtl.common.constants;



/**
 * 扩展电压数值查询的公开入口类。
 *
 * <p>职责：继承 {@link Hk3ValuesImpl}，外部统一通过本类查询电压值、颜色、显示名等数值信息。</p>
 *
 * <p>实现类：{@link Hk3ValuesImpl}（包含全部 31 元素数组和安全 getter 方法）</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增数值查询方法请在 {@link Hk3ValuesImpl} 中添加，本类自动继承</li>
 *   <li>tier 15+ 的电压值超出 int 范围，必须使用 long 类型（{@code VA_LONG}）</li>
 *   <li>所有 getter 方法已内置边界检查和 fallback，Mixin 失败时不会崩溃</li>
 * </ul>
 *
 * @see Hk3ValuesImpl 数值定义与安全 getter
 * @see Hk3Tiers  tier 索引常量
 */
public class Hk3Values extends Hk3ValuesImpl {
}
