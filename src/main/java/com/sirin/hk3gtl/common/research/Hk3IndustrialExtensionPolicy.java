package com.sirin.hk3gtl.common.research;

/** 2026-10-30（修订182）：I40–I45沿用暂定工艺拒绝策略，建筑获批不改变研究、工艺或旅行许可。 */

 
 
import java.util.Set;



 







 






public final class Hk3IndustrialExtensionPolicy {
    public static final Set<String> GUARDED_ROLES = Set.of("I14", "I15", "I16", "I18",
            "I19", "I20", "I21", "I22", "I23", "I24", "I25", "I26", "I27", "I28",
            "I29", "I30", "I31", "I32", "I33", "I34", "I35", "I36", "I37", "I38", "I39",
            "I40", "I41", "I42", "I43", "I44", "I45");

    private Hk3IndustrialExtensionPolicy() {}

    public static boolean permits(String role, boolean provisional) {
        return !GUARDED_ROLES.contains(role) || !provisional;
    }
}
