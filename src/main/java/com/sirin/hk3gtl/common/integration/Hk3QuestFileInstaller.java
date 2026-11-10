package com.sirin.hk3gtl.common.integration;

/** 中文说明：该处说明已按当前代码行为整理。*/

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Properties;

public final class Hk3QuestFileInstaller {
    private static final String PENDING = "pending.properties";
    private static final String MANIFEST = "originals.properties";

    private Hk3QuestFileInstaller() {}

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @FunctionalInterface
    public interface Resources {
        InputStream open(String relativePath) throws IOException;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Path install(Path questDir, String marker, String version,
                               List<String> chapters, List<String> legacy,
                               Resources resources) throws IOException {
        if (version == null || version.isBlank() || chapters.isEmpty()) {
            throw new IOException("Empty quest version or manifest");
        }
        Path root = questDir.toAbsolutePath().normalize();
        Path backups = root.resolveSibling("hk3gtl-quest-backups");
        checked(backups, PENDING);
        recover(root, backups);
        LinkedHashSet<String> owned = new LinkedHashSet<>(chapters);
        if (owned.size() != chapters.size() || owned.contains(marker)) {
            throw new IOException("Duplicate chapter or marker collision");
        }
        for (String path : legacy) {
            if (!owned.add(path) || path.equals(marker)) {
                throw new IOException("Overlapping legacy quest path: " + path);
            }
        }
        owned.add(marker);
        for (String path : owned) checked(root, path);
        Path markerPath = checked(root, marker);
        boolean complete = Files.isRegularFile(markerPath)
                && version.equals(Files.readString(markerPath, StandardCharsets.UTF_8).trim());
        for (String path : chapters) complete &= Files.isRegularFile(checked(root, path));
        if (complete) return null;

        // 缺资源必须在任何活动文件写入前失败；不留下虚假的成功版本。
        // 中文备注：该处说明已按当前代码行为整理。
        Map<String, byte[]> payload = new LinkedHashMap<>();
        for (String path : chapters) {
            try (InputStream in = resources.open(path)) {
                if (in == null) throw new IOException("Missing bundled quest resource: " + path);
                payload.put(path, in.readAllBytes());
            }
        }
        Files.createDirectories(backups);
        Path snapshot = Files.createTempDirectory(backups, "migration-");
        Properties manifest = new Properties();
        for (String path : owned) {
            Path current = checked(root, path);
            boolean exists = Files.exists(current, LinkOption.NOFOLLOW_LINKS);
            if (exists && !Files.isRegularFile(current)) throw new IOException("Not a quest file: " + current);
            manifest.setProperty(path, Boolean.toString(exists));
            if (exists) {
                Path copy = checked(snapshot.resolve("originals"), path);
                Files.createDirectories(copy.getParent());
                Files.copy(current, copy);
            }
        }
        writeProperties(snapshot.resolve(MANIFEST), manifest);
        Properties pending = new Properties();
        pending.setProperty("snapshot", snapshot.getFileName().toString());
        writeProperties(backups.resolve(PENDING), pending);
        try {
            for (Map.Entry<String, byte[]> entry : payload.entrySet()) {
                atomicWrite(checked(root, entry.getKey()), entry.getValue());
            }
            // 旧章节移出FTB读取目录，实际内容已经归档；不用删除旧文本。
            // 中文备注：该处说明已按当前代码行为整理。
            for (String path : legacy) {
                Path current = checked(root, path);
                if (Files.exists(current)) {
                    Path archived = checked(snapshot.resolve("retired"), path);
                    Files.createDirectories(archived.getParent());
                    Files.move(current, archived);
                }
            }
            atomicWrite(markerPath, version.getBytes(StandardCharsets.UTF_8));
            Files.delete(backups.resolve(PENDING));
            return snapshot;
        } catch (IOException failure) {
            try {
                recover(root, backups);
            } catch (IOException recoveryFailure) {
                failure.addSuppressed(recoveryFailure);
            }
            throw failure;
        }
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static void recover(Path root, Path backups) throws IOException {
        Path journal = checked(backups, PENDING);
        if (!Files.exists(journal)) return;
        Properties pending = readProperties(journal);
        String name = pending.getProperty("snapshot", "");
        if (!name.matches("migration-[a-zA-Z0-9-]+")) throw new IOException("Invalid quest journal");
        Path snapshot = backups.resolve(name);
        Properties manifest = readProperties(checked(snapshot, MANIFEST));
        if (manifest.isEmpty()) throw new IOException("Empty quest recovery manifest");
        // 两遍处理避免恢复了一半才发现另一份备份丢失；所有键均作路径校验。
        // 中文备注：该处说明已按当前代码行为整理。
        for (String path : manifest.stringPropertyNames()) {
            checked(root, path);
            String existed = manifest.getProperty(path);
            if (!existed.equals("true") && !existed.equals("false")) throw new IOException("Invalid manifest flag");
            if (existed.equals("true") && !Files.isRegularFile(checked(snapshot.resolve("originals"), path))) {
                throw new IOException("Missing quest backup: " + path);
            }
        }
        for (String path : manifest.stringPropertyNames()) {
            Path target = checked(root, path);
            if (Boolean.parseBoolean(manifest.getProperty(path))) {
                atomicWrite(target, Files.readAllBytes(checked(snapshot.resolve("originals"), path)));
            } else if (Files.exists(target)) {
                Path failed = checked(snapshot.resolve("failed-created"), path);
                Files.createDirectories(failed.getParent());
                if (Files.exists(failed)) throw new IOException("Recovery destination already exists: " + failed);
                Files.move(target, failed);
            }
        }
        Files.delete(journal);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static Path checked(Path root, String relative) throws IOException {
        Path base = root.toAbsolutePath().normalize();
        Path result = base.resolve(relative).normalize();
        if (relative.isBlank() || Path.of(relative).isAbsolute() || !result.startsWith(base) || result.equals(base)
                || !base.resolve(relative).equals(result)) {
            throw new IOException("Unsafe quest path: " + relative);
        }
        for (Path p = result; p != null; p = p.getParent()) {
            if (Files.isSymbolicLink(p)) throw new IOException("Symlink in quest path: " + p);
        }
        return result;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static void atomicWrite(Path target, byte[] bytes) throws IOException {
        Files.createDirectories(target.getParent());
        Path temp = Files.createTempFile(target.getParent(), ".hk3gtl-", ".tmp");
        try {
            Files.write(temp, bytes);
            try {
                Files.move(temp, target, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException ignored) {
                Files.move(temp, target, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(temp); // 中文备注：该处说明已按当前代码行为整理。
        }
    }

    /** 属性写入也采用单文件替换，避免半写日志。 / Replace property files atomically to avoid truncated journals. */
    private static void writeProperties(Path path, Properties properties) throws IOException {
        java.io.ByteArrayOutputStream bytes = new java.io.ByteArrayOutputStream();
        properties.store(bytes, "HK3GTL quest migration; preserve originals / keep for recovery");
        atomicWrite(path, bytes.toByteArray());
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static Properties readProperties(Path path) throws IOException {
        Properties properties = new Properties();
        try (InputStream in = Files.newInputStream(path)) {
            properties.load(in);
        }
        return properties;
    }
}
