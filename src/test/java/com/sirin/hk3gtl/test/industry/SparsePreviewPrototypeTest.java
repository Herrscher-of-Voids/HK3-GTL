package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3PreviewPrototype;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01PreviewIndex;

/** 两份真实蓝图全量坐标、状态、材料和分层守恒；堆上限测试不等同于游戏总内存。 */
public final class SparsePreviewPrototypeTest {
    public static void main(String[] args) throws Exception {
        String id = args.length == 0 ? "i34" : args[0];
        require(!Hk3PreviewPrototype.selected(Hk3PreviewPrototype.I34), "测试开关默认不能接管JEI");
        System.setProperty(Hk3PreviewPrototype.PROPERTY, "true");
        require(Hk3PreviewPrototype.selected(Hk3PreviewPrototype.I34)
                && !Hk3PreviewPrototype.selected("gtceu:assembly_line")
                && !Hk3PreviewPrototype.selected("hk3gtl:i35_imaginary_space_anchoring_array"), "预览分流越界");
        long start = System.nanoTime();
        var data = id.equals("w01") ? null : Hk3PreviewPrototype.loadI34();
        var layout = data == null ? Hk3W01HallLayout.load() : data.layout();
        var index = new Hk3W01PreviewIndex(layout);
        long layers = 0, materials = 0;
        for (int y = 0; y < layout.height(); y++) layers += index.countLayer(y);
        for (int s = 0; s < layout.palette().size(); s++) materials += index.countMaterial(s);
        require(layers == layout.cells().length && materials == layers, "材料或逐层计数丢失");
        for (long cell : layout.cells()) require(index.stateAt(Hk3W01HallLayout.x(cell), Hk3W01HallLayout.y(cell),
                Hk3W01HallLayout.z(cell)) == Hk3W01HallLayout.state(cell), "稀疏坐标丢失");
        if (data != null) try (var input = Hk3PreviewPrototype.class.getResourceAsStream(
                "/data/hk3gtl/structures/approved_preview/i34.bin.gz")) {
            var header = Hk3LargeArchitectureShapes.read(input, h -> {}, (linear, palette, entity) -> {
                int d = layout.depth(), h = layout.height();
                int x = linear / d / h, y = linear / d % h, z = linear % d;
                require(index.stateAt(x, y, z) == palette, "与原始HK3P状态不一致");
                long coordinate = Hk3W01HallLayout.pack(x,y,z,0)>>>16;
                require(java.util.Objects.equals(entity, data.entities().get(coordinate)), "方块实体数据不一致");
            });
            require(header.count() == layout.cells().length, "完整蓝图计数不一致");
        }
        require(index.stateAt(-1, 0, 0) == -1 && index.stateAt(layout.width(), 0, 0) == -1, "边界不正确");
        long volume = (long) layout.width() * layout.height() * layout.depth();
        long sparseBytes = (long) layout.cells().length * Long.BYTES;
        long denseReferenceBytes = volume * 4;
        System.out.printf(java.util.Locale.ROOT,
                "{\"id\":\"%s\",\"blocks\":%d,\"size\":[%d,%d,%d],\"palette\":%d,\"sparse_coordinate_bytes\":%d,\"dense_reference_bytes_4byte_assumption\":%d,\"heap_limit_bytes\":%d,\"elapsed_ms\":%.1f,\"all_coordinates_verified\":true}%n",
                id, layout.cells().length, layout.width(), layout.height(), layout.depth(), layout.palette().size(),
                sparseBytes, denseReferenceBytes, Runtime.getRuntime().maxMemory(), (System.nanoTime() - start) / 1e6);
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
