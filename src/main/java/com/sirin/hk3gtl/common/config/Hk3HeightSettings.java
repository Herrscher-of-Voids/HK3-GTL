package com.sirin.hk3gtl.common.config;

import com.sirin.hk3gtl.common.dimension.height.Hk3HeightConfig;
import dev.toma.configuration.config.Config;
import dev.toma.configuration.config.Configurable;

@Config(id = "hk3gtl-height", filename = "config/hk3gtl-height", group = Hk3ConfigPages.GROUP)
public final class Hk3HeightSettings {
    @Configurable
    @Configurable.Synchronized
    @Configurable.Comment({"hk3gtl.config.height.new_world_mode.comment"})
    public Hk3HeightConfig.NewWorldMode newWorldMode = Hk3HeightConfig.NewWorldMode.ALL_NEW_WORLDS;

    @Configurable
    @Configurable.Synchronized
    @Configurable.Range(min = 528, max = 2032)
    @Configurable.Comment({"hk3gtl.config.height.top_exclusive.comment"})
    public int topExclusive = 2032;

    @Configurable
    @Configurable.Synchronized
    @Configurable.Comment({"hk3gtl.config.height.existing_worlds.comment"})
    public String[] existingWorlds = {};

    public void apply() {
        Hk3HeightConfig.MODE.set(newWorldMode);
        Hk3HeightConfig.TOP_EXCLUSIVE.set(topExclusive);
        Hk3HeightConfig.EXISTING_WORLDS.set(java.util.Arrays.asList(existingWorlds));
        Hk3HeightConfig.SPEC.save();
    }
}
