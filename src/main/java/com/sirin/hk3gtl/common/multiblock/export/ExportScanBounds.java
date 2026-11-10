package com.sirin.hk3gtl.common.multiblock.export;

/**
 * 【文件职责】提供不依赖游戏运行时的导出预算、坐标与区块边界校验，由 StructureScanner 调用。
 * 【变更记录 #1】2026-10-31 17:44:08（第 1 次备注 · 修订 189）
 * - 删除：无。
 * - 新增：全选区 262144 格、单轴 256 格预算，合法高度、世界水平边界和控制器包含校验。
 * - 修改：坐标差先转 long，校验后才分配字符矩阵；局部坐标仅包含控制器平面及背后。
 * - 用途：同步导出前拒绝超预算或非法选区，避免溢出、负索引与逐格中间对象堆积。
 */
final class ExportScanBounds {
    static final int MAX_BLOCKS = 262_144;
    static final int MAX_AXIS = 256;
    private static final int WORLD_LIMIT = 30_000_000;

    record Point(int x, int y, int z) {}
    final Point min;
    final Point max;
    final Point controller;

    private ExportScanBounds(Point min, Point max, Point controller) {
        this.min = min;
        this.max = max;
        this.controller = controller;
    }

    static ExportScanBounds create(Point a, Point b, Point controller, int minHeight, int maxHeight) {
        Point min = new Point(Math.min(a.x, b.x), Math.min(a.y, b.y), Math.min(a.z, b.z));
        Point max = new Point(Math.max(a.x, b.x), Math.max(a.y, b.y), Math.max(a.z, b.z));
        if (min.x < -WORLD_LIMIT || max.x >= WORLD_LIMIT || min.z < -WORLD_LIMIT || max.z >= WORLD_LIMIT) {
            throw new IllegalArgumentException("选区超出世界水平坐标范围");
        }
        if (min.y < minHeight || max.y >= maxHeight) {
            throw new IllegalArgumentException("选区超出世界建筑高度：[" + minHeight + ", " + maxHeight + ")");
        }
        long width = (long) max.x - min.x + 1;
        long height = (long) max.y - min.y + 1;
        long depth = (long) max.z - min.z + 1;
        if (width > MAX_AXIS || height > MAX_AXIS || depth > MAX_AXIS
                || width * height * depth > MAX_BLOCKS) {
            throw new IllegalArgumentException("选区 " + width + "×" + height + "×" + depth
                    + " 超过同步导出预算：最多 " + MAX_BLOCKS
                    + " 格，单轴最多 " + MAX_AXIS + " 格");
        }
        if (controller.x < min.x || controller.x > max.x || controller.y < min.y || controller.y > max.y
                || controller.z < min.z || controller.z > max.z) {
            throw new IllegalArgumentException("控制器坐标不在选区范围内");
        }
        return new ExportScanBounds(min, max, controller);
    }

    /** 朝向为水平单位向量；所有空气和实体方块采用相同的前方裁剪边界。 */
    Frame frame(int frontX, int frontZ) {
        if (Math.abs(frontX) + Math.abs(frontZ) != 1) {
            throw new IllegalArgumentException("控制器必须具有水平朝向");
        }
        int rightX = -frontZ;
        int rightZ = frontX;
        int minLocalX = Math.min((min.x - controller.x) * rightX, (max.x - controller.x) * rightX)
                + Math.min((min.z - controller.z) * rightZ, (max.z - controller.z) * rightZ);
        int maxLocalX = Math.max((min.x - controller.x) * rightX, (max.x - controller.x) * rightX)
                + Math.max((min.z - controller.z) * rightZ, (max.z - controller.z) * rightZ);
        int maxLocalZ = Math.max((min.x - controller.x) * -frontX, (max.x - controller.x) * -frontX)
                + Math.max((min.z - controller.z) * -frontZ, (max.z - controller.z) * -frontZ);
        return new Frame(maxLocalX - minLocalX + 1, max.y - min.y + 1, maxLocalZ + 1,
                minLocalX, min.y - controller.y, rightX, rightZ, -frontX, -frontZ, controller);
    }

    record Frame(int width, int height, int depth, int minLocalX, int minLocalY,
                 int rightX, int rightZ, int backX, int backZ, Point controller) {
        int worldX(int gx, int gz) { return controller.x + (gx + minLocalX) * rightX + gz * backX; }
        int worldY(int gy) { return controller.y + gy + minLocalY; }
        int worldZ(int gx, int gz) { return controller.z + (gx + minLocalX) * rightZ + gz * backZ; }
    }
}
