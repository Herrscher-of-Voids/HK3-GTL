package com.sirin.hk3gtl.common.dimension.height;

import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.storage.PrimaryLevelData;
import net.minecraftforge.common.ForgeConfigSpec;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.config.ModConfig;

import java.util.List;

/** 高度合同配置与旧世界扩高名单。 */
public final class Hk3HeightConfig {
    public enum NewWorldMode { DISABLED, ISOLATED_TEST_ONLY, ALL_NEW_WORLDS }
    public static final String TEST_PREFIX = "hk3gtl-height-r166";
    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.EnumValue<NewWorldMode> MODE;
    public static final ForgeConfigSpec.IntValue TOP_EXCLUSIVE;
    public static final ForgeConfigSpec.ConfigValue<List<? extends String>> EXISTING_WORLDS;
    static {
        var builder = new ForgeConfigSpec.Builder();
        MODE = builder.translation("hk3gtl.height.config.mode")
            .comment("决定新建世界的启用范围；默认全部新世界。已有高度合同按当前topExclusive向上迁移。")
            .defineEnum("newWorldMode", NewWorldMode.ALL_NEW_WORLDS);
        TOP_EXCLUSIVE = builder.translation("hk3gtl.height.config.top")
            .comment("新建世界和已有合同的最高可建Y加1；默认2032，允许528至2032，必须16对齐。已有合同只允许向上迁移。")
            .defineInRange("topExclusive", 2032, 528, 2032);
        EXISTING_WORLDS = builder.translation("hk3gtl.height.config.existing")
            .comment("允许下次完整重开时启用高度合同的无合同旧档文件夹名；精确匹配，不填路径或通配符。已有合同按topExclusive自动向上迁移。")
            .defineListAllowEmpty("existingWorlds", List.of(), value -> value instanceof String name
                && Hk3HeightWorldUpgrade.validFolderName(name));
        SPEC = builder.build();
    }
    private Hk3HeightConfig() {}
    public static void register() {
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, SPEC, "hk3gtl-height-common.toml");
    }
    public static boolean shouldEnable(LevelSettings settings, PrimaryLevelData.SpecialWorldProperty property) {
        return switch (MODE.get()) {
            case DISABLED -> false;
            case ALL_NEW_WORLDS -> true;
            case ISOLATED_TEST_ONLY -> property == PrimaryLevelData.SpecialWorldProperty.FLAT
                && settings.gameType() == GameType.CREATIVE && settings.allowCommands()
                && settings.levelName().startsWith(TEST_PREFIX);
        };
    }
}
