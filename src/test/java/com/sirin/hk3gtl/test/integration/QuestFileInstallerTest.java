package com.sirin.hk3gtl.test.integration;

import com.sirin.hk3gtl.common.integration.Hk3QuestFileInstaller;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Properties;

/**
 * 【变更记录 #1】2026-09-22 13:40:00（内测5第1次代码更新）
 * 新增真实临时目录的文件迁移回归；无删除，失败抛AssertionError令构建失败。
 * Real temporary-directory migration regressions; failures throw and fail the build.
 * 覆盖旧文本保留、缺资源、部分写入失败、崩溃恢复与路径边界；无需启动Minecraft。
 * Covers archival, missing resources, partial IO failure, crash recovery and path isolation.
 */
public final class QuestFileInstallerTest {
    private static final String MARKER = ".version";
    private static final List<String> CHAPTERS = List.of("chapters/a.snbt", "chapters/b.snbt");
    private static final List<String> LEGACY = List.of("chapters/old.snbt");
    private static int passed;

    /** 测试入口，无参数；留下独立临时目录供失败诊断，所有断言均不依赖-ea。 / No-arg entry; retain temp fixtures for diagnosis, independent of -ea. */
    public static void main(String[] args) throws Exception {
        testArchiveAndIdempotence();
        testMissingResource();
        testPartialWriteRollback();
        testCrashRecoveryBeforeVersionCheck();
        testMissingBackupRefusesRecovery();
        testRepairMissingChapter();
        testTraversalRefused();
        testManifestCollision();
        System.out.println("Quest migration: " + passed + " scenarios passed");
    }

    /** 覆盖前备份，退役不删文本，其他模组不受影响，同版本保留用户编辑。 / Archive before overwrite, retire losslessly, preserve other mods and same-version edits. */
    private static void testArchiveAndIdempotence() throws Exception {
        Path root = fixture();
        put(root, "chapters/other-mod.snbt", "foreign");
        Path archive = install(root, "v2");
        check(read(archive, "originals/chapters/a.snbt").equals("old-a"), "old chapter backed up");
        check(read(archive, "retired/chapters/old.snbt").equals("legacy"), "legacy retained");
        check(!Files.exists(root.resolve(LEGACY.get(0))), "legacy outside FTB scan root");
        check(read(root, "chapters/a.snbt").equals("new-chapters/a.snbt"), "new bytes installed");
        check(read(root, MARKER).equals("v2"), "version committed");
        check(read(root, "chapters/other-mod.snbt").equals("foreign"), "foreign chapter untouched");
        put(root, CHAPTERS.get(0), "player-edit");
        check(install(root, "v2") == null, "same version no-op");
        check(read(root, CHAPTERS.get(0)).equals("player-edit"), "same version customization preserved");
        passed++;
    }

    /** 资源缺失不得覆盖任何活动文件或提交标记。 / Missing resource must leave all live files and marker untouched. */
    private static void testMissingResource() throws Exception {
        Path root = fixture();
        expectFailure(() -> Hk3QuestFileInstaller.install(root, MARKER, "v2", CHAPTERS, LEGACY,
                path -> path.equals(CHAPTERS.get(1)) ? null : bytes("new")));
        check(read(root, CHAPTERS.get(0)).equals("old-a"), "missing resource leaves chapter");
        check(read(root, MARKER).equals("v1"), "missing resource leaves version");
        check(read(root, LEGACY.get(0)).equals("legacy"), "missing resource leaves legacy");
        passed++;
    }

    /** 先成功写一章，再因父路径是普通文件而失败，验证真实I/O回滚。 / Fail after first chapter write using a file as the next parent, verifying real IO rollback. */
    private static void testPartialWriteRollback() throws Exception {
        Path root = fixture();
        put(root, "blocked", "not-a-directory");
        expectFailure(() -> Hk3QuestFileInstaller.install(root, MARKER, "v2",
                List.of(CHAPTERS.get(0), "blocked/b.snbt"), LEGACY, path -> bytes("new")));
        check(read(root, CHAPTERS.get(0)).equals("old-a"), "partial commit rolled back");
        check(read(root, MARKER).equals("v1"), "rollback restores version");
        check(read(root, "blocked").equals("not-a-directory"), "unrelated blocker preserved");
        check(!Files.exists(root.resolveSibling("hk3gtl-quest-backups").resolve("pending.properties")), "recovered journal closed");
        passed++;
    }

    /** 模拟标记已写但事务未关闭的崩溃，恢复必须早于同版本跳过。 / Simulate crash after marker write; recovery must precede the version shortcut. */
    private static void testCrashRecoveryBeforeVersionCheck() throws Exception {
        Path root = fixture();
        Path archive = crashFixture(root, false);
        expectFailure(() -> Hk3QuestFileInstaller.install(root, MARKER, "v2", CHAPTERS, LEGACY, path -> null));
        check(read(root, CHAPTERS.get(0)).equals("old-a"), "crash restores old bytes");
        check(read(root, MARKER).equals("v1"), "crash restores old marker");
        check(!Files.exists(root.resolve(CHAPTERS.get(1))), "new chapter retired on recovery");
        check(read(archive, "failed-created/chapters/b.snbt").equals("partial-new-b"), "failed new bytes retained");
        check(install(root, "v2") != null, "retry succeeds after recovery");
        passed++;
    }

    /** 损坏备份不能被静默跳过；保留待恢复日志及活动文件。 / Missing backup must preserve journal and live files instead of skipping recovery. */
    private static void testMissingBackupRefusesRecovery() throws Exception {
        Path root = fixture();
        crashFixture(root, true);
        expectFailure(() -> install(root, "v2"));
        check(read(root, CHAPTERS.get(0)).equals("partial-new-a"), "corrupt backup fails before restore");
        check(Files.exists(root.resolveSibling("hk3gtl-quest-backups").resolve("pending.properties")), "journal retained");
        passed++;
    }

    /** 标记存在但章节缺失时必须修复，不能当作已安装。 / A version marker alone cannot hide a missing chapter. */
    private static void testRepairMissingChapter() throws Exception {
        Path root = fixture();
        put(root, MARKER, "v2");
        check(install(root, "v2") != null, "repair missing chapter despite matching version");
        check(Files.isRegularFile(root.resolve(CHAPTERS.get(1))), "missing chapter restored");
        passed++;
    }

    /** 清单不能写出任务目录。 / Manifest paths must never escape the quest root. */
    private static void testTraversalRefused() throws Exception {
        Path root = fixture();
        expectFailure(() -> Hk3QuestFileInstaller.install(root, MARKER, "v2",
                List.of("../outside.snbt"), LEGACY, path -> bytes("new")));
        check(!Files.exists(root.getParent().resolve("outside.snbt")), "outside path untouched");
        passed++;
    }

    /** 同一路径不能既安装又退役，防止错误清单移走新章节。 / A chapter cannot also be retired by the same manifest. */
    private static void testManifestCollision() throws Exception {
        Path root = fixture();
        expectFailure(() -> Hk3QuestFileInstaller.install(root, MARKER, "v2", CHAPTERS,
                List.of(CHAPTERS.get(0)), path -> bytes("new")));
        check(read(root, CHAPTERS.get(0)).equals("old-a"), "collision rejected without mutation");
        passed++;
    }

    /** 构造磁盘崩溃现场；missing控制是否缺失一份原始备份。 / Build on-disk interrupted transaction; missing omits one required backup. */
    private static Path crashFixture(Path root, boolean missing) throws IOException {
        Path backups = root.resolveSibling("hk3gtl-quest-backups");
        Path snapshot = backups.resolve("migration-test");
        if (!missing) put(snapshot, "originals/chapters/a.snbt", "old-a");
        put(snapshot, "originals/" + MARKER, "v1");
        Properties original = new Properties();
        original.setProperty(CHAPTERS.get(0), "true");
        original.setProperty(CHAPTERS.get(1), "false");
        original.setProperty(MARKER, "true");
        properties(snapshot.resolve("originals.properties"), original);
        Properties journal = new Properties();
        journal.setProperty("snapshot", "migration-test");
        properties(backups.resolve("pending.properties"), journal);
        put(root, CHAPTERS.get(0), "partial-new-a");
        put(root, CHAPTERS.get(1), "partial-new-b");
        put(root, MARKER, "v2");
        return snapshot;
    }

    /** 返回带旧章与版本的独立临时目录。 / Return an isolated fixture with an old chapter and version. */
    private static Path fixture() throws IOException {
        Path root = Files.createTempDirectory("hk3gtl-quest-test-").resolve("quests");
        put(root, CHAPTERS.get(0), "old-a");
        put(root, LEGACY.get(0), "legacy");
        put(root, MARKER, "v1");
        return root;
    }

    /** 测试资源供应器无外部依赖，返回实际归档路径。 / Supply deterministic test resources and return the archive path. */
    private static Path install(Path root, String version) throws IOException {
        return Hk3QuestFileInstaller.install(root, MARKER, version, CHAPTERS, LEGACY, path -> bytes("new-" + path));
    }

    /** UTF-8测试字节流。 / UTF-8 test stream. */
    private static ByteArrayInputStream bytes(String value) { return new ByteArrayInputStream(value.getBytes(StandardCharsets.UTF_8)); }
    /** 创建父目录后写入测试文本。 / Write fixture text after creating its parent. */
    private static void put(Path root, String path, String value) throws IOException {
        Files.createDirectories(root.resolve(path).getParent());
        Files.writeString(root.resolve(path), value, StandardCharsets.UTF_8);
    }
    /** 读取完整UTF-8文本用于字节内容核对。 / Read complete UTF-8 fixture content. */
    private static String read(Path root, String path) throws IOException { return Files.readString(root.resolve(path), StandardCharsets.UTF_8); }
    /** 写入与生产日志同格式的故障现场。 / Write an interrupted-journal fixture in the production format. */
    private static void properties(Path file, Properties props) throws IOException {
        Files.createDirectories(file.getParent());
        try (OutputStream out = Files.newOutputStream(file)) { props.store(out, "test fixture"); }
    }
    /** 断言不依赖JVM开关，失败立即传播。 / Assertions fail independently of JVM switches. */
    private static void check(boolean condition, String message) { if (!condition) throw new AssertionError(message); }
    @FunctionalInterface private interface Operation { void run() throws IOException; }
    /** 必须抛I/O异常；正常返回代表失败保护失效。 / Require IO failure; successful return means protection failed. */
    private static void expectFailure(Operation operation) throws IOException {
        try { operation.run(); } catch (IOException expected) { return; }
        throw new AssertionError("Expected migration failure");
    }
}
