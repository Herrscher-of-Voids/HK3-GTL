package com.sirin.hk3gtl.common.dimension.height;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;

/** 只在临时目录检查精确选择与备份拒绝分支，不读写玩家存档。 */
public final class Hk3HeightWorldUpgradeTest {
    private Hk3HeightWorldUpgradeTest() {}

    public static void main(String[] args) throws IOException {
        Path root = Files.createTempDirectory("hk3-height-upgrade-");
        String folder = root.getFileName().toString();
        require(Hk3HeightWorldUpgrade.selected(root, List.of(folder)), "精确存档文件夹未匹配");
        require(!Hk3HeightWorldUpgrade.selected(root, List.of(folder + "-other")), "不得匹配前缀");
        require(!Hk3HeightWorldUpgrade.selected(root, List.of("*")), "不得匹配通配符");
        for (String invalid : List.of("", " ", ".", "..", "../save", "C:\\save", "save*", " save", "save;other"))
            require(!Hk3HeightWorldUpgrade.validFolderName(invalid), "非法名单被接受：" + invalid);
        require(Hk3HeightWorldUpgrade.validFolderName("礼堂测试 2026-10-29"), "中文与空格名称应可用");
        require(!Hk3HeightWorldUpgrade.selected(root, List.of()), "空名单不得启用旧档");
        rejects(() -> Hk3HeightWorldUpgrade.backup(root, 1024), "缺少level.dat必须拒绝");
        byte[] current = "旧世界元数据-当前".getBytes(StandardCharsets.UTF_8);
        byte[] previous = "旧世界元数据-前版".getBytes(StandardCharsets.UTF_8);
        Files.write(root.resolve("level.dat"), current);
        Path single = Hk3HeightWorldUpgrade.backup(root, 1024);
        require(Arrays.equals(current, Files.readAllBytes(single.resolve("level.dat"))), "当前备份内容变化");
        require(Files.notExists(single.resolve("level.dat_old")), "不得伪造缺少的旧元数据");
        Files.write(root.resolve("level.dat_old"), previous);
        Path both = Hk3HeightWorldUpgrade.backup(root, 1024);
        require(!single.equals(both), "不得覆盖旧备份");
        require(Arrays.equals(previous, Files.readAllBytes(both.resolve("level.dat_old"))), "旧元数据备份变化");
        require(Arrays.equals(current, Files.readAllBytes(root.resolve("level.dat"))), "备份不得修改当前存档");
        require(Files.readString(both.resolve("校验记录.txt")).contains("SHA256="), "缺少备份摘要");
        Files.delete(root.resolve("level.dat_old"));
        Files.createDirectory(root.resolve("level.dat_old"));
        rejects(() -> Hk3HeightWorldUpgrade.backup(root, 1024), "异常旧元数据路径必须拒绝");
        System.out.println("旧档高度升级名单与备份检查通过；仅使用临时目录，未执行游戏验收。");
    }

    private static void rejects(IoAction action, String message) throws IOException {
        try { action.run(); }
        catch (IOException expected) { return; }
        throw new AssertionError(message);
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    @FunctionalInterface private interface IoAction { void run() throws IOException; }
}
