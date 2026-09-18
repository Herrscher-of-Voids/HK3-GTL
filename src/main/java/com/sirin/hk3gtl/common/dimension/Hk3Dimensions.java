package com.sirin.hk3gtl.common.dimension;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.util.Mth;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.dimension.DimensionType;

/**
 * 虚数维度资源键常量定义。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>集中声明虚数维度 (hk3gtl:imaginary_dimension) 的 ResourceKey，
 *       供传送命令、BOSS 战逻辑、平台生成等模块引用</li>
 *   <li>提供虚数平台的几何/出生点常量，避免散落在多处的魔法数字</li>
 * </ul>
 *
 * <h3>维度数据位置</h3>
 * <ul>
 *   <li>维度 JSON：data/hk3gtl/dimension/imaginary_dimension.json</li>
 *   <li>维度类型 JSON：data/hk3gtl/dimension_type/imaginary_dimension.json</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>修改维度 ID：需同步修改 JSON 文件名、维度类型文件名、语言键及所有引用此常量的代码</li>
 *   <li>调整平台高度 / 半径：PLATFORM_Y / PLATFORM_HALF 变化会影响平台生成逻辑和玩家传送坐标
 *       （SPAWN_Y 以 PLATFORM_Y 派生，保持一致）</li>
 *   <li>调整出生点 SPAWN_Z：负值表示站在平台南侧边缘，朝向北侧 BOSS；改变会影响战斗视角与体验</li>
 *   <li>新增维度：建议在本类中追加新的 ResourceKey 常量，避免在其它模块硬编码字符串</li>
 * </ul>
 */
public class Hk3Dimensions {

    /**
     * 虚数维度的 Level ResourceKey。
     * 用于 server.getLevel(IMAGINARY)、传送、维度判断。
     * 修改影响：若改动命名空间或路径，所有相关数据包 JSON 与引用均需同步修改。
     */
    public static final ResourceKey<Level> IMAGINARY =
            ResourceKey.create(Registries.DIMENSION,
                    new ResourceLocation(Hk3Constants.MOD_ID, "imaginary_dimension"));

    /**
     * 虚数维度的 DimensionType ResourceKey。
     * 对应 data/hk3gtl/dimension_type/imaginary_dimension.json。
     * 修改影响：控制时间长度、光照、是否自然生成、方块高度上限等基础物理。
     */
    public static final ResourceKey<DimensionType> IMAGINARY_TYPE =
            ResourceKey.create(Registries.DIMENSION_TYPE,
                    new ResourceLocation(Hk3Constants.MOD_ID, "imaginary_dimension"));

    /**
     * 平台中心的 Y 坐标。
     * 修改影响：改变会同时挪动整个平台、出生点高度（SPAWN_Y = PLATFORM_Y + 1）与 BOSS 生成位置。
     */
    public static final int PLATFORM_Y = 100;

    /**
     * 平台半径（当前为 5，生成 11x11 的方形平台：2*5+1）。
     * 修改影响：会改变平台实体大小，需同步检查 BOSS 战 AI 活动区域与玩家坠落保护逻辑。
     */
    public static final int PLATFORM_HALF = 5;

    /** 玩家传送到虚数维度时的 X 坐标（平台中心对齐） */
    public static final int SPAWN_X = 0;

    /**
     * 玩家传送时的 Y 坐标（站在平台上方一格避免卡方块）。
     * 与 PLATFORM_Y 保持 +1 关系，修改平台高度时自动跟随。
     */
    public static final int SPAWN_Y = PLATFORM_Y + 1;

    /**
     * 玩家传送时的 Z 坐标（负值 = 站在平台南侧边缘，面向北方 BOSS）。
     * 修改影响：改变玩家入场朝向与距离，直接影响战斗手感。
     */
    public static final int SPAWN_Z = -4;

    /**
     * 西琳在平台中心 (0.5, 0.5) 面向南侧玩家出生点的 yRot。
     * PlayerModel 正面朝向由 yaw 决定：让西琳从平台中心看向玩家出生点。
     * yaw 语义：0=+Z(南)、90=-X(西)、180=-Z(北)、270=+X(东)。
     * 玩家在 SPAWN_Z(=-4) 的北侧，故西琳应朝 -Z，即 yaw≈180，直接用视线角，无需 +180 补偿。
     */
    public static float sirinFacePlayerYaw() {
        double dx = (SPAWN_X + 0.5D) - 0.5D;
        double dz = (SPAWN_Z + 0.5D) - 0.5D;
        // Minecraft yaw = -atan2(dx, dz) 的等价式：atan2(dz,dx) 再修正到 yaw 语义。
        float lookAt = (float) (Mth.atan2(dz, dx) * (180.0 / Math.PI)) - 90.0F;
        return Mth.wrapDegrees(lookAt);
    }
}
