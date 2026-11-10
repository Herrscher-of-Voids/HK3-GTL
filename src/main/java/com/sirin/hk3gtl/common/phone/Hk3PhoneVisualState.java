package com.sirin.hk3gtl.common.phone;

import net.minecraft.nbt.CompoundTag;

/** 【变更记录 #1】2026-10-01 01:25:10（修订125）：删除无；新增手机可见状态比较；修改只忽略电池Charge，不忽略名称、模型或其他元数据；用途：装备动画与真实电池存储分离，比较不修改原物品NBT。 */
public final class Hk3PhoneVisualState {
    private Hk3PhoneVisualState() {}
    public static boolean changed(CompoundTag before,CompoundTag after){
        var a=before==null?new CompoundTag():before.copy();
        var b=after==null?new CompoundTag():after.copy();
        a.remove("Charge");b.remove("Charge");
        return !a.equals(b);
    }
}
