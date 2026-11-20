package com.sirin.hk3gtl.common.dimension.height;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

/**
 * 旧档按文件夹精确选择；创建Level前先校验元数据备份，不修改区块或原始存档。
 */
public final class Hk3HeightWorldUpgrade {
    private Hk3HeightWorldUpgrade() {}

    public static boolean validFolderName(String name) {
        return name != null && !name.isBlank() && name.equals(name.strip())
            && !name.equals(".") && !name.equals("..")
            && name.chars().noneMatch(c -> Character.isISOControl(c) || "/\\:*?\"<>|;".indexOf(c) >= 0);
    }

    public static boolean selected(Path worldRoot, List<? extends String> folders) {
        String name = worldRoot.toAbsolutePath().normalize().getFileName().toString();
        return validFolderName(name) && folders.stream().anyMatch(name::equals);
    }

    /** 只备份启动前的元数据；写入高处内容后，不能靠这两份文件缩高回滚。 */
    public static Path backup(Path worldRoot, int topExclusive) throws IOException {
        Hk3HeightPolicy.requireTopExclusive(topExclusive);
        Path root = worldRoot.toRealPath();
        Path current = root.resolve("level.dat");
        if (!Files.isRegularFile(current, LinkOption.NOFOLLOW_LINKS))
            throw new IOException("旧档缺少普通level.dat文件，拒绝扩高：" + current);
        Path directory = root.resolve("hk3gtl-height-backups");
        if (Files.isSymbolicLink(directory))
            throw new IOException("高度升级备份目录不可为符号链接：" + directory);
        Files.createDirectories(directory);
        Path archive = directory.resolve(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss").format(OffsetDateTime.now())
                + "-" + UUID.randomUUID() + ".zip");
        var files = new LinkedHashMap<String, byte[]>();
        StringBuilder receipt = new StringBuilder("仅含扩高前的元数据。写入高处区块后，完整回滚需要另行恢复区块。\n目标排除上界=")
                .append(topExclusive).append('\n');
        for (String name : List.of("level.dat", "level.dat_old")) {
            Path source = root.resolve(name);
            if (name.equals("level.dat_old") && Files.notExists(source, LinkOption.NOFOLLOW_LINKS)) continue;
            if (!Files.isRegularFile(source, LinkOption.NOFOLLOW_LINKS))
                throw new IOException("高度升级备份源不是普通文件：" + source);
            byte[] bytes = Files.readAllBytes(source);
            files.put(name, bytes);
            receipt.append(name).append(" SHA256=").append(HexFormat.of().formatHex(digest(bytes))).append('\n');
        }
        files.put("校验记录.txt", receipt.toString().getBytes(StandardCharsets.UTF_8));
        Path temporary = Files.createTempFile(directory, "height-", ".tmp");
        try {
            try (var zip = new ZipOutputStream(Files.newOutputStream(temporary))) {
                for (var entry : files.entrySet()) {
                    zip.putNextEntry(new ZipEntry(entry.getKey()));
                    zip.write(entry.getValue());
                    zip.closeEntry();
                }
            }
            try (var zip = new ZipFile(temporary.toFile())) {
                for (var entry : files.entrySet()) {
                    try (var input = zip.getInputStream(zip.getEntry(entry.getKey()))) {
                        if (!Arrays.equals(entry.getValue(), input.readAllBytes()))
                            throw new IOException("高度升级备份校验失败：" + entry.getKey());
                    }
                }
            }
            for (String name : List.of("level.dat", "level.dat_old")) {
                if (files.containsKey(name) && !Arrays.equals(files.get(name), Files.readAllBytes(root.resolve(name))))
                    throw new IOException("备份期间存档元数据变化，拒绝扩高：" + name);
            }
            flush(temporary);
            Files.move(temporary, archive);
            return archive;
        } finally {
            Files.deleteIfExists(temporary);
        }
    }

    private static void flush(Path file) throws IOException {
        try (var channel = java.nio.channels.FileChannel.open(file, java.nio.file.StandardOpenOption.WRITE)) {
            channel.force(true);
        }
    }

    private static byte[] digest(byte[] bytes) {
        try {
            return MessageDigest.getInstance("SHA-256").digest(bytes);
        } catch (NoSuchAlgorithmException impossible) {
            throw new IllegalStateException(impossible);
        }
    }
}
