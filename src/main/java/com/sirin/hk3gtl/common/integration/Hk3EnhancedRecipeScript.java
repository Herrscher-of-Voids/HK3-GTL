package com.sirin.hk3gtl.common.integration;

import com.google.common.hash.Hashing;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.loading.FMLPaths;
import org.slf4j.Logger;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

import static java.nio.charset.StandardCharsets.UTF_8;
import static java.nio.file.StandardCopyOption.ATOMIC_MOVE;
import static java.nio.file.StandardCopyOption.REPLACE_EXISTING;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class Hk3EnhancedRecipeScript {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final String NAME = "circuit_substitution.js";
    private static final String MANAGED = "// HK3GTL managed SHA256: ";
    private static final String FIRST_OPTIMIZED_HASH = "c8e29a264e468f6b64649f885438773aaf0f38a812f844eb12ebe70d3fe2523a";
    // 增强版 3.9.2 和 3.9.3 使用同一份原版脚本。
    private static final String STOCK_HASH = "f7ea6312ea2d4892e388f0cc68bc2960ec2e1f6cd0b6d7cb7e1ed246899cb817";

    private Hk3EnhancedRecipeScript() {}

    @SubscribeEvent
    public static void setup(FMLCommonSetupEvent event) {
        var mods = ModList.get();
        if (mods.isLoaded("kubejs") && mods.isLoaded("gtl_enhancedcore")) {
            event.enqueueWork(Hk3EnhancedRecipeScript::install);
        }
    }

    private static void install() {
        Path kubejs = FMLPaths.GAMEDIR.get().resolve("kubejs");
        Path script = kubejs.resolve("server_scripts").resolve(NAME);
        try (var resource = Hk3EnhancedRecipeScript.class.getResourceAsStream("/hk3gtl/kubejs/" + NAME)) {
            String body = normalized(resource.readAllBytes());
            String managed = MANAGED + hash(body) + "\n" + body;
            byte[] replacement = managed.getBytes(UTF_8);
            if (Files.exists(script)) {
                byte[] original = Files.readAllBytes(script);
                String text = normalized(original);
                if (text.equals(managed)) return;
                String currentHash = hash(text);
                if (!currentHash.equals(STOCK_HASH) && !currentHash.equals(FIRST_OPTIMIZED_HASH)
                        && !isUnmodifiedManagedScript(text)) {
                    LOGGER.warn("[HK3GTL] 保留未识别的 KubeJS 配方脚本：{}", script);
                    return;
                }
                backup(kubejs.resolve("hk3gtl-backups"), original);
            }
            Files.createDirectories(script.getParent());
            Path temporary = Files.createTempFile(script.getParent(), "hk3gtl-", ".tmp");
            try {
                Files.write(temporary, replacement);
                Files.move(temporary, script, ATOMIC_MOVE, REPLACE_EXISTING);
            } finally {
                Files.deleteIfExists(temporary);
            }
            LOGGER.info("[HK3GTL] 已安装 KubeJS 配方优化脚本：{}", script);
        } catch (IOException e) {
            LOGGER.error("[HK3GTL] 安装 KubeJS 配方优化脚本失败：{}", script, e);
        }
    }

    private static boolean isUnmodifiedManagedScript(String text) {
        int lineEnd = text.indexOf('\n');
        return text.startsWith(MANAGED) && lineEnd > MANAGED.length()
                && text.substring(MANAGED.length(), lineEnd).equals(hash(text.substring(lineEnd + 1)));
    }

    private static String hash(String text) {
        return Hashing.sha256().hashString(text, UTF_8).toString();
    }

    private static String normalized(byte[] bytes) {
        String text = new String(bytes, UTF_8).replace("\r\n", "\n");
        return text.startsWith("\uFEFF") ? text.substring(1) : text;
    }

    private static void backup(Path directory, byte[] original) throws IOException {
        Files.createDirectories(directory);
        Path archive = directory.resolve("circuit_substitution-" + Hashing.sha256().hashBytes(original) + ".zip");
        Path temporary = Files.createTempFile(directory, "hk3gtl-", ".tmp");
        try {
            try (var zip = new ZipOutputStream(Files.newOutputStream(temporary))) {
                zip.putNextEntry(new ZipEntry(NAME));
                zip.write(original);
                zip.closeEntry();
            }
            try (var zip = new ZipFile(temporary.toFile()); var entry = zip.getInputStream(zip.getEntry(NAME))) {
                if (!Arrays.equals(original, entry.readAllBytes())) throw new IOException("配方脚本备份校验失败");
            }
            Files.move(temporary, archive, ATOMIC_MOVE, REPLACE_EXISTING);
        } finally {
            Files.deleteIfExists(temporary);
        }
    }
}
