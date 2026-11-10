package com.sirin.hk3gtl.common.multiblock.pattern;

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;
import java.io.IOException;
import java.io.Reader;
import java.util.*;

/**
 * 【变更记录 #1】2026-09-27 23:52:00（内测5修订91）
 * 删除：无。新增：逐项解析建筑JSON，用长整数坐标及调色板保存非空气方块。
 * 修改：避免常驻逐格对象、三元数组和重复状态文本；遍历时才生成兼容视图。
 * 用途：降低大型建筑加载与缓存占用，保持原顺序、全部状态、主控和端口；非法资源拒绝加载。
 */
public final class Hk3PackedArchitectureReader {
    private static final int BITS = 21, MASK = (1 << BITS) - 1;
    private static final Gson GSON = new Gson();
    private Hk3PackedArchitectureReader() {}

    public static Hk3ApprovedArchitecture.Layout readCompact(java.io.InputStream input, Reader metadata, String key) throws IOException {
        var json=com.google.gson.JsonParser.parseReader(metadata).getAsJsonObject();
        if(!key.equals(json.get("key").getAsString()))throw invalid("紧凑建筑身份不符");
        try(var stream=new Hk3StructureStream(input)) {
            var h=stream.header();int[] size={h.width(),h.height(),h.depth()},center={h.cx(),h.cy(),h.cz()};
            if(!Arrays.equals(size,GSON.fromJson(json.get("size"),int[].class))
                    ||!Arrays.equals(center,GSON.fromJson(json.get("controller"),int[].class)))throw invalid("紧凑元数据坐标不符");
            long[] positions=new long[h.count()];char[] states=new char[h.count()];
            List<String> palette=new ArrayList<>(h.palette());Map<String,Integer> paletteIndices=new HashMap<>();
            for(int i=0;i<palette.size();i++)paletteIndices.put(palette.get(i),i);
            var overrides=json.getAsJsonObject("layout_state_overrides");
            var overrideIndices=new it.unimi.dsi.fastutil.ints.Int2IntOpenHashMap();overrideIndices.defaultReturnValue(-1);
            if(overrides!=null)for(var entry:overrides.entrySet()) {
                int linear=Integer.parseInt(entry.getKey());if(linear<0||linear>=h.volume())throw invalid("接口修正越界");
                String text=entry.getValue().getAsString();if(text.isBlank())throw invalid("空状态修正");
                Integer state=paletteIndices.get(text);
                if(state==null){state=palette.size();if(state>65535)throw invalid("调色板过大");palette.add(text);paletteIndices.put(text,state);}
                overrideIndices.put(linear,state.intValue());
            }
            BitSet occupied=new BitSet(h.volume());
            for(int i=0;i<h.count();i++) {
                var cell=stream.next();int p=cell.linear();
                if(occupied.get(p))throw invalid("重复坐标");occupied.set(p);
                positions[i]=pack(new int[]{p/h.depth()/h.height(),p/h.depth()%h.height(),p%h.depth()});
                int override=overrideIndices.get(p);states[i]=(char)(override<0?cell.state():override);
            }
            stream.finish();
            var ports=Arrays.asList(GSON.fromJson(json.get("ports"),Hk3ApprovedArchitecture.Port[].class));
            Set<String> ids=new HashSet<>();Set<Long> used=new HashSet<>();
            for(var port:ports){validate(port.pos(),size);if(port.id()==null||port.id().isBlank()||!ids.add(port.id())||!used.add(pack(port.pos())))throw invalid("端口重复或无效");}
            return new Hk3ApprovedArchitecture.Layout(key,size,center,
                    new PackedCells(positions,states,palette.toArray(String[]::new)),ports);
        }
    }

    public static Hk3ApprovedArchitecture.Layout read(Reader input, String expectedKey) throws IOException {
        JsonReader reader = new JsonReader(input);
        String key = null;
        int[] size = null, controller = null;
        PackedCells cells = null;
        List<Hk3ApprovedArchitecture.Port> ports = null;
        Set<String> fields = new HashSet<>();
        reader.beginObject();
        while (reader.hasNext()) {
            String field = reader.nextName();
            if (!fields.add(field)) throw invalid("重复字段：" + field);
            switch (field) {
                case "key" -> key = reader.nextString();
                case "size" -> size = triple(reader);
                case "controller" -> controller = triple(reader);
                case "blocks" -> cells = blocks(reader);
                case "ports" -> {
                    ports = new ArrayList<>();
                    reader.beginArray();
                    while (reader.hasNext()) ports.add(GSON.fromJson(reader, Hk3ApprovedArchitecture.Port.class));
                    reader.endArray();
                }
                default -> reader.skipValue();
            }
        }
        reader.endObject();
        if (reader.peek() != com.google.gson.stream.JsonToken.END_DOCUMENT) throw invalid("尾随数据");
        if (!expectedKey.equals(key) || size == null || controller == null || cells == null || ports == null)
            throw invalid("建筑元数据不完整：" + expectedKey);
        for (int value : size) if (value <= 0 || value > MASK) throw invalid("尺寸越界");
        validate(controller, size);
        // 原始顺序保留；排序副本用于重复检测，不创建逐格字符串和哈希节点。
        long[] sorted = cells.positions.clone();
        Arrays.sort(sorted);
        for (int i = 0; i < sorted.length; i++) {
            if (i > 0 && sorted[i] == sorted[i - 1]) throw invalid("重复坐标");
            validate(unpack(sorted[i]), size);
        }
        Set<String> portIds = new HashSet<>();
        Set<Long> portPositions = new HashSet<>();
        for (var port : ports) {
            if (port == null || port.id() == null || port.id().isBlank() || !portIds.add(port.id())) throw invalid("端口标识错误");
            validate(port.pos(), size);
            if (!portPositions.add(pack(port.pos()))) throw invalid("端口坐标重复");
        }
        return new Hk3ApprovedArchitecture.Layout(key, size, controller, cells, List.copyOf(ports));
    }

    private static PackedCells blocks(JsonReader reader) throws IOException {
        long[] positions = new long[1024];
        char[] states = new char[1024];
        Map<String, Integer> palette = new LinkedHashMap<>();
        int count = 0;
        reader.beginArray();
        while (reader.hasNext()) {
            int[] pos = null;
            String state = null;
            reader.beginObject();
            while (reader.hasNext()) {
                switch (reader.nextName()) {
                    case "pos" -> { if (pos != null) throw invalid("重复坐标字段"); pos = triple(reader); }
                    case "state" -> { if (state != null) throw invalid("重复状态字段"); state = reader.nextString(); }
                    default -> reader.skipValue();
                }
            }
            reader.endObject();
            if (pos == null || state == null || state.isBlank()) throw invalid("方块数据缺失");
            Integer index = palette.get(state);
            if (index == null) {
                index = palette.size();
                if (index > Character.MAX_VALUE) throw invalid("调色板超过65536项");
                palette.put(state, index);
            }
            if (count == positions.length) {
                int capacity = Math.addExact(count, Math.max(1024, count / 2));
                positions = Arrays.copyOf(positions, capacity);
                states = Arrays.copyOf(states, capacity);
            }
            positions[count] = pack(pos);
            states[count++] = (char) index.intValue();
        }
        reader.endArray();
        return new PackedCells(Arrays.copyOf(positions, count), Arrays.copyOf(states, count), palette.keySet().toArray(String[]::new));
    }

    private static int[] triple(JsonReader reader) throws IOException {
        int[] values = new int[3];
        reader.beginArray();
        for (int i = 0; i < 3; i++) values[i] = reader.nextInt();
        if (reader.hasNext()) throw invalid("坐标维数错误");
        reader.endArray();
        return values;
    }

    private static long pack(int[] p) {
        for (int value : p) if (value < 0 || value > MASK) throw invalid("坐标越界");
        return ((long) p[0] << (BITS * 2)) | ((long) p[1] << BITS) | p[2];
    }
    private static int[] unpack(long p) { return new int[]{(int) (p >>> (BITS * 2)), (int) (p >>> BITS) & MASK, (int) p & MASK}; }
    private static void validate(int[] p, int[] size) {
        if (p == null || p.length != 3) throw invalid("坐标维数错误");
        for (int i = 0; i < 3; i++) if (p[i] < 0 || p[i] >= size[i]) throw invalid("坐标越界");
    }
    private static IllegalStateException invalid(String message) { return new IllegalStateException("正式建筑数据错误：" + message); }

    public static long estimatedBytes(Hk3ApprovedArchitecture.Layout layout) {
        PackedCells cells = (PackedCells) layout.blocks();
        long bytes = 1024L + cells.positions.length * 10L + layout.ports().size() * 512L;
        for (String state : cells.palette) bytes += 64L + state.length() * 2L;
        return bytes;
    }

    private static final class PackedCells extends AbstractList<Hk3ApprovedArchitecture.Cell> implements RandomAccess {
        private final long[] positions;
        private final char[] states;
        private final String[] palette;
        private PackedCells(long[] positions, char[] states, String[] palette) {
            this.positions = positions; this.states = states; this.palette = palette;
        }
        @Override public int size() { return positions.length; }
        @Override public Hk3ApprovedArchitecture.Cell get(int index) {
            Objects.checkIndex(index, positions.length);
            return new Hk3ApprovedArchitecture.Cell(unpack(positions[index]), palette[states[index]]);
        }
    }
}
