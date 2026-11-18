package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleData;
import net.minecraft.nbt.CompoundTag;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

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

