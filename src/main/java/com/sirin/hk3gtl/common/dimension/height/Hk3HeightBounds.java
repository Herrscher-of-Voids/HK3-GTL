package com.sirin.hk3gtl.common.dimension.height;

/**
 * 记录一个维度类型扩展前的生成边界与扩展后的建筑边界，不持有世界或注册表。
 */
public record Hk3HeightBounds(int originalMinY, int originalHeight, int logicalHeight,
                              int newHeight, int newTopExclusive) {
    public Hk3HeightBounds {
        Hk3HeightPolicy.validateExpandedBounds(originalMinY, originalHeight, logicalHeight,
                newHeight, newTopExclusive);
    }
}
