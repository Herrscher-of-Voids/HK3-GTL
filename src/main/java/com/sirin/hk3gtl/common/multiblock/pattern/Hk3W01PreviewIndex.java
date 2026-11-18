package com.sirin.hk3gtl.common.multiblock.pattern;

 





 
public final class Hk3W01PreviewIndex {
    private final Hk3W01HallLayout layout;
    private final int[] layers;
    private final int[] materials;
    private final long[] firstCells;
    private final int[] columns;
    private final long[] blockEntityCells;
    private final int[] renderCells;

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
        for (long cell : layout.cells()) {
            layers[Hk3W01HallLayout.y(cell)]++;
            columns[Hk3W01HallLayout.x(cell) * layout.height() + Hk3W01HallLayout.y(cell) + 1]++;
            int state = Hk3W01HallLayout.state(cell);
            if (materials[state]++ == 0) firstCells[state] = cell;
            if (blockEntityStates[state]) entities.add(cell);
        }
        for (int i = 1; i < columns.length; i++) columns[i] += columns[i - 1];
        blockEntityCells = entities.toLongArray();
        renderCells = surfaceCells(blockEntityStates, opaqueStates);
    }

    private int[] surfaceCells(boolean[] blockEntityStates, boolean[] opaqueStates) {
        long[] cells = layout.cells();
        byte[] hiddenFaces = new byte[cells.length];
        int[] limits = {layout.depth(), layout.height(), layout.width()};
        // 正向邻居单调归并，同时登记一对方块各自的反向遮挡。
        for (int axis = 0; axis < 3; axis++) {
            int shift = axis * 12, next = 0;
            long step = 1L << shift;
            for (int i = 0; i < cells.length; i++) {
                long coordinate = cells[i] >>> 16;
                if (((coordinate >>> shift) & 4095) == limits[axis] - 1) continue;
                long neighbor = coordinate + step;
                while (next < cells.length && (cells[next] >>> 16) < neighbor) next++;
                if (next == cells.length) break;
                if ((cells[next] >>> 16) != neighbor) continue;
                if (opaqueStates[Hk3W01HallLayout.state(cells[next])]) hiddenFaces[i] |= 1 << (axis * 2);
                if (opaqueStates[Hk3W01HallLayout.state(cells[i])]) hiddenFaces[next] |= 1 << (axis * 2 + 1);
            }
        }
        long controller = Hk3W01HallLayout.pack(layout.controllerX(), layout.controllerY(), layout.controllerZ(), 0) >>> 16;
        int count = 0;
        for (int i = 0; i < cells.length; i++) {
            int state = Hk3W01HallLayout.state(cells[i]);
            if (!opaqueStates[state] || blockEntityStates[state] || (cells[i] >>> 16) == controller) hiddenFaces[i] = 0;
            if (hiddenFaces[i] != 63) count++;
        }
        int[] visible = new int[count];
        for (int i = 0, next = 0; i < cells.length; i++) if (hiddenFaces[i] != 63) visible[next++] = i;
        return visible;
    }

    public int stateAt(int x, int y, int z) {
        if (x < 0 || y < 0 || z < 0 || x >= layout.width() || y >= layout.height() || z >= layout.depth()) return -1;
        long key = Hk3W01HallLayout.pack(x,y,z,0)>>>16;
        long[] cells = layout.cells();
        int column = x * layout.height() + y;
        int low = columns[column], high = columns[column + 1] - 1;
        while (low <= high) {
            int middle = (low + high) >>> 1;
            long candidate = cells[middle] >>> 16;
            if (candidate < key) low = middle + 1;
            else if (candidate > key) high = middle - 1;
            else return Hk3W01HallLayout.state(cells[middle]);
        }
        return -1;
    }

    public int countLayer(int layer) { return layer < 0 ? layout.cells().length : layers[layer]; }
    public int countMaterial(int state) { return materials[state]; }
    public long firstCell(int state) { return firstCells[state]; }
    public long[] blockEntityCells() { return blockEntityCells; }
    public int[] renderCells() { return renderCells; }
    public long byteSize() { return 4L * (columns.length + layers.length + materials.length + renderCells.length) + 8L * (firstCells.length + blockEntityCells.length); }
}
