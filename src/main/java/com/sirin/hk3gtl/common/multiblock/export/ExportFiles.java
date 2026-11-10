package com.sirin.hk3gtl.common.multiblock.export;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * 【文件职责】集中约束结构导出的文件名、固定目录与四份产物写入；由导出命令调用。
 * 【变更记录 #1】2026-10-31 17:42:29（第 1 次备注 · 内测5修订189）
 * - 删除：无；不再允许命令逐份覆盖既有产物。
 * - 新增：跨平台安全名称、目录边界、独占新建与失败清理；清理失败保留为原异常的抑制异常。
 * - 修改：四份文本先在命令内生成，再在固定目录创建；同名文件与符号链接一律拒绝覆盖。
 * - 用途：阻止服务器导出误覆盖与半套新文件；进程中断可能留下未完成的新文件，重试需另取名称。
 */
public final class ExportFiles {
    public static final String DIRECTORY = "hk3gtl_exports";
    private static final List<String> SUFFIXES = List.of(".txt", "_pattern_impl.txt", "_pattern_facade.txt", "_machine.txt");

    private ExportFiles() {}

    public static boolean validName(String name) {
        if (name == null || !name.matches("[a-z][a-z0-9_]{0,63}")) return false;
        String upper = name.toUpperCase(Locale.ROOT);
        return !upper.matches("CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9]");
    }

    /** 只创建本轮新文件；发生异常时清理这些文件，绝不回滚或删除已有文件。 */
    public static void write(Path serverDirectory, String name, List<String> contents) throws IOException {
        if (!validName(name)) throw new IOException("名称须为1至64位小写字母、数字或下划线，以字母开头且不是系统保留名");
        if (contents.size() != SUFFIXES.size() || contents.stream().anyMatch(s -> s == null)) {
            throw new IllegalArgumentException("导出必须提供四份完整文本");
        }
        Path root = serverDirectory.toAbsolutePath().normalize();
        Path dir = root.resolve(DIRECTORY);
        Files.createDirectories(dir);
        if (Files.isSymbolicLink(dir) || !Files.isDirectory(dir, LinkOption.NOFOLLOW_LINKS)
                || !dir.toRealPath().equals(root.toRealPath().resolve(DIRECTORY))) {
            throw new IOException("导出目录必须是服务器目录内的真实目录");
        }
        List<Path> created = new ArrayList<>();
        try {
            for (int i = 0; i < SUFFIXES.size(); i++) {
                Path file = dir.resolve(name + SUFFIXES.get(i));
                try (BufferedWriter writer = Files.newBufferedWriter(file, StandardCharsets.UTF_8,
                        StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
                    created.add(file);
                    writer.write(contents.get(i));
                }
            }
        } catch (IOException | RuntimeException failure) {
            for (Path file : created) {
                try {
                    Files.deleteIfExists(file);
                } catch (IOException | RuntimeException cleanup) {
                    failure.addSuppressed(cleanup);
                }
            }
            throw failure;
        }
    }
}
