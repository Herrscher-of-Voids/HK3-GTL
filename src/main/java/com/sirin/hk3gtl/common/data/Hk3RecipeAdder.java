package com.sirin.hk3gtl.common.data;



/**
 * 配方注入器入口（data 包下的重导出 / 兼容别名类）。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>仅做类型重导出，真正转发链为：
 *       本类 → {@link com.sirin.hk3gtl.common.recipe.Hk3RecipeAdder}
 *       → {@link com.sirin.hk3gtl.common.recipe.Hk3RecipeAdderImpl}（最终实现）</li>
 *   <li>为配方引导/数据生成模块提供稳定的 common.data.Hk3RecipeAdder 引用路径</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增配方注入逻辑：请去 Hk3RecipeAdderImpl 中添加</li>
 *   <li>本类严禁添加任何字段或方法，保持纯转发</li>
 *   <li>如需在数据生成流程中引用，请保留此类路径以免破坏既有 import</li>
 * </ul>
 */
public class Hk3RecipeAdder extends com.sirin.hk3gtl.common.recipe.Hk3RecipeAdder {
}
