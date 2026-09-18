package com.sirin.hk3gtl.common.data;



/**
 * 配方类型入口（data 包下的重导出 / 兼容别名类）。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>仅做类型重导出，真正转发链为：
 *       本类 → {@link com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes}
 *       → {@link com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImpl}（最终实现）</li>
 *   <li>为配方/机器定义模块提供稳定的 common.data.Hk3RecipeTypes 引用路径</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增配方类型：请去 Hk3RecipeTypesImpl 中添加 public static final 字段并注册</li>
 *   <li>本类严禁添加任何字段或方法，保持纯转发</li>
 *   <li>删改配方类型会影响 JSON 数据包、JEI、机器 recipeType() 绑定，改动前需全局搜索引用</li>
 * </ul>
 */
public class Hk3RecipeTypes extends com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes {
}
