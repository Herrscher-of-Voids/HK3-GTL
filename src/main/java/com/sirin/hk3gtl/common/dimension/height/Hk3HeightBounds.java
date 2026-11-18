package com.sirin.hk3gtl.common.dimension.height;









public record Hk3HeightBounds(int originalMinY, int originalHeight, int logicalHeight,
                              int newHeight, int newTopExclusive) {
    public Hk3HeightBounds {
        Hk3HeightPolicy.validateExpandedBounds(originalMinY, originalHeight, logicalHeight,
                newHeight, newTopExclusive);
    }
}
