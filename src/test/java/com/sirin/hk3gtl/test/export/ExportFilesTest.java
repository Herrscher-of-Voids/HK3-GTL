package com.sirin.hk3gtl.test.export;

import com.sirin.hk3gtl.common.multiblock.export.ExportFiles;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;

/**
 * 【文件职责】使用真实临时文件验证导出边界、同名保护、失败回滚与符号链接拒绝。
 * 【变更记录 #1】2026-10-31 17:42:29（内测5修订189）
 * - 删除：无。新增：纯Java文件系统回归，无需Minecraft启动。
 * - 修改：无。用途：保证失败不损坏旧产物，拒绝越界名称与目录；不代替游戏权限验收。
 */
public final class ExportFilesTest {
    private static int checks;

    public static void main(String[] args) throws Exception {
        Path root = Files.createTempDirectory("hk3-export-test-");
        try {
            names();
            successfulAndDuplicate(root.resolve("success"));
            rollback(root.resolve("rollback"));
            invalidBeforeFilesystem(root.resolve("invalid"));
            directoryBoundary(root.resolve("boundary"));
            System.out.println("ExportFilesTest：" + checks + " 项通过");
        } finally {
            try (var paths = Files.walk(root)) {
                for (Path path : paths.sorted(Comparator.reverseOrder()).toList()) Files.deleteIfExists(path);
            }
        }
    }

    private static void names() {
        check(ExportFiles.validName("machine_01"), "正常名称");
        check(ExportFiles.validName("a".repeat(64)), "64字符边界");
        for (String name : List.of("../world", "a/b", "a\\b", "..", "a.txt", "a-1", "A", "1machine",
                "con", "nul", "com1", "lpt9", "", "a".repeat(65))) {
            check(!ExportFiles.validName(name), "拒绝非法或系统保留名：" + name);
        }
    }

    private static void successfulAndDuplicate(Path root) throws IOException {
        List<String> text = List.of("中文切片", "实现", "门面", "机器");
        ExportFiles.write(root, "machine", text);
        Path dir = root.resolve(ExportFiles.DIRECTORY);
        List<String> suffixes = List.of(".txt", "_pattern_impl.txt", "_pattern_facade.txt", "_machine.txt");
        for (int i = 0; i < 4; i++) {
            check(Files.readString(dir.resolve("machine" + suffixes.get(i))).equals(text.get(i)), "四份UTF-8内容完整");
        }
        expectFailure(() -> ExportFiles.write(root, "machine", List.of("改写", "改写", "改写", "改写")));
        check(Files.readString(dir.resolve("machine.txt")).equals(text.get(0)), "重复名称保护旧内容");
        check(count(dir) == 4, "重复导出不产生附加文件");
    }

    private static void rollback(Path root) throws IOException {
        Path dir = Files.createDirectories(root.resolve(ExportFiles.DIRECTORY));
        Path collision = dir.resolve("machine_machine.txt");
        Files.writeString(collision, "先前文件");
        expectFailure(() -> ExportFiles.write(root, "machine", List.of("一", "二", "三", "四")));
        check(count(dir) == 1, "第四份冲突时撤销本轮前三份新文件");
        check(Files.readString(collision).equals("先前文件"), "回滚绝不删除冲突旧文件");
        Files.delete(collision);
        ExportFiles.write(root, "machine", List.of("一", "二", "三", "四"));
        check(count(dir) == 4, "清除外部冲突后可重试");
    }

    private static void invalidBeforeFilesystem(Path root) throws IOException {
        expectFailure(() -> ExportFiles.write(root, "../escape", List.of("一", "二", "三", "四")));
        check(!Files.exists(root), "非法名称在创建目录前拒绝");
    }

    private static void directoryBoundary(Path root) throws IOException {
        Files.createDirectories(root);
        Path directory = root.resolve(ExportFiles.DIRECTORY);
        Files.writeString(directory, "既有普通文件");
        expectFailure(() -> ExportFiles.write(root, "machine", List.of("一", "二", "三", "四")));
        check(Files.readString(directory).equals("既有普通文件"), "输出目录被普通文件占用时拒绝且不覆盖");
        Files.delete(directory);
        Path outside = Files.createDirectories(root.resolve("outside"));
        try {
            Files.createSymbolicLink(directory, outside);
        } catch (IOException | UnsupportedOperationException unavailable) {
            System.out.println("符号链接用例未执行：当前系统不允许创建链接；" + unavailable.getMessage());
            return;
        }
        expectFailure(() -> ExportFiles.write(root, "machine", List.of("一", "二", "三", "四")));
        check(count(outside) == 0, "符号链接目录拒绝且目标目录无写入");
    }

    private static long count(Path dir) throws IOException {
        try (var files = Files.list(dir)) { return files.count(); }
    }

    private static void expectFailure(IoAction action) throws IOException {
        try { action.run(); } catch (IOException expected) { checks++; return; }
        throw new AssertionError("操作应拒绝");
    }

    private static void check(boolean passed, String message) {
        if (!passed) throw new AssertionError(message);
        checks++;
    }

    @FunctionalInterface
    private interface IoAction { void run() throws IOException; }
}
