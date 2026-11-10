package com.sirin.hk3gtl.test.industry;

import com.google.gson.*;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3PackedArchitectureReader;
import com.sirin.hk3gtl.common.util.Hk3WeightedCache;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 【变更记录 #1】2026-09-27 23:52:00（内测5修订91）
 * 删除：无。新增：生产资源逐格对照、非法数据、隔离修改、缓存淘汰和并发回归。
 * 修改：独立小堆压力入口生成704710格临时数据，可对照旧Gson对象布局。
 * 用途：证明数据未丢失并测量纯布局内存边界；不代替GT预览、世界运行或手机实测。
 */
public final class PackedArchitectureTest {
    // 2026-10-30：独立流式对照全部批准布局，避免测试额外展开千万级Gson对象树。
    private record LegacyCell(int[] pos, String state) {}
    private record LegacyLayout(List<LegacyCell> blocks) {}
    public static void main(String[] args) throws Exception {
        if (args.length > 0) { stress(args[0]); return; }
        long count = 0, bytes = 0;
        for (String id : Hk3ApprovedArchitecture.IDS) {
            var data = Hk3ApprovedArchitecture.get(id);
            try (var input = new InputStreamReader(Objects.requireNonNull(PackedArchitectureTest.class.getResourceAsStream(
                    "/data/hk3gtl/approved_architecture/" + id + ".json")), StandardCharsets.UTF_8)) {
                count += compare(input, data); bytes += Hk3PackedArchitectureReader.estimatedBytes(data);
                int old = data.blocks().get(0).pos()[0]; data.blocks().get(0).pos()[0] = -100;
                check(data.blocks().get(0).pos()[0] == old, "修改污染缓存");
                data.size()[0] = -1; check(data.size()[0] > 0, "尺寸污染缓存");
                try { data.blocks().clear(); throw new AssertionError("集合可修改"); } catch (UnsupportedOperationException expected) {}
                System.out.println(id + "逐格对照通过：" + data.blocks().size());
            }
        }
        String header = "{\"key\":\"test\",\"size\":[4,4,4],\"controller\":[0,0,0],\"ports\":[],\"blocks\":";
        for (String blocks : List.of("[{\"pos\":[0,0,0],\"state\":\"minecraft:stone\"},{\"pos\":[0,0,0],\"state\":\"minecraft:stone\"}]",
                "[{\"pos\":[4,0,0],\"state\":\"minecraft:stone\"}]", "[{\"pos\":[-1,0,0],\"state\":\"minecraft:stone\"}]",
                "[{\"pos\":[0,0,0]}]")) {
            try { Hk3PackedArchitectureReader.read(new StringReader(header + blocks + "}"), "test"); throw new AssertionError("错误资源未拦截"); }
            catch (IllegalStateException expected) {}
        }
        var port = Hk3PackedArchitectureReader.read(new StringReader(header
                + "[{\"pos\":[0,0,0],\"state\":\"hk3gtl:industrial_port_casing\"}]}"), "test");
        check(port.blocks().get(0).state().equals("hk3gtl:industrial_port_casing"), "现行接口机壳被拒绝");
        for (String blocks : List.of("[]", "[{\"pos\":[1,0,0],\"state\":\"hk3gtl:industrial_port_casing\"}]",
                "[{\"pos\":[0,0,0],\"state\":\"minecraft:stone\"}]", "[{\"pos\":[0,0,0]}]")) {
            boolean rejected = false;
            try { compare(new StringReader(header + blocks + "}"), port); }
            catch (AssertionError expected) { rejected = true; }
            check(rejected, "独立对照未拦截数量、坐标、状态或字段差异");
        }
        cache();
        System.out.println("逐格对照通过：" + count + "；紧凑布局估算常驻字节：" + bytes + "；损坏资源与缓存回归通过");
    }
    private static int compare(Reader input, Hk3ApprovedArchitecture.Layout data) throws IOException {
        JsonReader reader = new JsonReader(input);
        int count = 0;
        boolean found = false;
        reader.beginObject();
        while (reader.hasNext()) {
            if (!reader.nextName().equals("blocks")) { reader.skipValue(); continue; }
            check(!found, "重复方块数组"); found = true;
            reader.beginArray();
            while (reader.hasNext()) {
                check(count < data.blocks().size(), "源方块数量过多：" + data.key());
                var actual = data.blocks().get(count);
                int[] pos = actual.pos();
                boolean positionSeen = false, stateSeen = false;
                reader.beginObject();
                while (reader.hasNext()) {
                    switch (reader.nextName()) {
                        case "pos" -> {
                            check(!positionSeen, "重复坐标字段"); positionSeen = true;
                            reader.beginArray();
                            for (int axis = 0; axis < 3; axis++) {
                                check(reader.hasNext(), "坐标维度不足");
                                check(reader.nextInt() == pos[axis], "坐标顺序不同：" + data.key() + "/" + count);
                            }
                            check(!reader.hasNext(), "坐标维度过多"); reader.endArray();
                        }
                        case "state" -> {
                            check(!stateSeen, "重复状态字段"); stateSeen = true;
                            check(reader.nextString().equals(actual.state()), "状态不同：" + data.key() + "/" + count);
                        }
                        default -> reader.skipValue();
                    }
                }
                reader.endObject();
                check(positionSeen && stateSeen, "方块坐标或状态字段缺失");
                count++;
            }
            reader.endArray();
        }
        reader.endObject();
        check(found && count == data.blocks().size(), "源方块数量不同：" + data.key());
        check(reader.peek() == JsonToken.END_DOCUMENT, "对照源含尾随数据");
        return count;
    }
    private static void cache() throws Exception {
        var cache = new Hk3WeightedCache<String, String>(6, String::length);
        cache.get("a", k -> "aaa"); cache.get("b", k -> "bbb"); cache.get("a", k -> { throw new AssertionError(); });
        cache.get("c", k -> "ccc");
        check(cache.get("b", k -> "new").equals("new"), "未淘汰最旧项");
        check(cache.retainedBytes() == 6, "缓存超额");
        cache.get("large", k -> "1234567"); check(cache.retainedBytes() == 6, "超大项被缓存");
        try { cache.get("error", k -> { throw new IllegalStateException(); }); } catch (IllegalStateException expected) {}
        check(cache.size() == 2, "异常污染缓存"); cache.clear(); check(cache.retainedBytes() == 0, "释放失败");
        AtomicInteger loads = new AtomicInteger(); ExecutorService pool = Executors.newFixedThreadPool(4);
        try {
            List<Future<String>> futures = new ArrayList<>();
            for (int i = 0; i < 16; i++) futures.add(pool.submit(() -> cache.get("x", k -> { loads.incrementAndGet(); return "xx"; })));
            for (var future : futures) check(future.get().equals("xx"), "并发值错误");
            check(loads.get() == 1, "并发重复加载");
        } finally { pool.shutdownNow(); }
    }
    private static void stress(String mode) throws Exception {
        Path file = Files.createTempFile("hk3-layout-stress-", ".json");
        final int count = 704710;
        try {
            try (var out = Files.newBufferedWriter(file, StandardCharsets.UTF_8)) {
                out.write("{\"key\":\"stress\",\"size\":[256,16,256],\"controller\":[0,0,0],\"ports\":[],\"blocks\":[");
                for (int i = 0; i < count; i++) {
                    if (i > 0) out.write(',');
                    out.write("{\"pos\":[" + (i % 256) + "," + ((i / 256) % 16) + "," + (i / 4096) + "],\"state\":\"minecraft:stone\"}");
                }
                out.write("]}");
            }
            try (var input = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                if (mode.equals("legacy")) {
                    var layout = new Gson().fromJson(input, LegacyLayout.class);
                    check(layout.blocks().size() == count, "旧布局数量");
                } else {
                    var layout = Hk3PackedArchitectureReader.read(input, "stress");
                    check(layout.blocks().size() == count, "紧凑布局数量");
                    for (int i = 0; i < count; i++) {
                        var cell = layout.blocks().get(i); int[] p = cell.pos();
                        check(p[0] == i % 256 && p[1] == (i / 256) % 16 && p[2] == i / 4096, "大结构坐标丢失");
                    }
                    try (var original = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                        check(compare(original, layout) == count, "小堆流式逐格对照数量");
                    }
                    System.out.println("紧凑布局估算字节=" + Hk3PackedArchitectureReader.estimatedBytes(layout));
                }
                System.out.println("布局压力验证通过，模式=" + mode + "，方块=" + count + "，最大堆=" + Runtime.getRuntime().maxMemory());
            }
        } finally { Files.deleteIfExists(file); }
    }
    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
}
