package com.sirin.hk3gtl.common.constants;



/**
 * 模组全局常量入口（桥接类 / 重导出类）。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>仅作为空壳转发，真正实现位于 {@link Hk3ConstantsImpl}</li>
 *   <li>通过继承 Impl 暴露所有 MOD_ID、毕业参数、注视度公式等 public static final 常量</li>
 *   <li>外部模块统一通过 Hk3Constants.XXX 引用，禁止直接访问 Impl</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增常量：请去 {@link Hk3ConstantsImpl} 中添加 public static final 字段</li>
 *   <li>本类严禁添加任何字段、方法或构造器，保持空桥接</li>
 *   <li>修改 MOD_ID 会影响所有资源路径、注册名、语言键、数据包——严禁轻易改动</li>
 *   <li>修改毕业 / 注视度等数值型常量需同步检查平衡性与已有存档兼容</li>
 * </ul>
 */
public class Hk3Constants extends Hk3ConstantsImpl {
}
