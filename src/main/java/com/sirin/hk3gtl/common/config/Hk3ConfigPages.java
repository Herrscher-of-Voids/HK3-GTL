package com.sirin.hk3gtl.common.config;

import com.sirin.hk3gtl.common.dimension.height.Hk3HeightConfig;
import com.sirin.hk3gtl.common.farview.Hk3FarViewConfig;
import com.sirin.hk3gtl.common.phone.Hk3PhoneConfig;
import dev.toma.configuration.Configuration;
import dev.toma.configuration.config.Config;
import dev.toma.configuration.config.ConfigHolder;
import dev.toma.configuration.config.format.ConfigFormats;
import dev.toma.configuration.config.io.ConfigIO;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;

import java.nio.file.Files;
import java.nio.file.Path;

public final class Hk3ConfigPages {
    public static final String GROUP = "hk3gtl";
    public static Hk3ResearchSettings RESEARCH;
    public static Hk3AeSettings AE;
    public static Hk3HeightSettings HEIGHT;
    public static Hk3FarViewSettings FAR_VIEW;
    public static Hk3PhoneSettings PHONE;
    private static ConfigHolder<Hk3HeightSettings> heightHolder;
    private static ConfigHolder<Hk3FarViewSettings> farViewHolder;
    private static ConfigHolder<Hk3PhoneSettings> phoneHolder;
    private static boolean importHeight;
    private static boolean importFarView;
    private static boolean importPhone;

    private Hk3ConfigPages() {}

    public static void register(IEventBus modEventBus) {
        importHeight = missingPage(Hk3HeightSettings.class);
        importFarView = missingPage(Hk3FarViewSettings.class);
        importPhone = missingPage(Hk3PhoneSettings.class);
        RESEARCH = Configuration.registerConfig(Hk3ResearchSettings.class, ConfigFormats.json()).getConfigInstance();
        AE = Configuration.registerConfig(Hk3AeSettings.class, ConfigFormats.json()).getConfigInstance();
        heightHolder = Configuration.registerConfig(Hk3HeightSettings.class, ConfigFormats.json());
        farViewHolder = Configuration.registerConfig(Hk3FarViewSettings.class, ConfigFormats.json());
        phoneHolder = Configuration.registerConfig(Hk3PhoneSettings.class, ConfigFormats.json());
        HEIGHT = heightHolder.getConfigInstance();
        FAR_VIEW = farViewHolder.getConfigInstance();
        PHONE = phoneHolder.getConfigInstance();
        modEventBus.addListener(Hk3ConfigPages::commonSetup);
    }

    private static boolean missingPage(Class<?> page) {
        return Files.notExists(Path.of("config", page.getAnnotation(Config.class).filename() + ".json"));
    }

    private static void commonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            if (importHeight) {
                set(heightHolder, "newWorldMode", Hk3HeightConfig.MODE.get());
                set(heightHolder, "topExclusive", Hk3HeightConfig.TOP_EXCLUSIVE.get());
                set(heightHolder, "existingWorlds",
                        Hk3HeightConfig.EXISTING_WORLDS.get().toArray(String[]::new));
                ConfigIO.saveClientValues(heightHolder);
            }
            HEIGHT.apply();
        });
    }

    public static void applyClientSettings() {
        if (importFarView) {
            set(farViewHolder, "enabled", Hk3FarViewConfig.ENABLED.get());
            set(farViewHolder, "distance", Hk3FarViewConfig.DISTANCE.get());
            set(farViewHolder, "gpuMiB", Hk3FarViewConfig.GPU_MIB.get());
            ConfigIO.saveClientValues(farViewHolder);
        }
        if (importPhone) copyPhoneSettings();
        FAR_VIEW.apply();
        PHONE.apply();
    }

    public static void setFarViewEnabled(boolean enabled) {
        set(farViewHolder, "enabled", enabled);
        FAR_VIEW.apply();
        ConfigIO.saveClientValues(farViewHolder);
    }

    public static void savePhoneSettings() {
        Hk3PhoneConfig.SPEC.save();
        copyPhoneSettings();
    }

    private static void copyPhoneSettings() {
        set(phoneHolder, "rightSide", Hk3PhoneConfig.RIGHT.get());
        set(phoneHolder, "horizontalMargin", Hk3PhoneConfig.MARGIN.get());
        set(phoneHolder, "top", Hk3PhoneConfig.TOP.get());
        set(phoneHolder, "scale", Hk3PhoneConfig.SCALE.get());
        set(phoneHolder, "phoneSize", Hk3PhoneConfig.PHONE_SIZE.get());
        set(phoneHolder, "sound", Hk3PhoneConfig.SOUND.get());
        set(phoneHolder, "chatter", Hk3PhoneConfig.CHATTER.get());
        set(phoneHolder, "doNotDisturb", Hk3PhoneConfig.DO_NOT_DISTURB.get());
        set(phoneHolder, "positionX", Hk3PhoneConfig.POSITION_X.get());
        set(phoneHolder, "positionY", Hk3PhoneConfig.POSITION_Y.get());
        set(phoneHolder, "appOrder", Hk3PhoneConfig.APP_ORDER.get().toArray(String[]::new));
        set(phoneHolder, "gazeX", Hk3PhoneConfig.GAZE_X.get());
        set(phoneHolder, "gazeY", Hk3PhoneConfig.GAZE_Y.get());
        set(phoneHolder, "gazeScale", Hk3PhoneConfig.GAZE_SCALE.get());
        ConfigIO.saveClientValues(phoneHolder);
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    private static void set(ConfigHolder<?> holder, String key, Object value) {
        ((dev.toma.configuration.config.value.ConfigValue) holder.getValueMap().get(key)).set(value);
    }
}
