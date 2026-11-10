package com.sirin.hk3gtl.common.dimension.height;

/**
 * 【文件职责】每个世界数据对象独立持有冻结高度合同与本次应用状态，无跨世界静态开关。
 * 【变更记录 #1】2026-10-17 21:19:41（第1次备注 · 修订166）
 * - 删除：无。新增：PrimaryLevelData的实例合同接口；修改：无旧数据改写。
 * - 用途：新建、保存、加载、早期注册表应用共用同一世界身份；空合同代表保持原高度。
 */
public interface Hk3HeightWorldData {
    Hk3HeightWorldState hk3gtl$getHeightState();
    void hk3gtl$setHeightState(Hk3HeightWorldState state);
    boolean hk3gtl$isHeightApplied();
    void hk3gtl$markHeightApplied();
}
