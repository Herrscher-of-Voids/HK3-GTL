package com.sirin.hk3gtl.common.multiblock.pattern;

/**
 * 【文件职责】共享W01有序实体布局，提供无空气数组的坐标查询与逐层、逐状态计数。
 * 【变更记录 #1】2026-10-29 23:12:35（第1次备注 · 本轮高度与预览修复）
 * 删除：无；新增：二分坐标索引、材料和高度统计；修改：无。
 * 用途：游戏内完整预览仅共享原实体long[]，不为约两亿格包围盒分配引用。
 */
/** 【变更记录 #2】2026-10-29 23:18:13（第2次备注 · 本轮高度与预览修复）：删除无；新增每状态首个真实格坐标；修改材料取样共用索引；用途为只读预览世界中按原坐标取材，避免查询玩家当前世界的零坐标。 */
public final class Hk3W01PreviewIndex {
    private final Hk3W01HallLayout layout;
    private final int[] layers;
    private final int[] materials;
    private final long[] firstCells;

    public Hk3W01PreviewIndex(Hk3W01HallLayout layout) {
        this.layout = layout;
        layers = new int[layout.height()];
        materials = new int[layout.palette().size()];
        firstCells = new long[materials.length];
        for (long cell : layout.cells()) {
            layers[Hk3W01HallLayout.y(cell)]++;
            int state = Hk3W01HallLayout.state(cell);
            if (materials[state]++ == 0) firstCells[state] = cell;
        }
    }

    public int stateAt(int x, int y, int z) {
        if (x < 0 || y < 0 || z < 0 || x >= layout.width() || y >= layout.height() || z >= layout.depth()) return -1;
        long key = Hk3W01HallLayout.pack(x,y,z,0)>>>16;
        long[] cells = layout.cells();
        int low = 0, high = cells.length - 1;
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
}
