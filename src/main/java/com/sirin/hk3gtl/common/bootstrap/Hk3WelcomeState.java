package com.sirin.hk3gtl.common.bootstrap;

import net.minecraft.nbt.CompoundTag;
import java.util.List;

/**
 * 更新说明的版本身份与个人已读状态，不授予任何游戏成果。
 */
public final class Hk3WelcomeState {
    public static final String SEEN_TAG = "hk3gtl_seen_welcome_version";
    public static final String CONTENT_REVISION = "release-notes-r188";
    public static final List<String> HISTORY = List.of("0.5.0", "0.4.0", "0.3.0", "0.2.0", "0.1.0");
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
