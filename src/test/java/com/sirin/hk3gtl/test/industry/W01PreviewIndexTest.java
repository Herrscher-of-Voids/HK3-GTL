package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01PreviewIndex;

/** W01真实资源逐实体二分查询、空气边界和逐层/材料计数回归；不启动Minecraft。 */
// 变更记录#1：2026-10-30 00:09:26，修订183：匹配干燥清理后的276状态及1932713实体，保留全量逐格核验。
public final class W01PreviewIndexTest {
    public static void main(String[] args) {
        var layout = Hk3W01HallLayout.load();
        var index = new Hk3W01PreviewIndex(layout);
        long totalLayers = 0, totalMaterials = 0;
        for (int y = 0; y < layout.height(); y++) totalLayers += index.countLayer(y);
        for (int material = 0; material < layout.palette().size(); material++) {
            totalMaterials += index.countMaterial(material);
            if (index.countMaterial(material) > 0) {
                long first = index.firstCell(material);
                require(index.stateAt(Hk3W01HallLayout.x(first), Hk3W01HallLayout.y(first), Hk3W01HallLayout.z(first)) == material,
                        "材料取样坐标不符");
            }
        }
        require(totalLayers == 1_932_713 && totalMaterials == totalLayers && index.countLayer(-1) == totalLayers, "实体计数不符");
        for (long cell : layout.cells()) {
            int x = Hk3W01HallLayout.x(cell), y = Hk3W01HallLayout.y(cell), z = Hk3W01HallLayout.z(cell);
            require(index.stateAt(x, y, z) == Hk3W01HallLayout.state(cell), "实体坐标或状态丢失");
        }
        require(index.stateAt(-1, 0, 0) == -1 && index.stateAt(0, -1, 0) == -1 && index.stateAt(0, 0, -1) == -1,
                "负坐标误匹配");
        require(index.stateAt(layout.width(), 0, 0) == -1 && index.stateAt(0, layout.height(), 0) == -1
                && index.stateAt(0, 0, layout.depth()) == -1, "包围盒边界误匹配");
        require(index.stateAt(0, 0, 0) == -1, "原空气不能新增实体");
        require(index.stateAt(layout.controllerX(), layout.controllerY(), layout.controllerZ()) >= 0, "主控缺失");
        System.out.println("W01预览索引通过：1932713格逐一命中，383层与276状态计数守恒，空气和越界不匹配。");
    }
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
