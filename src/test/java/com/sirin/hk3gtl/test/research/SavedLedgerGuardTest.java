package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleData;
import net.minecraft.nbt.CompoundTag;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 【变更记录 #1】2026-09-27 04:32:00（第 1 次备注 · 内测5修订90）
 * 删除：无。新增：缺文件可新建、坏文件/目录拒绝回退、缺账户格式拒绝的边界验证。
 * 修改：测试夹具只写build下独立UUID目录，不访问玩家存档、不执行清理；用途：防止读错后静默清账。
 */
public final class SavedLedgerGuardTest {
    public static void main(String[] args) throws Exception {
        Path folder = Path.of("build", "ledger-guard-fixtures", UUID.randomUUID().toString());
        Files.createDirectories(folder);
        AtomicInteger creations = new AtomicInteger();
        var created = Hk3SavedDataGuard.freshIfMissing(folder.resolve("absent.dat"), () -> {
            creations.incrementAndGet(); return new Hk3WorldBubbleData();
        });
        if (created == null || creations.get() != 1) throw new AssertionError("fresh world factory");
        Path damaged = folder.resolve("damaged.dat"); byte[] bytes = {0, 1, 2, 3}; Files.write(damaged, bytes);
        reject(() -> Hk3SavedDataGuard.freshIfMissing(damaged, () -> { creations.incrementAndGet(); return null; }));
        reject(() -> Hk3SavedDataGuard.freshIfMissing(folder, () -> { creations.incrementAndGet(); return null; }));
        if (creations.get() != 1 || !java.util.Arrays.equals(bytes, Files.readAllBytes(damaged)))
            throw new AssertionError("failed read must neither replace data nor run factory");
        reject(() -> Hk3ResearchData.load(new CompoundTag()));
        reject(() -> Hk3WorldBubbleData.load(new CompoundTag()));
        CompoundTag legacy = new CompoundTag(); legacy.put("Accounts", new CompoundTag());
        if (Hk3ResearchData.load(legacy) == null) throw new AssertionError("legacy accounts retained");
        System.out.println("Saved ledger guard: absent, corrupt, directory, missing schema and legacy accounts passed");
    }
    private static void reject(Runnable action) {
        try { action.run(); } catch (IllegalArgumentException | IllegalStateException expected) { return; }
        throw new AssertionError("Unsafe empty-ledger fallback accepted");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
