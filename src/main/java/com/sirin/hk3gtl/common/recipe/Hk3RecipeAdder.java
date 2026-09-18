package com.sirin.hk3gtl.common.recipe;



/**
 * 配方注入器的对外门面（桥接类 / 重导出类）。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>仅作为空壳转发，真正实现位于 {@link Hk3RecipeAdderImpl}</li>
 *   <li>通过继承 Impl 暴露所有 public 静态方法，使外部调用统一用 Hk3RecipeAdder.xxx</li>
 *   <li>解耦：若将来切换实现（例如拆成 Forge/Fabric 分别实现），只需改 Impl，门面类无需动</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增配方注入逻辑：请去 {@link Hk3RecipeAdderImpl} 里加，不要在此添加任何方法</li>
 *   <li>本类必须保持为"空桥接"——禁止写字段、构造方法、静态代码块</li>
 *   <li>若需平台特定实现：在 forge/fabric 子模块创建同路径类覆盖此门面</li>
 *   <li>外部调用入口请统一使用 {@link com.sirin.hk3gtl.common.data.Hk3RecipeAdder}（再包一层的稳定引用）</li>
 * </ul>
 */
public class Hk3RecipeAdder extends Hk3RecipeAdderImpl {
}
