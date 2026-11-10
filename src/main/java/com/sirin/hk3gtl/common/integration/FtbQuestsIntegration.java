package com.sirin.hk3gtl.common.integration;

/** 中文说明：该处说明已按当前代码行为整理。*/
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

/**
 * FTB Quests 自动导入 —— 按版本标记同步任务文件（仅版本变化时覆盖）。
 */
/**
 * 【变更记录 #1】2026-09-30 02:28:02（内测5修订107）
 * 删除：旧任务包版本标记。新增：电压注册键迁移版本。
 * 修改：已有实例下次服务端启动时，通过原有备份及回滚安装器同步本模组章节。
 * 用途：防止任务资源继续引用已移除物品ID；不改其他模组章节或玩家任务进度。
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
/** 【变更记录 #2】2026-10-01 14:10:35（修订129）：删除：无；新增/修改：安装八章正式教程，将旧六章归档；不触碰其他模组章节和世界任务账本；用途：任务和进度只投影真实账本，不授研究、物品或审查资格。 */
/** 【变更记录 #3】2026-10-01 15:13:33（修订131）：删除旧研究所分章规则；新增/修改：安装MAX与16档新电压章节，原八章移入备份，全部已有任务和检测ID保持；用途：按GTL电压页组织玩家教程，保留真实研究与既有任务进度。 */
/** 【变更记录 #4】2026-10-01 15:44:24（修订132）：删除无；新增横向布局资源版本；修改安装标记以备份更新17页坐标；用途：同步横向任务图，保留章节/任务ID、正文与世界完成数据。 */
/** 【变更记录 #5】2026-10-01 16:10:33（修订133）：删除无；新增暂停说明；修改任务安装标记恢复为已部署131，横向132源码与包另存；用途：遵守任务最后定案，本批其他系统更新不迁移任务布局或存档。 */
public class FtbQuestsIntegration {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final String FTB_QUESTS_MOD_ID = "ftbquests";
    private static final String QUEST_VERSION = "quest-schema-v4-voltage-r161";
    private static final String MARKER_FILE = ".hk3gtl_quest_version";
    private static final String RESOURCE_PREFIX = "/assets/" + Hk3Constants.MOD_ID + "/ftbquests/";

    /** 当前任务线章节（按 order_index 顺序）。新增章节：在此追加 + 打包对应 SNBT 资源。 */
    private static final List<String> CHAPTER_FILES = List.of(
            "chapters/hk3_voltage_00.snbt",
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
            "chapters/hk3_voltage_16.snbt"
    );

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static final List<String> LEGACY_FILES = List.of(

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

    /** 中文说明：该处说明已按当前代码行为整理。*/
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
// 修订161：仅移除八项旧版本章节兼容清理路径；本命名脚本不删除物理任务文件，也不执行实机任务迁移。
