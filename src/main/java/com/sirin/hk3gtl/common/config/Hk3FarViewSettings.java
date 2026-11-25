package com.sirin.hk3gtl.common.config;

import com.sirin.hk3gtl.common.farview.Hk3FarViewConfig;
import dev.toma.configuration.config.Config;
import dev.toma.configuration.config.Configurable;

@Config(id = "hk3gtl-farview", filename = "config/hk3gtl-farview", group = Hk3ConfigPages.GROUP)
public final class Hk3FarViewSettings {
    @Configurable
    @Configurable.Comment({"hk3gtl.config.farview.enabled.comment"})
    public boolean enabled = true;

    @Configurable
    @Configurable.Range(min = 256, max = 4096)
    @Configurable.Comment({"hk3gtl.config.farview.distance.comment"})
    public int distance = 2048;

    @Configurable
    @Configurable.Range(min = 8, max = 128)
    @Configurable.Comment({"hk3gtl.config.farview.gpu_mib.comment"})
    public int gpuMiB = 64;

    public void apply() {
        Hk3FarViewConfig.ENABLED.set(enabled);
        Hk3FarViewConfig.DISTANCE.set(distance);
        Hk3FarViewConfig.GPU_MIB.set(gpuMiB);
        Hk3FarViewConfig.SPEC.save();
    }
}
