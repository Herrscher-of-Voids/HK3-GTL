package com.sirin.hk3gtl.common.config;

import dev.toma.configuration.Configuration;
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
        importHeight = Files.notExists(Path.of("config/hk3gtl-height.json"));
        importFarView = Files.notExists(Path.of("config/hk3gtl-farview.json"));
        importPhone = Files.notExists(Path.of("config/hk3gtl-phone.json"));
        RESEARCH = Configuration.registerConfig(Hk3ResearchSettings.class, ConfigFormats.json()).getConfigInstance();
        heightHolder = Configuration.registerConfig(Hk3HeightSettings.class, ConfigFormats.json());
        farViewHolder = Configuration.registerConfig(Hk3FarViewSettings.class, ConfigFormats.json());
        phoneHolder = Configuration.registerConfig(Hk3PhoneSettings.class, ConfigFormats.json());
        HEIGHT = heightHolder.getConfigInstance();
        FAR_VIEW = farViewHolder.getConfigInstance();
        PHONE = phoneHolder.getConfigInstance();
        modEventBus.addListener(Hk3ConfigPages::commonSetup);
    }

    private static void commonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            if (importHeight) {
                set(heightHolder, "newWorldMode", com.sirin.hk3gtl.common.dimension.height.Hk3HeightConfig.MODE.get());
                set(heightHolder, "topExclusive", com.sirin.hk3gtl.common.dimension.height.Hk3HeightConfig.TOP_EXCLUSIVE.get());
                set(heightHolder, "existingWorlds",
                        com.sirin.hk3gtl.common.dimension.height.Hk3HeightConfig.EXISTING_WORLDS.get().toArray(String[]::new));
                ConfigIO.saveClientValues(heightHolder);
            }
            HEIGHT.apply();
        });
    }

    public static void applyClientSettings() {
        if (importFarView) {
            set(farViewHolder, "enabled", com.sirin.hk3gtl.common.farview.Hk3FarViewConfig.ENABLED.get());
            set(farViewHolder, "distance", com.sirin.hk3gtl.common.farview.Hk3FarViewConfig.DISTANCE.get());
            set(farViewHolder, "gpuMiB", com.sirin.hk3gtl.common.farview.Hk3FarViewConfig.GPU_MIB.get());
            ConfigIO.saveClientValues(farViewHolder);
        }
        if (importPhone) {
            set(phoneHolder, "rightSide", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.RIGHT.get());
            set(phoneHolder, "horizontalMargin", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.MARGIN.get());
            set(phoneHolder, "top", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.TOP.get());
            set(phoneHolder, "scale", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.SCALE.get());
            set(phoneHolder, "phoneSize", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.PHONE_SIZE.get());
            set(phoneHolder, "sound", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.SOUND.get());
            set(phoneHolder, "chatter", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.CHATTER.get());
            set(phoneHolder, "doNotDisturb", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.DO_NOT_DISTURB.get());
            set(phoneHolder, "positionX", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.POSITION_X.get());
            set(phoneHolder, "positionY", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.POSITION_Y.get());
            set(phoneHolder, "appOrder", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.APP_ORDER.get().toArray(String[]::new));
            set(phoneHolder, "gazeX", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.GAZE_X.get());
            set(phoneHolder, "gazeY", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.GAZE_Y.get());
            set(phoneHolder, "gazeScale", com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.GAZE_SCALE.get());
            ConfigIO.saveClientValues(phoneHolder);
        }
        FAR_VIEW.apply();
        PHONE.apply();
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    private static void set(ConfigHolder<?> holder, String key, Object value) {
        ((dev.toma.configuration.config.value.ConfigValue) holder.getValueMap().get(key)).set(value);
    }
}
