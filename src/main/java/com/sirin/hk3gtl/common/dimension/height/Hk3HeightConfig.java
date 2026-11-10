package com.sirin.hk3gtl.common.dimension.height;

import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.storage.PrimaryLevelData;
import net.minecraftforge.common.ForgeConfigSpec;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.config.ModConfig;

import java.util.List;

/**
 * 【文件职责】只为新建世界选择高度合同；已存在合同不受后续配置缩高影响。
 * 【变更记录 #1】2026-10-17 21:19:41（第1次备注 · 修订166）
 * - 删除：无。新增：新世界模式和16对齐上界配置，默认仅隔离平坦创造作弊测试世界。
 * - 修改：不修改维度资源、已存世界或客户端物理边界；用途：服务端冻结世界级高度身份。
 */
/**
 * 【变更记录 #2】2026-10-29 23:06:53（第2次备注 · 本轮高度与预览修复）
 * - 删除：默认仅测试前缀新档启用的限制，原隔离模式仍可选。
 * - 新增：无合同旧档文件夹精确升级名单，默认空；禁止路径、通配符和空条目。
 * - 修改：默认全部新世界，目标上界仍1024；已有合同不随配置改高或缩高。
 * - 用途：落实主世界及全维度范围；旧档须显式选择并重开，由Service先备份再应用。
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
            .comment("新建世界或名单旧档首次升级的最高可建Y加1；528至2032，必须16对齐。合同创建后冻结，此项不改变已有合同。")
            .defineInRange("topExclusive", 1024, 528, 2032);
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
