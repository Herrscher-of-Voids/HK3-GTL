package com.sirin.hk3gtl.common.integration;


import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.List;

/**
 * FTB Quests 自动导入 —— 按版本标记同步任务文件（仅版本变化时覆盖）。
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class FtbQuestsIntegration {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final String FTB_QUESTS_MOD_ID = "ftbquests";
    private static final String QUEST_VERSION = "release-quests-v1";
    private static final String MARKER_FILE = ".hk3gtl_quest_version";
    private static final String RESOURCE_PREFIX = "/assets/" + Hk3Constants.MOD_ID + "/ftbquests/";

    /** 当前任务线章节（按 order_index 顺序）。新增章节：在此追加 + 打包对应 SNBT 资源。 */
    private static final List<String> CHAPTER_FILES = List.of(
            "chapters/hk3_ch1_honkai.snbt",
            "chapters/hk3_ch2_abyss.snbt",
            "chapters/hk3_ch3_imaginary.snbt",
            "chapters/hk3_ch4_quantum.snbt",
            "chapters/hk3_ch5_finality.snbt",
            "chapters/hk3_ch6_finale.snbt"
    );

    /** 历史版本遗留文件（含内测章节），同步时一并删除。 */
    private static final List<String> LEGACY_FILES = List.of(
            "chapters/honkai_gtl.snbt",
            "chapters/hk3_abyss.snbt",
            "chapters/hk3_graduation.snbt",
            "chapters/abyss_phase.snbt",
            "chapters/imaginary_phase.snbt",
            "chapters/quantum_phase.snbt",
            "chapters/finality_phase.snbt",
            ".hk3gtl_quests_imported"
    );

    @SubscribeEvent
    public static void onServerStarted(ServerStartedEvent event) {
        if (!ModList.get().isLoaded(FTB_QUESTS_MOD_ID)) return;

        try {
            Path configDir = net.minecraftforge.fml.loading.FMLPaths.CONFIGDIR.get();
            Path questDir = configDir.resolve("ftbquests").resolve("quests");
            Path markerPath = questDir.resolve(MARKER_FILE);

            if (Files.exists(markerPath)) {
                String existing = Files.readString(markerPath, StandardCharsets.UTF_8).trim();
                if (QUEST_VERSION.equals(existing)) return;
            }

            LOGGER.info("[HK3GTL] FTB Quests 任务同步 → {}", QUEST_VERSION);
            removeLegacyFiles(questDir);
            syncChapterFiles(questDir);
            Files.writeString(markerPath, QUEST_VERSION, StandardCharsets.UTF_8);
            LOGGER.info("[HK3GTL] FTB Quests 同步完成。");
        } catch (Exception e) {
            // 同步失败不影响模组主流程，仅记录日志
            LOGGER.error("[HK3GTL] FTB Quests 同步失败", e);
        }
    }

    private static void removeLegacyFiles(Path questDir) {
        for (String legacy : LEGACY_FILES) {
            try {
                Files.deleteIfExists(questDir.resolve(legacy));
            } catch (IOException exception) {
                LOGGER.warn("[HK3GTL] 无法删除旧 FTB Quests 文件: {}", legacy, exception);
            }
        }
    }

    private static void syncChapterFiles(Path questDir) throws IOException {
        for (String relativePath : CHAPTER_FILES) {
            Path target = questDir.resolve(relativePath);
            Files.createDirectories(target.getParent());
            String resourcePath = RESOURCE_PREFIX + relativePath;
            try (InputStream in = FtbQuestsIntegration.class.getResourceAsStream(resourcePath)) {
                if (in == null) {
                    LOGGER.warn("[HK3GTL] 缺失任务资源: {}", resourcePath);
                    continue;
                }
                Files.copy(in, target, StandardCopyOption.REPLACE_EXISTING);
            }
        }
    }
}
