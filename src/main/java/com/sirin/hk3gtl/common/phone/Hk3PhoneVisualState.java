package com.sirin.hk3gtl.common.phone;

import net.minecraft.nbt.CompoundTag;

public final class Hk3PhoneVisualState {
    private Hk3PhoneVisualState() {}
    public static boolean changed(CompoundTag before,CompoundTag after){
        var a=before==null?new CompoundTag():before.copy();
        var b=after==null?new CompoundTag():after.copy();
        a.remove("Charge");b.remove("Charge");
        return !a.equals(b);
    }
}
