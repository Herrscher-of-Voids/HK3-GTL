package com.sirin.hk3gtl.common.farview;

/** 客户端缓存范围可能大于实际绘制范围，缓存命中本身不能隐藏远景。 */
public final class Hk3FarViewMask {
    private Hk3FarViewMask() {}
    public static boolean covered(boolean loaded,int dx,int dz,int renderDistance) {
        int radius=Math.max(1,renderDistance-2);
        return loaded && (long)dx*dx+(long)dz*dz < (long)radius*radius;
    }
}
