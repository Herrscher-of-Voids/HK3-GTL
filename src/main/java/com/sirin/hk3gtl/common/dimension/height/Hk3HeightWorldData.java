package com.sirin.hk3gtl.common.dimension.height;

/**
 * 每个世界数据对象独立持有冻结高度合同与本次应用状态，无跨世界静态开关。
 */
public interface Hk3HeightWorldData {
    Hk3HeightWorldState hk3gtl$getHeightState();
    void hk3gtl$setHeightState(Hk3HeightWorldState state);
    boolean hk3gtl$isHeightApplied();
    void hk3gtl$markHeightApplied();
}
