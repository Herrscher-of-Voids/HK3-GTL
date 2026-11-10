package com.sirin.hk3gtl.common.dimension.height;

/**
 * 【文件职责】以纯函数计算建筑高度扩展，保留维度原始最低高度与逻辑高度，不改生成器。
 * 【变更记录 #1】2026-10-17 21:24:01（修订166）
 * - 删除：无。
 * - 新增：528至2032、16格对齐的目标上界和原版12位Y编码边界校验。
 * - 修改：扩展结果使用较大的原上界与目标上界；拒绝缩界、溢出和非法逻辑高度。
 * - 用途：供世界合同与运行时注册表应用复用；不访问配置、磁盘、静态世界状态或第三方类。
 */
public final class Hk3HeightPolicy {
    public static final int MIN_TOP_EXCLUSIVE = 528;
    public static final int MAX_TOP_EXCLUSIVE = 2032;
    public static final int MIN_ENCODED_Y = -2032;
    public static final int MAX_ENCODED_Y = 2031;
    public static final int MAX_ENCODED_HEIGHT = 4064;

    private Hk3HeightPolicy() {
    }

    public static boolean isValidTopExclusive(int topExclusive) {
        return topExclusive >= MIN_TOP_EXCLUSIVE && topExclusive <= MAX_TOP_EXCLUSIVE
                && topExclusive % 16 == 0;
    }

    public static int requireTopExclusive(int topExclusive) {
        if (!isValidTopExclusive(topExclusive)) {
            throw new IllegalArgumentException("建筑高度合同上界必须在528至2032之间且为16的倍数：" + topExclusive);
        }
        return topExclusive;
    }

    /** 目标低于原上界时保留原范围；所有加减先用长整数，避免损坏输入溢出。 */
    public static Hk3HeightBounds expand(int minY, int height, int logicalHeight, int topExclusive) {
        requireTopExclusive(topExclusive);
        validateOriginalBounds(minY, height, logicalHeight);
        long newTop = Math.max((long) minY + height, topExclusive);
        long newHeight = newTop - minY;
        if (newHeight > MAX_ENCODED_HEIGHT || newTop > MAX_ENCODED_Y + 1L) {
            throw new IllegalArgumentException("建筑高度扩展超过原版维度编码范围");
        }
        return new Hk3HeightBounds(minY, height, logicalHeight, (int) newHeight, (int) newTop);
    }

    public static Hk3HeightBounds unchanged(int minY, int height, int logicalHeight) {
        validateOriginalBounds(minY, height, logicalHeight);
        return new Hk3HeightBounds(minY, height, logicalHeight, height, minY + height);
    }

    public static void validateOriginalBounds(int minY, int height, int logicalHeight) {
        if (minY < MIN_ENCODED_Y || minY > MAX_ENCODED_Y || minY % 16 != 0) {
            throw new IllegalArgumentException("维度最低高度越界或未按16格对齐：" + minY);
        }
        if (height < 16 || height > MAX_ENCODED_HEIGHT || height % 16 != 0
                || (long) minY + height > MAX_ENCODED_Y + 1L) {
            throw new IllegalArgumentException("维度原始高度越界或未按16格对齐：" + height);
        }
        if (logicalHeight < 0 || logicalHeight > height) {
            throw new IllegalArgumentException("维度逻辑高度必须位于0与原始高度之间：" + logicalHeight);
        }
    }

    static void validateExpandedBounds(int minY, int originalHeight, int logicalHeight,
                                       int newHeight, int newTopExclusive) {
        validateOriginalBounds(minY, originalHeight, logicalHeight);
        if (newHeight < originalHeight || newHeight > MAX_ENCODED_HEIGHT || newHeight % 16 != 0
                || (long) minY + newHeight != newTopExclusive
                || newTopExclusive > MAX_ENCODED_Y + 1) {
            throw new IllegalArgumentException("维度建筑边界快照损坏、缩小或超过原版编码范围");
        }
    }
}
