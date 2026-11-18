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
        var file = supb.getFile();
        if (Files.isRegularFile(file.findResource("com/gtlsupb/gtlsupb/common/machine/hatch/PatternAssemblyPartMachine.class"))
                || Files.isRegularFile(file.findResource("com/gtlsupb/gtlsupb/common/machine/multiblock/part/PatternAssemblyPartMachine.class"))) return true;
        LogUtils.getLogger().info("HK3GTL：未发现兼容的 GTL-Supb 样板总成，暂停专属概率订单。");
        return false;
    }
}
