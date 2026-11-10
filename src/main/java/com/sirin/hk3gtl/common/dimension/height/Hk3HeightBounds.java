package com.sirin.hk3gtl.common.dimension.height;

/**
 * 【文件职责】记录一个维度类型扩展前的生成边界与扩展后的建筑边界，不持有世界或注册表。
 * 【变更记录 #1】2026-10-17 21:24:01（修订166）
 * - 删除：无。
 * - 新增：不可变高度快照及原版编码、对齐、逻辑高度与禁止缩界的构造校验。
 * - 修改：无旧数据迁移；非法快照直接拒绝，由世界合同入口报告错误。
 * - 用途：供高度策略计算、存档合同持久化与注册表漂移核验共享同一边界定义。
 */
public record Hk3HeightBounds(int originalMinY, int originalHeight, int logicalHeight,
                              int newHeight, int newTopExclusive) {
    public Hk3HeightBounds {
        Hk3HeightPolicy.validateExpandedBounds(originalMinY, originalHeight, logicalHeight,
                newHeight, newTopExclusive);
    }
}
