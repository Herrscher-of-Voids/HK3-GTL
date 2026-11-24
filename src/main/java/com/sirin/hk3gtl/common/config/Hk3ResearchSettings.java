package com.sirin.hk3gtl.common.config;

import dev.toma.configuration.config.Config;
import dev.toma.configuration.config.Configurable;
import dev.toma.configuration.client.IValidationHandler;

@Config(id = "hk3gtl-research", filename = "config/hk3gtl-research", group = Hk3ConfigPages.GROUP)
public final class Hk3ResearchSettings {
    @Configurable
    @Configurable.Synchronized
    @Configurable.Comment({"hk3gtl.config.research.enabled.comment"})
    @Configurable.ValueUpdateCallback(method = "onUpdate")
    public boolean enabled = true;

    private static Runnable changeListener = () -> {};

    public static boolean enabled() {
        return Hk3ConfigPages.RESEARCH.enabled;
    }

    public static void setChangeListener(Runnable listener) {
        changeListener = listener;
    }

    public void onUpdate(String[] path, IValidationHandler handler) {
        changeListener.run();
    }
}
