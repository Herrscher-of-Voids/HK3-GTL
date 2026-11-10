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

/**
 * 【文件职责】连接或切换维度时，只读记录客户端从服务器同步的实际维度类型和Level边界。
 * 【变更记录 #1】2026-10-17 21:11:26（第1次备注 · 修订166）
 * 删除：无。新增：客户端加载后独立高度回执，不含玩家身份、位置或世界种子。
 * 修改：不读取本地高度配置，不二次改写服务器维度类型。
 * 用途：与服务端导出逐项比对同步结果，不将单人回执冒充远端多人通过。
 * 【变更记录 #2】2026-10-29 23:13:43（第2次备注 · 修订182）
 * 删除：回执固定修订166的身份；新增：无；修改：回执修订为182。
 * 用途：区分本轮正常世界扩高与旧隔离测试证据，不改变客户端注册表或世界。
 */
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
