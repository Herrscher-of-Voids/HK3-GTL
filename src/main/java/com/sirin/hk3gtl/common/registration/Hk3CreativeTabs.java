package com.sirin.hk3gtl.common.registration;



/**
 * 创造物品栏注册入口（桥接类 / 重导出类）。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>仅作为空壳转发，真正实现位于 {@link Hk3CreativeTabsImpl}</li>
 *   <li>通过继承 Impl 暴露所有 CreativeModeTab / RegistryObject 常量</li>
 *   <li>所有外部代码统一通过本类或 {@link com.sirin.hk3gtl.common.data.Hk3CreativeTabs} 引用</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增创造物品栏：请去 {@link Hk3CreativeTabsImpl} 添加字段并在 register() 中注册</li>
 *   <li>本类禁止添加任何字段或方法，必须保持空桥接</li>
 *   <li>修改物品栏图标/显示物品：同步更新对应语言文件 en_us.json / zh_cn.json 中的 itemGroup 键</li>
 *   <li>如切换加载器（Fabric/NeoForge）实现：在子模块创建同路径类覆盖此门面</li>
 * </ul>
 */
public class Hk3CreativeTabs extends Hk3CreativeTabsImpl {
}
