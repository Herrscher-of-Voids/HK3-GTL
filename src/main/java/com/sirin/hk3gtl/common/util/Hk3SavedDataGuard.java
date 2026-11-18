package com.sirin.hk3gtl.common.util;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.storage.LevelResource;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.Function;
import java.util.function.Supplier;

 






public final class Hk3SavedDataGuard {
    private Hk3SavedDataGuard() {}
    public static <T extends SavedData> T get(MinecraftServer server, String name,
                                             Function<CompoundTag, T> load, Supplier<T> create) {
        if (!server.isSameThread()) throw new IllegalStateException("Saved ledger requires server thread");
        Path file = server.getWorldPath(LevelResource.ROOT).resolve("data").resolve(name + ".dat");
        return server.overworld().getDataStorage().computeIfAbsent(load, () -> freshIfMissing(file, create), name);
    }

    /** 存在或无法判定是否存在都拒绝覆盖；先检查再调用工厂，错误不会获得可写空账本。 */
    public static <T> T freshIfMissing(Path file, Supplier<T> create) {
        if (!Files.notExists(file, java.nio.file.LinkOption.NOFOLLOW_LINKS))
            throw new IllegalStateException("账本读取失败，拒绝重置现有文件：" + file);
        return create.get();
    }
}
