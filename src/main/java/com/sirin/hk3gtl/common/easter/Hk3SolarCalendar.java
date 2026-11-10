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
 * 【文件职责】从服务端数据包读取有来源的逐年节气民用日期，运行时不联网或推算。
 * 【变更记录 #1】2026-11-05 19:08:32（修订210）
 * 删除：无。新增：年度日历解析、重载及缺来源休眠；修改：无。
 * 用途：372/377只使用配置日历；时区日期区间不相容、年份缺失或资源损坏时不触发。
 */
/** 【变更记录 #2】2026-11-05 21:56:28（修订211）：删除无；新增同包农历库复用民用日区间校验；修改仅将校验方法开放给同包；用途：两类日历沿用同一时区边界，原节气结果不变。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3SolarCalendar {
    private static final ResourceLocation RESOURCE = new ResourceLocation("hk3gtl", "calendar/solar_terms.json");
    private static volatile Library library = new Library(ZoneId.of("Asia/Hong_Kong"), Map.of());
    private Hk3SolarCalendar() {}

    public record Terms(LocalDate qingming, LocalDate winterSolstice) {}
    public record Library(ZoneId sourceZone, Map<Integer, Terms> years) {
        public Library { years = Map.copyOf(years); }
        public Map<String,String> facts(LocalDate date, ZoneId serverZone) {
            var terms = years.get(date.getYear());
            if (terms == null || !sameCivilDay(date, sourceZone, serverZone)) return Map.of();
            return Map.of("qingming", Boolean.toString(date.equals(terms.qingming())),
                    "winter_solstice", Boolean.toString(date.equals(terms.winterSolstice())));
        }
    }

    // 数据源只提供香港民用日期，不把它冒充其他时区的天文交节时刻。
    static boolean sameCivilDay(LocalDate date, ZoneId source, ZoneId server) {
        return date.atStartOfDay(source).toInstant().equals(date.atStartOfDay(server).toInstant())
                && date.plusDays(1).atStartOfDay(source).toInstant().equals(date.plusDays(1).atStartOfDay(server).toInstant());
    }

    public static Library parse(Reader reader) {
        var root = JsonParser.parseReader(reader).getAsJsonObject();
        if (root.get("schema").getAsInt() != 1 || root.get("source").getAsString().isBlank())
            throw new IllegalArgumentException("节气日历缺少格式或来源");
        var zone = ZoneId.of(root.get("sourceZone").getAsString());
        var entries = root.getAsJsonObject("years");
        if (entries.size() > 512) throw new IllegalArgumentException("节气日历年度数量超限");
        var years = new LinkedHashMap<Integer, Terms>();
        for (var entry : entries.entrySet()) {
            int year = Integer.parseInt(entry.getKey());
            var row = entry.getValue().getAsJsonObject();
            var qingming = LocalDate.parse(row.get("qingming").getAsString());
            var winter = LocalDate.parse(row.get("winter_solstice").getAsString());
            if (year < 1 || year > 9999 || qingming.getYear() != year || winter.getYear() != year
                    || qingming.getMonthValue() != 4 || winter.getMonthValue() != 12
                    || years.putIfAbsent(year, new Terms(qingming, winter)) != null)
                throw new IllegalArgumentException("节气日历年份或日期无效");
        }
        return new Library(zone, years);
    }

    public static Map<String,String> facts(LocalDate date, ZoneId serverZone) {
        return library.facts(date, serverZone);
    }

    @SubscribeEvent public static void listeners(AddReloadListenerEvent event) {
        event.addListener((ResourceManagerReloadListener) Hk3SolarCalendar::reload);
    }

    private static void reload(ResourceManager manager) {
        Library next = new Library(ZoneId.of("Asia/Hong_Kong"), Map.of());
        try {
            var resource = manager.getResource(RESOURCE);
            if (resource.isPresent()) try (var reader = resource.get().openAsReader()) { next = parse(reader); }
        } catch (IOException | RuntimeException invalid) {
            LogUtils.getLogger().warn("[HK3GTL] 节气日历不可用，372/377保持休眠，不沿用旧缓存。", invalid);
        }
        library = next;
    }
}
