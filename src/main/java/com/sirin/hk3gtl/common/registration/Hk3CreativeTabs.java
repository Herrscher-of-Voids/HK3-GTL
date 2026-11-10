package com.sirin.hk3gtl.common.registration;


/**
 * 【文件职责】
 * - 维护 Hk3CreativeTabs 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
