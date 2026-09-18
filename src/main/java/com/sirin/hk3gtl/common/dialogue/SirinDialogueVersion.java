package com.sirin.hk3gtl.common.dialogue;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraftforge.fml.ModList;

import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 终局开场语言键版本段（如 v0_1_0），从模组版本号解析，供 {@code hk3gtl.dialogue.sirin.<suffix>.d01} 使用。
 */
public final class SirinDialogueVersion {

    private static final Pattern SEMVER = Pattern.compile("(\\d+)\\.(\\d+)\\.(\\d+)");

    private SirinDialogueVersion() {}

    /** 例如 {@code v0_1_0}，解析失败时为 {@code v0_0_0} */
    public static String introKeySuffix() {
        String raw = ModList.get().getModContainerById(Hk3Constants.MOD_ID)
                .map(c -> c.getModInfo().getVersion().toString())
                .orElse("0.0.0");
        Matcher m = SEMVER.matcher(raw);
        if (m.find()) {
            return String.format(Locale.ROOT, "v%s_%s_%s", m.group(1), m.group(2), m.group(3));
        }
        return "v0_0_0";
    }

    /** 0.2.0 及以上使用内测二专属终局开场（不混用内测一全文）。 */
    public static boolean isBeta2OrLater() {
        String raw = ModList.get().getModContainerById(Hk3Constants.MOD_ID)
                .map(c -> c.getModInfo().getVersion().toString())
                .orElse("0.0.0");
        Matcher m = SEMVER.matcher(raw);
        if (!m.find()) {
            return false;
        }
        int major = Integer.parseInt(m.group(1));
        int minor = Integer.parseInt(m.group(2));
        return major > 0 || minor >= 2;
    }

    public static int introLineCount() {
        return isBeta2OrLater() ? 24 : 52;
    }
}
