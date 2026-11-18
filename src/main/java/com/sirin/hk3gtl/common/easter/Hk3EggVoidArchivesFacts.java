package com.sirin.hk3gtl.common.easter;

import net.minecraft.world.phys.HitResult;

/** 079的只读使用条件，离线检查不初始化Minecraft物品注册表。 */
public final class Hk3EggVoidArchivesFacts {
    private Hk3EggVoidArchivesFacts() {}

    public static boolean accepts(boolean heldIdentity, int count, HitResult.Type target) {
        return heldIdentity && count > 0 && target == HitResult.Type.MISS;
    }
}
