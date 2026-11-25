package com.sirin.hk3gtl.common.config;

import com.sirin.hk3gtl.common.phone.Hk3PhoneConfig;
import dev.toma.configuration.config.Config;
import dev.toma.configuration.config.Configurable;

@Config(id = "hk3gtl-phone", filename = "config/hk3gtl-phone", group = Hk3ConfigPages.GROUP)
public final class Hk3PhoneSettings {
    @Configurable @Configurable.Comment({"hk3gtl.config.phone.right_side.comment"})
    public boolean rightSide = true;
    @Configurable @Configurable.Range(min = 0, max = 500) @Configurable.Comment({"hk3gtl.config.phone.horizontal_margin.comment"})
    public int horizontalMargin = 12;
    @Configurable @Configurable.Range(min = 0, max = 600) @Configurable.Comment({"hk3gtl.config.phone.top.comment"})
    public int top = 24;
    @Configurable @Configurable.DecimalRange(min = 0.6, max = 1.5) @Configurable.Comment({"hk3gtl.config.phone.scale.comment"})
    public double scale = 1.0;
    @Configurable @Configurable.Range(min = 60, max = 86) @Configurable.Comment({"hk3gtl.config.phone.phone_size.comment"})
    public int phoneSize = 72;
    @Configurable @Configurable.Comment({"hk3gtl.config.phone.sound.comment"})
    public boolean sound = true;
    @Configurable @Configurable.Comment({"hk3gtl.config.phone.chatter.comment"})
    public boolean chatter = true;
    @Configurable @Configurable.Comment({"hk3gtl.config.phone.do_not_disturb.comment"})
    public boolean doNotDisturb;
    @Configurable @Configurable.DecimalRange(min = -1.0, max = 1.0) @Configurable.Comment({"hk3gtl.config.phone.position_x.comment"})
    public double positionX = -1.0;
    @Configurable @Configurable.DecimalRange(min = -1.0, max = 1.0) @Configurable.Comment({"hk3gtl.config.phone.position_y.comment"})
    public double positionY = -1.0;
    @Configurable @Configurable.Comment({"hk3gtl.config.phone.app_order.comment"})
    public String[] appOrder = {"inbox", "letters", "ae", "updates", "settings", "quiet"};
    @Configurable @Configurable.DecimalRange(min = -1.0, max = 1.0) @Configurable.Comment({"hk3gtl.config.phone.gaze_x.comment"})
    public double gazeX = -1.0;
    @Configurable @Configurable.DecimalRange(min = -1.0, max = 1.0) @Configurable.Comment({"hk3gtl.config.phone.gaze_y.comment"})
    public double gazeY = -1.0;
    @Configurable @Configurable.DecimalRange(min = 0.6, max = 1.5) @Configurable.Comment({"hk3gtl.config.phone.gaze_scale.comment"})
    public double gazeScale = 1.0;

    public void apply() {
        Hk3PhoneConfig.RIGHT.set(rightSide);
        Hk3PhoneConfig.MARGIN.set(horizontalMargin);
        Hk3PhoneConfig.TOP.set(top);
        Hk3PhoneConfig.SCALE.set(scale);
        Hk3PhoneConfig.PHONE_SIZE.set(phoneSize);
        Hk3PhoneConfig.SOUND.set(sound);
        Hk3PhoneConfig.CHATTER.set(chatter);
        Hk3PhoneConfig.DO_NOT_DISTURB.set(doNotDisturb);
        Hk3PhoneConfig.POSITION_X.set(positionX);
        Hk3PhoneConfig.POSITION_Y.set(positionY);
        Hk3PhoneConfig.APP_ORDER.set(java.util.Arrays.asList(appOrder));
        Hk3PhoneConfig.GAZE_X.set(gazeX);
        Hk3PhoneConfig.GAZE_Y.set(gazeY);
        Hk3PhoneConfig.GAZE_SCALE.set(gazeScale);
        Hk3PhoneConfig.SPEC.save();
    }
}
