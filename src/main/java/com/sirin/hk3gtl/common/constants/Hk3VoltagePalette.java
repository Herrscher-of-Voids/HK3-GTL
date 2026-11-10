package com.sirin.hk3gtl.common.constants;
/**
 * 【文件职责】批准的16档配色；纯数值类避免GT静态初始化循环。
 * 【变更记录 #1】2026-09-30 03:21:46（内测5修订108）
 * 删除：无。新增：主色、暗底文字色及传统16色接口的最近色回退。
 * 修改：无电压与工艺逻辑。用途：资源色卡与Java逐档比对。
 */
public final class Hk3VoltagePalette {
    private static final int[] MAIN = {0x428DFF, 0xF4AE40, 0xC93F63, 0x48C9A3, 0x91DCEB, 0x5969C8, 0xE56A38, 0xB8524A, 0x9B75CA, 0xB68A4F, 0xCECDA2, 0xCE54A8, 0xF3A9CF, 0xBDA9F3, 0x52BBD6, 0xDCC17B};
    private static final int[] TEXT = {0x428DFF, 0xF4AE40, 0xD15A79, 0x48C9A3, 0x91DCEB, 0x6D7BCF, 0xE56A38, 0xC16862, 0x9B75CA, 0xB68A4F, 0xCECDA2, 0xCE54A8, 0xF3A9CF, 0xBDA9F3, 0x52BBD6, 0xDCC17B};
    private static final String[] LEGACY = {"§9§l", "§6§l", "§c§l", "§3§l", "§b§l", "§9§l", "§c§l", "§c§l", "§7§l", "§c§l", "§7§l", "§5§l", "§7§l", "§7§l", "§b§l", "§7§l"};
    private Hk3VoltagePalette() {}
    private static int index(int tier) {
        if(tier<15 || tier>30) throw new IllegalArgumentException("Unsupported palette tier: "+tier);
        return tier-15;
    }
    public static int main(int tier) { return MAIN[index(tier)]; }
    public static int text(int tier) { return TEXT[index(tier)]; }
    // 传统String格式仅16色；精确RGB通过Component.Style或VC整数接口。
    public static String legacy(int tier) { return LEGACY[index(tier)]; }
}
