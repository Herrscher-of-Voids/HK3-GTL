package com.sirin.hk3gtl.common.entity;

/**
 * 
 * - 西琳终局出场相关功能开关；内测二关闭出场动画，逻辑归档至 {@code archive.entrance}。
 *
 */
public final class SirinEntranceFeatures {

    /** 终局出场粒子/凝聚动画（已修复翅膀跟随与朝向）。 */
    public static final boolean ENTRANCE_ANIMATION_ENABLED = true;

    /** 西琳 BakedModel 翅膀层。 */
    public static final boolean WING_LAYER_ENABLED = true;

    private SirinEntranceFeatures() {}
}
