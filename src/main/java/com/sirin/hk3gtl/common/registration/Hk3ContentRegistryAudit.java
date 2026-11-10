package com.sirin.hk3gtl.common.registration;

import com.google.gson.JsonParser;
import com.mojang.logging.LogUtils;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

/** 中文说明：该处说明已按当前代码行为整理。*/
@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3ContentRegistryAudit {
    private Hk3ContentRegistryAudit() {}

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @SubscribeEvent
    public static void onServerStarted(ServerStartedEvent event) {
        String path = "/data/hk3gtl/catalog/industrial_content.json";
        try (var stream = Hk3ContentRegistryAudit.class.getResourceAsStream(path)) {
            if (stream == null) throw new IllegalStateException("Missing industrial content manifest");
            var entries = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8))
                    .getAsJsonObject().getAsJsonArray("entries");
            var missing = new ArrayList<String>();
            for (var element : entries) {
                var entry = element.getAsJsonObject();
                String kind = entry.get("kind").getAsString();
                var id = new ResourceLocation("hk3gtl", entry.get("id").getAsString());
                boolean found = switch (kind) {
                    case "item" -> ForgeRegistries.ITEMS.containsKey(id);
                    case "block" -> ForgeRegistries.BLOCKS.containsKey(id) && ForgeRegistries.ITEMS.containsKey(id);
                    case "fluid" -> ForgeRegistries.FLUIDS.containsKey(id)
                            && ForgeRegistries.ITEMS.containsKey(new ResourceLocation("hk3gtl", id.getPath() + "_bucket"));
                    default -> false;
                };
                if (!found) missing.add(kind + ":" + id);
            }
            if (missing.isEmpty()) LogUtils.getLogger().info("[HK3GTL-CONTENT-AUDIT] PASS: {} physical entries, world server started", entries.size());
            else LogUtils.getLogger().error("[HK3GTL-CONTENT-AUDIT] FAIL: {}", missing);
        } catch (Exception failure) {
            LogUtils.getLogger().error("[HK3GTL-CONTENT-AUDIT] Could not audit registered content", failure);
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
