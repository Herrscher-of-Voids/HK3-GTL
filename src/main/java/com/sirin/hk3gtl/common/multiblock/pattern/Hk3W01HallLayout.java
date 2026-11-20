package com.sirin.hk3gtl.common.multiblock.pattern;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import com.sirin.hk3gtl.common.util.Hk3PackedResources;

/** W01全实体紧凑布局；保持Azu原坐标和全部状态，不展开约两亿空气格。。 */
public record Hk3W01HallLayout(int width, int height, int depth, int controllerX, int controllerY,
                             int controllerZ, List<String> palette, Cells storage) {
    public Hk3W01HallLayout(int width, int height, int depth, int x, int y, int z, List<String> palette, long[] cells) {
        this(width, height, depth, x, y, z, palette, new Cells(cells));
    }
    public int count() { return storage.count(); }
    public long cell(int index) { return storage.cell(index, height, depth); }
    long position(int index) { return storage.packed == null ? storage.linear[index] : storage.packed[index] >>> 16; }
    long position(int x, int y, int z) {
        return storage.packed == null ? (x * height + y) * depth + z : pack(x, y, z, 0) >>> 16;
    }
    long positionStep(int axis) {
        if (storage.packed != null) return 1L << (12 * axis);
        return axis == 0 ? 1 : axis == 1 ? depth : height * depth;
    }
    int state(int index) { return storage.packed == null ? storage.state(index) : state(storage.packed[index]); }
    public long bytes() { return storage.bytes(); }
    public long[] cells() {
        if (storage.packed != null) return storage.packed;
        long[] copy = new long[count()];
        for (int i = 0; i < copy.length; i++) copy[i] = cell(i);
        return copy;
    }

    static final class Cells {
        private final long[] packed;
        private final int[] linear;
        private final byte[] state8;
        private final char[] state16;

        Cells(long[] packed) { this.packed = packed; linear = null; state8 = null; state16 = null; }
        Cells(int count, int paletteSize) {
            packed = null;
            linear = new int[count];
            state8 = paletteSize <= 256 ? new byte[count] : null;
            state16 = state8 == null ? new char[count] : null;
        }
        private int count() { return packed == null ? linear.length : packed.length; }
        private long bytes() { return packed == null ? (state8 == null ? 6L : 5L) * linear.length : 8L * packed.length; }
        private long cell(int index, int height, int depth) {
            if (packed != null) return packed[index];
            int pos = linear[index], column = pos / depth, x = column / height;
            return ((long) x << 40) | ((long) (column - x * height) << 28)
                    | ((long) (pos - column * depth) << 16) | state(index);
        }
        int position(int i) { return linear[i]; }
        private int state(int i) { return state8 == null ? state16[i] : Byte.toUnsignedInt(state8[i]); }
        void set(int i, int position, int state) {
            linear[i] = position;
            if (state8 == null) state16[i] = (char) state;
            else state8[i] = (byte) state;
        }
        void sort() {
            it.unimi.dsi.fastutil.Arrays.quickSort(0, linear.length, (a, b) -> Integer.compare(linear[a], linear[b]), (a, b) -> {
                int pos = linear[a], state = state(a);
                set(a, linear[b], state(b));
                set(b, pos, state);
            });
        }
    }

    public static Hk3W01HallLayout load() {
        try (var stream = Hk3W01HallLayout.class.getResourceAsStream("/data/hk3gtl/structures/w01_hall.bin.gz")) {
            if (stream == null) throw new IOException("W01完整礼堂资源缺失");
            return read(stream);
        } catch (IOException failure) {
            throw new IllegalStateException("读取W01完整礼堂失败", failure);
        }
    }

    public static Hk3W01HallLayout read(InputStream compressed) throws IOException {
        try (var input = new DataInputStream(Hk3PackedResources.open(compressed))) {
            if (input.readInt() != 0x57303141 || input.readInt() != 1) throw new IOException("W01资源格式错误");
            int w = input.readInt(), h = input.readInt(), d = input.readInt();
            int cx = input.readInt(), cy = input.readInt(), cz = input.readInt(), count = input.readInt();
            if (w < 1 || h < 1 || d < 1 || w > 1024 || h > 1024 || d > 1024 || count < 1
                    || count > (long) w * h * d || cx < 0 || cy < 0 || cz < 0 || cx >= w || cy >= h || cz >= d)
                throw new IOException("W01尺寸或主控越界");
            int materials = input.readUnsignedShort();
            if (materials == 0) throw new IOException("W01调色板为空");
            var palette = new ArrayList<String>(materials);
            for (int i = 0; i < materials; i++) palette.add(input.readUTF());
            long[] cells = new long[count];
            long previous = -1;
            boolean controller = false;
            for (int i = 0; i < count; i++) {
                long legacy = input.readLong();
                int lx=(int)(legacy>>>36),ly=(int)(legacy>>>26)&1023,lz=(int)(legacy>>>16)&1023;
                if(legacy<0||lx>=w||ly>=h||lz>=d)throw new IOException("W01方块坐标越界");
                long cell = pack(lx,ly,lz,(int)legacy&65535);
                long coordinate = cell >>> 16;
                int x = x(cell), y = y(cell), z = z(cell);
                if (cell < 0 || coordinate <= previous || x >= w || y >= h || z >= d || state(cell) >= materials)
                    throw new IOException("W01方块坐标重复、越界或调色板错误");
                previous = coordinate;
                controller |= x == cx && y == cy && z == cz;
                cells[i] = cell;
            }
            if (!controller || input.read() != -1) throw new IOException("W01主控缺格或尾随数据");
            return new Hk3W01HallLayout(w, h, d, cx, cy, cz, List.copyOf(palette), cells);
        }
    }

    /** 运行时每轴12位；原W01磁盘十位格式只在读取时转换，不改源文件。 */
    public static long pack(int x,int y,int z,int state) {
        if(x<0||x>4095||y<0||y>4095||z<0||z>4095||state<0||state>65535)
            throw new IllegalArgumentException("稀疏预览坐标或材料越界");
        return ((long)x<<40)|((long)y<<28)|((long)z<<16)|state;
    }
    public static int x(long cell) { return (int) (cell >>> 40); }
    public static int y(long cell) { return (int) (cell >>> 28) & 4095; }
    public static int z(long cell) { return (int) (cell >>> 16) & 4095; }
    public static int state(long cell) { return (int) cell & 65535; }
}
