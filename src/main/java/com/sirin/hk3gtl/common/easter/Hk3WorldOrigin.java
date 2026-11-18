package com.sirin.hk3gtl.common.easter;

import net.minecraft.nbt.CompoundTag;
import java.time.*;
import java.util.Optional;

 





public record Hk3WorldOrigin(Instant createdAt) {
    public static final String TAG = "HK3GTLWorldOrigin";
    private static final String SOURCE = "hk3gtl:new-world-constructor:v1";
    public Hk3WorldOrigin {
        if (createdAt == null || createdAt.toEpochMilli() <= 0) throw new IllegalArgumentException("世界创建时间无效");
        createdAt = Instant.ofEpochMilli(createdAt.toEpochMilli());
    }
    public CompoundTag save() {
        var tag = new CompoundTag();
        tag.putInt("Schema", 1); tag.putString("Source", SOURCE); tag.putLong("CreatedAt", createdAt.toEpochMilli());
        return tag;
    }
    public static Optional<Hk3WorldOrigin> read(CompoundTag tag) {
        if (!tag.contains("Schema", 3) || tag.getInt("Schema") != 1 || !tag.contains("Source", 8)
                || !SOURCE.equals(tag.getString("Source")) || !tag.contains("CreatedAt", 4) || tag.getLong("CreatedAt") <= 0)
            return Optional.empty();
        try { return Optional.of(new Hk3WorldOrigin(Instant.ofEpochMilli(tag.getLong("CreatedAt")))); }
        catch (DateTimeException | ArithmeticException invalid) { return Optional.empty(); }
    }
    public boolean anniversaryReached(Instant now, ZoneId zone) {
        try { return !now.isBefore(createdAt.atZone(zone).plusYears(1).toInstant()); }
        catch (DateTimeException | ArithmeticException invalid) { return false; }
    }
}
