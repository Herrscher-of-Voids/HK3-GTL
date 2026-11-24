package com.sirin.hk3gtl.common.config;

import dev.toma.configuration.config.Config;
import dev.toma.configuration.config.Configurable;

@Config(id = "hk3gtl-ae", filename = "config/hk3gtl-ae", group = Hk3ConfigPages.GROUP)
public final class Hk3AeSettings {
    @Configurable
    @Configurable.Synchronized
    @Configurable.Comment({"hk3gtl.config.ae.nexus_planner.comment"})
    public boolean nexusPlanner = true;

    public static boolean nexusPlannerEnabled() {
        return Hk3ConfigPages.AE.nexusPlanner;
    }
}
