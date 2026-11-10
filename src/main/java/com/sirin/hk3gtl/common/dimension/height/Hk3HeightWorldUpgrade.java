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

/**
 * 【文件职责】旧档按文件夹精确选择；创建Level前先校验元数据备份，不修改区块或原始存档。
 * 【变更记录 #1】2026-10-29 23:06:53（第1次备注 · 本轮高度与预览修复）
 * - 删除：无；新增：精确选择、路径拒绝及原level.dat/level.dat_old的SHA256备份校验。
 * - 修改：无原存档内容写入；备份失败抛错，Service不得继续应用新边界。
 * - 用途：为已明确选择的旧档提供重开升级保护；这些元数据备份不能用于高处建成后的缩高回滚。
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
        Path directory = root.resolve("hk3gtl-height-backups").resolve(
            DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss").format(OffsetDateTime.now()) + "-" + UUID.randomUUID());
        if (Files.isSymbolicLink(directory.getParent()))
            throw new IOException("高度升级备份目录不可为符号链接：" + directory.getParent());
        Files.createDirectories(directory);
        StringBuilder receipt = new StringBuilder("目标排除上界=").append(topExclusive).append('\n');
        copyVerified(current, directory.resolve("level.dat"), receipt);
        Path previous = root.resolve("level.dat_old");
        if (!Files.notExists(previous, LinkOption.NOFOLLOW_LINKS))
            copyVerified(previous, directory.resolve("level.dat_old"), receipt);
        Path receiptFile = directory.resolve("校验记录.txt");
        Files.writeString(receiptFile, receipt, StandardCharsets.UTF_8);
        flush(receiptFile);
        return directory;
    }

    private static void copyVerified(Path source, Path target, StringBuilder receipt) throws IOException {
        if (!Files.isRegularFile(source, LinkOption.NOFOLLOW_LINKS))
            throw new IOException("高度升级备份源不是普通文件：" + source);
        byte[] original = digest(source);
        Files.copy(source, target);
        flush(target);
        if (!MessageDigest.isEqual(original, digest(target)) || !MessageDigest.isEqual(original, digest(source)))
            throw new IOException("高度升级备份不一致或源文件变化，拒绝扩高：" + source);
        receipt.append(source.getFileName()).append(" SHA256=").append(HexFormat.of().formatHex(original)).append('\n');
    }

    private static void flush(Path file) throws IOException {
        try (var channel = java.nio.channels.FileChannel.open(file, java.nio.file.StandardOpenOption.WRITE)) {
            channel.force(true);
        }
    }

    private static byte[] digest(Path source) throws IOException {
        try (var input = Files.newInputStream(source)) {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] buffer = new byte[8192];
            for (int length; (length = input.read(buffer)) >= 0;) digest.update(buffer, 0, length);
            return digest.digest();
        } catch (NoSuchAlgorithmException impossible) {
            throw new IllegalStateException("当前Java缺少SHA-256算法", impossible);
        }
    }
}
