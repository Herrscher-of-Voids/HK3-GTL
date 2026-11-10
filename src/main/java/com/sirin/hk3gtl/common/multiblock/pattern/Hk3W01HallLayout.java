package com.sirin.hk3gtl.common.multiblock.pattern;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.GZIPInputStream;

/** W01全实体紧凑布局；保持Azu原坐标和全部状态，不展开约两亿空气格。2026-10-29。 */
public record Hk3W01HallLayout(int width, int height, int depth, int controllerX, int controllerY,
                             int controllerZ, List<String> palette, long[] cells) {
    public static Hk3W01HallLayout load() {
        try (var stream = Hk3W01HallLayout.class.getResourceAsStream("/data/hk3gtl/structures/w01_hall.bin.gz")) {
            if (stream == null) throw new IOException("W01完整礼堂资源缺失");
            return read(stream);
        } catch (IOException failure) {
            throw new IllegalStateException("读取W01完整礼堂失败", failure);
        }
    }

    public static Hk3W01HallLayout read(InputStream compressed) throws IOException {
        try (var input = new DataInputStream(new GZIPInputStream(compressed))) {
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
