package com.sirin.hk3gtl.common.multiblock.pattern;

import net.minecraft.nbt.CompoundTag;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/** 2026-10-30：只在显式测试开关下为I34准备无空气数组的完整预览，不改变正式Pattern。 */
public final class Hk3PreviewPrototype {
    public static final String PROPERTY = "hk3gtl.previewPrototype";
    public static final String I34 = "hk3gtl:i34_imaginary_tree_observation_array";

    public record Data(Hk3W01HallLayout layout, Map<Long, CompoundTag> entities) {}

    private Hk3PreviewPrototype() {}

    public static boolean selected(String id) { return Boolean.getBoolean(PROPERTY) && I34.equals(id); }

    private static final class Holder { static final Data DATA = loadI34(); }

    public static Data i34() { return Holder.DATA; }

    public static Data loadI34() {
        class Read {
            Hk3LargeArchitectureShapes.Header header;
            long[] cells;
            int next;
            final Map<Long, CompoundTag> entities = new HashMap<>();
        }
        Read data = new Read();
        try (var resource = Hk3StructureStream.open("i34")) {
            if (resource == null) throw new IOException("I34预览资源缺失");
            Hk3LargeArchitectureShapes.read(resource, header -> {
                if (header.width() > 1024 || header.height() > 1024 || header.depth() > 1024)
                    throw new IllegalArgumentException("测试预览坐标超出十位编码");
                data.header = header;
                data.cells = new long[header.count()];
            }, (linear, state, entity) -> {
                var h = data.header;
                int z = linear % h.depth(), y = linear / h.depth() % h.height(), x = linear / h.depth() / h.height();
                long cell = Hk3W01HallLayout.pack(x,y,z,state);
                data.cells[data.next++] = cell;
                if (entity != null) data.entities.put(cell >>> 16, entity);
            });
        } catch (IOException failure) {
            throw new IllegalStateException("I34稀疏测试预览读取失败", failure);
        }
        Arrays.sort(data.cells);
        var h = data.header;
        return new Data(new Hk3W01HallLayout(h.width(), h.height(), h.depth(), h.controllerX(),
                h.controllerY(), h.controllerZ(), h.palette(), data.cells), Map.copyOf(data.entities));
    }
}
