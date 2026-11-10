package com.sirin.hk3gtl.common.easter;

import com.google.gson.JsonParser;
import com.mojang.logging.LogUtils;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.minecraftforge.event.AddReloadListenerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.io.*;
import java.time.*;
import java.util.*;

/**
 * 【文件职责】读取有来源的逐年农历节日公历日期；只提供日期事实，不模拟农历或授予进度。
 * 【变更记录 #1】2026-11-05 21:56:28（修订211）
 * 删除：无。新增：六节日年度库、不可变快照及数据包重载；修改：无。
 * 用途：370/371/373至376沿用服务器时区；缺年、缺库、损坏或民用日区间不同则休眠，拒绝旧缓存。
 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3LunarCalendar {
    private static final ResourceLocation RESOURCE = new ResourceLocation("hk3gtl", "calendar/lunar_festivals.json");
    public static final List<String> FESTIVALS = List.of("spring_festival", "lantern_festival", "dragon_boat",
            "qixi", "mid_autumn", "double_ninth");
    private static volatile Library library = new Library(ZoneId.of("Asia/Hong_Kong"), Map.of());
    private Hk3LunarCalendar() {}

    public record Library(ZoneId sourceZone, Map<Integer, Map<String,LocalDate>> years) {
        public Library {
            var copy = new LinkedHashMap<Integer,Map<String,LocalDate>>();
            years.forEach((year, dates) -> copy.put(year, Map.copyOf(dates)));
            years = Map.copyOf(copy);
        }
        public Map<String,String> facts(LocalDate date, ZoneId serverZone) {
            var dates = years.get(date.getYear());
            if (dates == null || !Hk3SolarCalendar.sameCivilDay(date, sourceZone, serverZone)) return Map.of();
            for (var entry : dates.entrySet()) if (date.equals(entry.getValue()))
                return Map.of("lunar_festival", entry.getKey());
            return Map.of();
        }
    }

    public static Library parse(Reader reader) {
        var root = JsonParser.parseReader(reader).getAsJsonObject();
        if (root.get("schema").getAsInt() != 1 || root.get("source").getAsString().isBlank())
            throw new IllegalArgumentException("农历节日日历缺少格式或来源");
        var zone = ZoneId.of(root.get("sourceZone").getAsString());
        var entries = root.getAsJsonObject("years");
        if (entries.size() > 512) throw new IllegalArgumentException("农历节日日历年度数量超限");
        var years = new LinkedHashMap<Integer,Map<String,LocalDate>>();
        for (var entry : entries.entrySet()) {
            int year = Integer.parseInt(entry.getKey());
            var row = entry.getValue().getAsJsonObject();
            if (year < 1 || year > 9999 || !row.keySet().equals(Set.copyOf(FESTIVALS)))
                throw new IllegalArgumentException("农历节日日历年份或六节日字段无效");
            var dates = new LinkedHashMap<String,LocalDate>();
            LocalDate previous = null;
            for (String festival : FESTIVALS) {
                var date = LocalDate.parse(row.get(festival).getAsString());
                if (date.getYear() != year || (previous != null && !date.isAfter(previous)))
                    throw new IllegalArgumentException("农历节日日历日期跨年、重复或倒序");
                dates.put(festival,date);
                previous = date;
            }
            if (years.putIfAbsent(year, dates) != null) throw new IllegalArgumentException("农历节日日历重复年份");
        }
        return new Library(zone, years);
    }

    public static Map<String,String> facts(LocalDate date, ZoneId serverZone) { return library.facts(date, serverZone); }

    @SubscribeEvent public static void listeners(AddReloadListenerEvent event) {
        event.addListener((ResourceManagerReloadListener) Hk3LunarCalendar::reload);
    }

    private static void reload(ResourceManager manager) {
        Library next = new Library(ZoneId.of("Asia/Hong_Kong"), Map.of());
        try {
            var resource = manager.getResource(RESOURCE);
            if (resource.isPresent()) try (var reader = resource.get().openAsReader()) { next = parse(reader); }
        } catch (IOException | RuntimeException invalid) {
            LogUtils.getLogger().warn("[HK3GTL] 农历节日日历不可用，相关六条彩蛋保持休眠，不沿用旧缓存。", invalid);
        }
        library = next;
    }
}
