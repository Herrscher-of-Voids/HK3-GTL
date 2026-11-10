package com.sirin.hk3gtl.common.entity;

/**
 * 【文件职责】
 * - 西琳终局出场相关功能开关；内测二关闭出场动画，逻辑归档至 {@code archive.entrance}。
 *
 * 【变更记录 #1】2026-05-19 04:25:00（第 1 次备注 · 内测二第 3 次更新）
 * - 新增：{@link #ENTRANCE_ANIMATION_ENABLED} 内测二为 false。
 * - 用途：统一控制服务端粒子出场与客户端翅膀层是否参与终局演出。
 */
public final class SirinEntranceFeatures {

    /** 终局出场粒子/凝聚动画（已修复翅膀跟随与朝向）。 */
    public static final boolean ENTRANCE_ANIMATION_ENABLED = true;

    /** 西琳 BakedModel 翅膀层。 */
    public static final boolean WING_LAYER_ENABLED = true;

    private SirinEntranceFeatures() {}
}
