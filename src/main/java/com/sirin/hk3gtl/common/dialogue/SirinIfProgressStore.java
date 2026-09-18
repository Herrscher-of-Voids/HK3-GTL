package com.sirin.hk3gtl.common.dialogue;



import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonParseException;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.dialogue.definition.SirinDialogueDefinitions;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.fml.loading.FMLPaths;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 西琳 IF 线已读进度：仅非专用服（单人/集成服）写入全局 config，按玩家 UUID 跨存档去重；
 * 专用服始终返回全量掩码且不读写文件，避免玩家间互相消耗 IF。
 */
public final class SirinIfProgressStore {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Object IO_LOCK = new Object();

    /** 全量掩码：随 IF 分支数动态生成（内测三起 10 条 → 低 10 位）。 */
    private static final int ALL_MASK = (1 << SirinDialogueDefinitions.IF_BRANCH_COUNT) - 1;
    private static final Path FILE_PATH = FMLPaths.CONFIGDIR.get().resolve("hk3gtl_sirin_if_progress.json");

    private static volatile boolean loaded;
    private static Map<String, Integer> usedMaskByPlayerUuid = new ConcurrentHashMap<>();

    private SirinIfProgressStore() {}

    /** 专用服不做跨存档去重：始终全量可选 */
    public static boolean usesGlobalIfDedup(ServerPlayer player) {
        return player.getServer() != null && !player.getServer().isDedicatedServer();
    }

    public static int availableMask(ServerPlayer player) {
        if (!usesGlobalIfDedup(player)) {
            return ALL_MASK;
        }
        ensureLoaded();
        int used = usedMaskByPlayerUuid.getOrDefault(player.getStringUUID(), 0);
        return (~used) & ALL_MASK;
    }

    /**
     * 记录 IF 已选。专用服不写文件且恒为成功；单人写入全局 JSON（临时文件 + 原子替换）。
     */
    public static boolean markUsed(ServerPlayer player, int optionIndex) {
        if (optionIndex < 0 || optionIndex >= SirinDialogueDefinitions.IF_BRANCH_COUNT) return false;
        if (!usesGlobalIfDedup(player)) {
            return true;
        }
        ensureLoaded();
        synchronized (IO_LOCK) {
            int used = usedMaskByPlayerUuid.getOrDefault(player.getStringUUID(), 0);
            int bit = 1 << optionIndex;
            if ((used & bit) != 0) return false;
            usedMaskByPlayerUuid.put(player.getStringUUID(), used | bit);
            saveInternal();
            return true;
        }
    }

    /** 调试用：清理当前玩家的 IF 已读记录 */
    public static void resetForPlayer(ServerPlayer player) {
        if (!usesGlobalIfDedup(player)) {
            return;
        }
        ensureLoaded();
        synchronized (IO_LOCK) {
            usedMaskByPlayerUuid.remove(player.getStringUUID());
            saveInternal();
        }
    }

    private static void ensureLoaded() {
        if (loaded) return;
        synchronized (IO_LOCK) {
            if (loaded) return;
            loaded = true;
            if (!Files.exists(FILE_PATH)) return;
            try (Reader reader = Files.newBufferedReader(FILE_PATH, StandardCharsets.UTF_8)) {
                ProgressFile parsed = GSON.fromJson(reader, ProgressFile.class);
                if (parsed != null && parsed.usedMaskByPlayerUuid != null) {
                    usedMaskByPlayerUuid = new ConcurrentHashMap<>(parsed.usedMaskByPlayerUuid);
                }
            } catch (IOException | JsonParseException e) {
                LOGGER.warn("[HK3GTL] 读取西琳 IF 进度失败，将以空进度启动：{}", e.toString());
                usedMaskByPlayerUuid = new ConcurrentHashMap<>();
            }
        }
    }

    private static void saveInternal() {
        try {
            Files.createDirectories(FILE_PATH.getParent());
            ProgressFile out = new ProgressFile();
            out.schema = 1;
            out.modid = Hk3Constants.MOD_ID;
            out.usedMaskByPlayerUuid = usedMaskByPlayerUuid;
            String json = GSON.toJson(out);
            Path tmp = FILE_PATH.resolveSibling(FILE_PATH.getFileName() + ".tmp");
            Files.writeString(tmp, json, StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING, StandardOpenOption.WRITE);
            try {
                Files.move(tmp, FILE_PATH, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
            } catch (AtomicMoveNotSupportedException e) {
                Files.move(tmp, FILE_PATH, StandardCopyOption.REPLACE_EXISTING);
            }
        } catch (IOException e) {
            LOGGER.warn("[HK3GTL] 保存西琳 IF 进度失败：{}", e.toString());
        }
    }

    private static final class ProgressFile {
        int schema;
        String modid;
        Map<String, Integer> usedMaskByPlayerUuid;
    }
}
