package com.sirin.hk3gtl.common.bootstrap;

import net.minecraft.nbt.CompoundTag;
import java.util.List;

/**
 * 更新说明的版本身份与个人已读状态，不授予任何游戏成果。
 * 【变更记录 #1】2026-10-01 16:11:00（修订133）
 * 删除：无；新增：说明修订独立于模组版本、精确确认与历史正文目录。
 * 修改：沿用个人hk3gtl_键，使现有死亡/末地返回复制器继续生效。
 * 用途：只在玩家确认对应说明后记已读，关闭、翻页、历史阅读均不确认。
 */
/** 【变更记录 #2】2026-10-01 22:50:14（第2次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/** 【变更记录 #3】2026-10-31 15:54:41（第3次备注 · 修订188）：删除无；新增健康检查范围修正文案对应的说明修订身份；修改正文修订从 release-notes-r155 升为 release-notes-r188，同模组版本也重新提示阅读；用途：让已有玩家获知六类注册检查的实际边界，确认前不改变已读状态与游戏进度。 */
public final class Hk3WelcomeState {
    public static final String SEEN_TAG = "hk3gtl_seen_welcome_version";
    public static final String CONTENT_REVISION = "release-notes-r188";
    public static final List<String> HISTORY = List.of("0.4.0", "0.3.0", "0.2.0", "0.1.0");
    public static final List<String> CURRENT_PROSE = List.of("U06", "U07", "U10", "U15", "U16", "U18");
    public static final List<String> COMPATIBILITY_PROSE = List.of("U21", "U22", "U23", "U24", "U25", "U05");
    private Hk3WelcomeState() {}

    public static String contentId(String version) { return version + "/" + CONTENT_REVISION; }
    public static boolean first(CompoundTag data) { return data.getString(SEEN_TAG).isEmpty(); }
    public static boolean unread(CompoundTag data, String version) {
        return !contentId(version).equals(data.getString(SEEN_TAG));
    }
    public static boolean acknowledge(CompoundTag data, String version, String displayed, String offered) {
        String current = contentId(version);
        if (!current.equals(displayed) || !current.equals(offered)) return false;
        data.putString(SEEN_TAG, current);
        return true;
    }
}
