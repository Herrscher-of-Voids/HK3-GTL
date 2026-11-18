package com.sirin.hk3gtl.client;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mojang.logging.LogUtils;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.registries.Registries;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.level.LevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;











@Mod.EventBusSubscriber(modid = "hk3gtl", value = Dist.CLIENT)
public final class Hk3HeightClientAudit {
    private Hk3HeightClientAudit() {}

    @SubscribeEvent
    public static void loaded(LevelEvent.Load event) {
        if (!(event.getLevel() instanceof ClientLevel level)) return;
        try {
            JsonObject receipt = new JsonObject();
            receipt.addProperty("schema", 1); receipt.addProperty("revision", 182);
            receipt.addProperty("captured_at", OffsetDateTime.now().toString());
            receipt.addProperty("dimension", level.dimension().location().toString());
            receipt.addProperty("min_y", level.getMinBuildHeight());
            receipt.addProperty("height", level.getHeight());
            receipt.addProperty("top_exclusive", level.getMaxBuildHeight());
            receipt.addProperty("sections", level.getSectionsCount());
            JsonArray types = new JsonArray();
            for (var entry : level.registryAccess().registryOrThrow(Registries.DIMENSION_TYPE).entrySet()) {
                JsonObject row = new JsonObject();
                row.addProperty("id", entry.getKey().location().toString());
                row.addProperty("min_y", entry.getValue().minY());
                row.addProperty("height", entry.getValue().height());
                row.addProperty("logical_height", entry.getValue().logicalHeight());
                types.add(row);
            }
            receipt.add("synced_dimension_types", types);
            var directory = FMLPaths.GAMEDIR.get().resolve("logs/hk3gtl-height-audit");
            Files.createDirectories(directory);
            var file = directory.resolve("client-" + DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss").format(OffsetDateTime.now()) + "-" + UUID.randomUUID() + ".json");
            Files.writeString(file, new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create().toJson(receipt), StandardCharsets.UTF_8);
            LogUtils.getLogger().info("[HK3GTL-HEIGHT-AUDIT] 客户端高度实际回执：{}", file);
        } catch (Exception failure) {
            LogUtils.getLogger().error("[HK3GTL-HEIGHT-AUDIT] 客户端高度回执失败", failure);
        }
    }
}
