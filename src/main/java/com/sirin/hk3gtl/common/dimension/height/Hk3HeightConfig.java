package com.sirin.hk3gtl.common.dimension.height;

import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.storage.PrimaryLevelData;
import net.minecraftforge.common.ForgeConfigSpec;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.config.ModConfig;

import java.util.List;

/**
 * 只为新建世界选择高度合同；已存在合同不受后续配置缩高影响。
 */
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
            .comment("决定新建世界的启用范围；默认全部新世界。已有合同不受此项修改影响，旧档仅按existingWorlds精确名单升级。")
            .defineEnum("newWorldMode", NewWorldMode.ALL_NEW_WORLDS);
        TOP_EXCLUSIVE = builder.translation("hk3gtl.height.config.top")
            .comment("新建世界或名单旧档首次升级的最高可建Y加1；默认2032，允许528至2032，必须16对齐。合同创建后冻结，此项不改变已有合同。")
            .defineInRange("topExclusive", 2032, 528, 2032);
        EXISTING_WORLDS = builder.translation("hk3gtl.height.config.existing")
            .comment("允许下次完整重开时升级的无合同旧档文件夹名；精确匹配，不填路径或通配符。升级前校验备份level.dat及level.dat_old；失败则拒绝启动。已有合同不再升级，移出名单也不会缩高。")
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
