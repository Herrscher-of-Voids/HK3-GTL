package com.sirin.hk3gtl.common.multiblock.export;

import java.util.HashSet;
import java.util.Set;

/**
 * 【文件职责】以纯 Java 验证生产导出选区预算与四朝向坐标裁剪，无需启动 Minecraft。
 * 【变更记录 #1】2026-10-31 17:44:08（第 1 次备注 · 修订 189）
 * - 删除：无。
 * - 新增：四朝向、反向角点、控制器前方空气对应区域、极端整数、高度和预算边界回归。
 * - 修改：无。
 * - 用途：阻止负矩阵索引、超预算分配与局部坐标旋转回归；断言失败直接终止测试主类。
 */
public final class ExportScanBoundsTest {
    private static int checks;

    public static void main(String[] args) {
        var origin = point(0, 0, 0);
        var bounds = ExportScanBounds.create(point(-2, -1, -3), point(4, 2, 5), origin, -64, 320);
        var reversed = ExportScanBounds.create(point(4, 2, 5), point(-2, -1, -3), origin, -64, 320);
        for (int[] facing : new int[][] {{0, -1}, {1, 0}, {0, 1}, {-1, 0}}) {
            var frame = bounds.frame(facing[0], facing[1]);
            check(frame.equals(reversed.frame(facing[0], facing[1])), "交换角点不能改变输出");
            Set<ExportScanBounds.Point> actual = new HashSet<>();
            for (int z = 0; z < frame.depth(); z++) {
                for (int y = 0; y < frame.height(); y++) {
                    for (int x = 0; x < frame.width(); x++) {
                        var world = point(frame.worldX(x, z), frame.worldY(y), frame.worldZ(x, z));
                        check(actual.add(world), "坐标转换不能重复");
                        check(world.x() * facing[0] + world.z() * facing[1] <= 0,
                                "前方区域无论空气或实体都必须裁去");
                    }
                }
            }
            Set<ExportScanBounds.Point> expected = new HashSet<>();
            for (int x = -2; x <= 4; x++) {
                for (int y = -1; y <= 2; y++) {
                    for (int z = -3; z <= 5; z++) {
                        if (x * facing[0] + z * facing[1] <= 0) expected.add(point(x, y, z));
                    }
                }
            }
            check(actual.equals(expected), "四朝向都应精确覆盖控制器平面与背后");
            check(actual.contains(origin), "控制器必须保留");
        }
        var shifted = ExportScanBounds.create(point(-100, 40, -90), point(-96, 43, -82),
                point(-99, 41, -88), -64, 320).frame(0, -1);
        check(shifted.worldX(-shifted.minLocalX(), 0) == -99
                && shifted.worldY(-shifted.minLocalY()) == 41
                && shifted.worldZ(-shifted.minLocalX(), 0) == -88, "非原点控制器应映射至自身坐标");
        check(ExportScanBounds.create(origin, point(63, 63, 63), origin, -64, 320)
                .frame(0, -1).width() == 64, "体积恰好等于预算应允许");
        rejected(origin, point(64, 63, 63), origin, -64, 320, "预算");
        rejected(origin, point(256, 0, 0), origin, -64, 320, "预算");
        rejected(point(0, -65, 0), origin, origin, -64, 320, "高度");
        rejected(origin, point(0, 320, 0), origin, -64, 320, "高度");
        rejected(origin, point(1, 1, 1), point(2, 0, 0), -64, 320, "控制器");
        rejected(point(Integer.MIN_VALUE, 0, 0), point(Integer.MAX_VALUE, 0, 0), origin,
                -64, 320, "水平坐标");
        rejected(point(0, Integer.MIN_VALUE, 0), point(0, Integer.MAX_VALUE, 0), origin,
                Integer.MIN_VALUE, Integer.MAX_VALUE, "高度");
        rejected(point(30_000_000, 0, 0), point(30_000_000, 0, 0), origin, -64, 320, "水平坐标");
        var edge = point(-30_000_000, -64, 29_999_999);
        check(ExportScanBounds.create(edge, edge, edge, -64, 320).frame(1, 0).depth() == 1,
                "合法水平与最低高度边界应保留");
        try {
            bounds.frame(1, 1);
            throw new AssertionError("非水平单位朝向必须拒绝");
        } catch (IllegalArgumentException expected) { checks++; }
        System.out.println("ExportScanBoundsTest 通过：" + checks + " 项断言");
    }

    private static ExportScanBounds.Point point(int x, int y, int z) {
        return new ExportScanBounds.Point(x, y, z);
    }

    private static void rejected(ExportScanBounds.Point a, ExportScanBounds.Point b,
                                 ExportScanBounds.Point controller, int min, int max, String message) {
        try {
            ExportScanBounds.create(a, b, controller, min, max);
            throw new AssertionError("应拒绝非法选区：" + message);
        } catch (IllegalArgumentException expected) {
            check(expected.getMessage().contains(message), "拒绝原因应准确：" + expected.getMessage());
        }
    }

    private static void check(boolean value, String message) {
        checks++;
        if (!value) throw new AssertionError(message);
    }
}
