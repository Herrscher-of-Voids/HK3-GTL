package com.sirin.hk3gtl.common.integration.ae.exact;

import com.mojang.logging.LogUtils;
import net.minecraftforge.fml.loading.LoadingModList;

import java.nio.file.Files;

public final class Hk3ProbabilitySupport {
    public static final boolean AVAILABLE = detect();

    private Hk3ProbabilitySupport() {}

    private static boolean detect() {
        var mods = LoadingModList.get();
        var supb = mods.getModFileById("gtlsupb");
        if (supb == null || mods.getModFileById("ae2") == null || mods.getModFileById("gtlcore") == null) return false;
        var assembly = supb.getFile().findResource("com/gtlsupb/gtlsupb/common/machine/hatch/PatternAssemblyPartMachine.class");
        if (Files.isRegularFile(assembly)) return true;
        LogUtils.getLogger().info("HK3GTL: GTL-Supb has no compatible pattern assembly; dedicated probability orders are disabled.");
        return false;
    }
}
