package com.sirin.hk3gtl.common.multiblock.pattern;

import java.util.BitSet;
import java.util.concurrent.CancellationException;

/**
 * 共享W01有序实体布局，提供无空气数组的坐标查询与逐层、逐状态计数。
 */
public final class Hk3W01PreviewIndex {
    private final Hk3W01HallLayout layout;
    private final int[] layers;
    private final int[] materials;
    private final long[] firstCells;
    private final int[] columns;
    private final long[] blockEntityCells;
    private final BitSet renderCells;
    private final int renderCount;

    public Hk3W01PreviewIndex(Hk3W01HallLayout layout) {
        this(layout, new boolean[layout.palette().size()]);
    }

    public Hk3W01PreviewIndex(Hk3W01HallLayout layout, boolean[] blockEntityStates) {
        this(layout, blockEntityStates, new boolean[layout.palette().size()]);
    }

    public Hk3W01PreviewIndex(Hk3W01HallLayout layout, boolean[] blockEntityStates, boolean[] opaqueStates) {
        this.layout = layout;
        layers = new int[layout.height()];
        materials = new int[layout.palette().size()];
        firstCells = new long[materials.length];
        columns = new int[layout.width() * layout.height() + 1];
        var entities = new it.unimi.dsi.fastutil.longs.LongArrayList();
        for (int i = 0; i < layout.count(); i++) {
            checkCancelled(i);
            long cell = layout.cell(i);
            layers[Hk3W01HallLayout.y(cell)]++;
            columns[Hk3W01HallLayout.x(cell) * layout.height() + Hk3W01HallLayout.y(cell) + 1]++;
            int state = Hk3W01HallLayout.state(cell);
            if (materials[state]++ == 0) firstCells[state] = cell;
            if (blockEntityStates[state]) entities.add(cell);
        }
        for (int i = 1; i < columns.length; i++) columns[i] += columns[i - 1];
        blockEntityCells = entities.toLongArray();
        renderCells = surfaceCells(blockEntityStates, opaqueStates);
        renderCount = renderCells.cardinality();
    }

    private BitSet surfaceCells(boolean[] blockEntityStates, boolean[] opaqueStates) {
        int count = layout.count();
        var exposed = new BitSet(count);
        int[] limit = {layout.depth(), layout.height(), layout.width()};
        int[] cursor = new int[6];
        long[] steps = {layout.positionStep(0), layout.positionStep(1), layout.positionStep(2)};
        long controller = layout.position(layout.controllerX(), layout.controllerY(), layout.controllerZ());
        for (int i = 0; i < count; i++) {
            checkCancelled(i);
            long cell = layout.cell(i), coordinate = layout.position(i);
            int state = Hk3W01HallLayout.state(cell);
            boolean visible = !opaqueStates[state] || blockEntityStates[state] || coordinate == controller;
            for (int face = 0; face < 6 && !visible; face++) {
                int axis = face / 2, shift = axis * 12, step = (face & 1) == 0 ? -1 : 1;
                long adjacent = ((cell >>> (16 + shift)) & 4095) + step;
                if (adjacent < 0 || adjacent >= limit[axis]) { visible = true; break; }
                long target = coordinate + step * steps[axis];
                int next = cursor[face];
                while (next < count && layout.position(next) < target) next++;
                cursor[face] = next;
                if (next == count) { visible = true; break; }
                visible = layout.position(next) != target || !opaqueStates[layout.state(next)];
            }
            if (visible) exposed.set(i);
        }
        return exposed;
    }

    private static void checkCancelled(int i) {
        if ((i & 4095) == 0 && Thread.currentThread().isInterrupted()) throw new CancellationException();
    }

    public int stateAt(int x, int y, int z) {
        if (x < 0 || y < 0 || z < 0 || x >= layout.width() || y >= layout.height() || z >= layout.depth()) return -1;
        long key = layout.position(x, y, z);
        int column = x * layout.height() + y;
        int low = columns[column], high = columns[column + 1] - 1;
        while (low <= high) {
            int middle = (low + high) >>> 1;
            long candidate = layout.position(middle);
            if (candidate < key) low = middle + 1;
            else if (candidate > key) high = middle - 1;
            else return layout.state(middle);
        }
        return -1;
    }

    public int countLayer(int layer) { return layer < 0 ? layout.count() : layers[layer]; }
    public int countMaterial(int state) { return materials[state]; }
    public long firstCell(int state) { return firstCells[state]; }
    public long[] blockEntityCells() { return blockEntityCells; }
    public int nextVisibleCell(int from) { return renderCells.nextSetBit(from); }
    public int renderCount() { return renderCount; }
    public long byteSize() {
        return 4L * (columns.length + layers.length + materials.length) + renderCells.size() / 8L
                + 8L * (firstCells.length + blockEntityCells.length);
    }
}
