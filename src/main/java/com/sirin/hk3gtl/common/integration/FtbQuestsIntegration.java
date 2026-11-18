package com.sirin.hk3gtl.common.integration;

import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraftforge.event.server.ServerAboutToStartEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class FtbQuestsIntegration {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final String FTB_QUESTS_MOD_ID = "ftbquests";
    private static final String QUEST_VERSION = "quest-schema-v16-defer-mx-replication-20261119";
    private static final String MARKER_FILE = ".hk3gtl_quest_version";
    private static final String RESOURCE_PREFIX = "/assets/" + Hk3Constants.MOD_ID + "/ftbquests/";

    private static final List<String> CHAPTER_FILES = List.of(
            "chapters/hk3_stargate.snbt",
            "chapters/hk3_voltage_01.snbt",
            "chapters/hk3_voltage_02.snbt",
            "chapters/hk3_voltage_03.snbt",
            "chapters/hk3_voltage_04.snbt",
            "chapters/hk3_voltage_05.snbt",
            "chapters/hk3_voltage_06.snbt",
            "chapters/hk3_voltage_07.snbt",
            "chapters/hk3_voltage_08.snbt",
            "chapters/hk3_voltage_09.snbt",
            "chapters/hk3_voltage_10.snbt",
            "chapters/hk3_voltage_11.snbt",
            "chapters/hk3_voltage_12.snbt",
            "chapters/hk3_voltage_13.snbt",
            "chapters/hk3_voltage_14.snbt",
            "chapters/hk3_voltage_15.snbt",
            "chapters/hk3_voltage_16.snbt",
            "chapters/hk3_multiblock_patterns.snbt"
    );

    private static final List<String> LEGACY_FILES = List.of(
            "chapters/hk3_industrial_early.snbt",
            "chapters/hk3_industrial_world.snbt",
            "chapters/hk3_industrial_late.snbt",
            "chapters/hk3_story_01.snbt",
            "chapters/hk3_story_02.snbt",
            "chapters/hk3_story_03.snbt",
            "chapters/hk3_story_04.snbt",
            "chapters/hk3_story_05.snbt",
            "chapters/hk3_story_06.snbt",
            "chapters/hk3_voltage_00.snbt",
            "chapters/hk3_ch1_honkai.snbt",
            "chapters/hk3_ch2_abyss.snbt",
            "chapters/hk3_ch3_imaginary.snbt",
            "chapters/hk3_ch4_quantum.snbt",
            "chapters/hk3_ch5_finality.snbt",
            "chapters/hk3_ch6_finale.snbt",

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
    public static void onServerAboutToStart(ServerAboutToStartEvent event) {
        if (!ModList.get().isLoaded(FTB_QUESTS_MOD_ID)) return;

        try {
            Path configDir = net.minecraftforge.fml.loading.FMLPaths.CONFIGDIR.get();
            Path questDir = configDir.resolve("ftbquests").resolve("quests");
            Path archive = Hk3QuestFileInstaller.install(questDir, MARKER_FILE, QUEST_VERSION,
                    CHAPTER_FILES, LEGACY_FILES,
                    path -> FtbQuestsIntegration.class.getResourceAsStream(RESOURCE_PREFIX + path));
            if (archive != null) {
                LOGGER.info("[HK3GTL] FTB Quests 同步完成 → {}，旧文件归档于 {}", QUEST_VERSION, archive);
            }
        } catch (IOException e) {
            LOGGER.error("[HK3GTL] FTB Quests 安全同步失败；保留备份并停止启动，请检查迁移日志。", e);
            throw new IllegalStateException("HK3GTL quest migration failed; backups retained", e);
        }
    }
}

