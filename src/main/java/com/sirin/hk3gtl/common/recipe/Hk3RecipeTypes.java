package com.sirin.hk3gtl.common.recipe;



/**
 * 配方类型入口（桥接类 / 重导出类）。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>仅作为空壳转发，真正实现位于 {@link Hk3RecipeTypesImpl}</li>
 *   <li>通过继承 Impl 暴露所有 GTRecipeType 常量（如研究、熔炼、虚数合成等配方类型）</li>
 *   <li>所有引用配方类型的代码统一走本类或其重导出 {@link com.sirin.hk3gtl.common.data.Hk3RecipeTypes}</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增配方类型：请去 {@link Hk3RecipeTypesImpl} 中新增 public static final 字段并在 init() 注册</li>
 *   <li>本类禁止写任何字段或方法，必须保持空桥接</li>
 *   <li>删改配方类型会影响所有配方 JSON、多方块 recipeType 绑定及 JEI 展示，改动前需全局搜索引用</li>
 * </ul>
 */
public class Hk3RecipeTypes extends Hk3RecipeTypesImpl {
}
