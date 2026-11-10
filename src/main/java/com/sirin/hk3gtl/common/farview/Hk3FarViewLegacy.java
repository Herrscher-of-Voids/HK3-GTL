package com.sirin.hk3gtl.common.farview;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.saveddata.SavedData;

/** 旧缓存只提供曾观察过的区域坐标；原有粗采样值绝不转换为新几何，也不覆写旧文件。 */
final class Hk3FarViewLegacy extends SavedData {
    final long[] areas;
    private Hk3FarViewLegacy(long[] areas){this.areas=areas;}
    static Hk3FarViewLegacy load(CompoundTag root) {
        var tiles=root.getList("tiles",Tag.TAG_COMPOUND);long[] keys=new long[Math.min(4096,tiles.size())];
        for(int i=0;i<keys.length;i++)keys[i]=tiles.getCompound(i).getLong("key");
        return new Hk3FarViewLegacy(keys);
    }
    @Override public CompoundTag save(CompoundTag root){throw new IllegalStateException("旧远景缓存仅供只读迁移");}
}
