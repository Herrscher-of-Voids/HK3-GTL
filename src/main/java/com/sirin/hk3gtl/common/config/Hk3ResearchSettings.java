package com.sirin.hk3gtl.common.config;

import dev.toma.configuration.config.Config;
import dev.toma.configuration.config.Configurable;

@Config(id = "hk3gtl-research", filename = "config/hk3gtl-research", group = Hk3ConfigPages.GROUP)
public final class Hk3ResearchSettings {
    @Configurable
    @Configurable.Synchronized
    @Configurable.Comment({"hk3gtl.config.research.enabled.comment"})
    public boolean enabled = true;

    public static boolean enabled() {
        return Hk3ConfigPages.RESEARCH.enabled;
    }
}
