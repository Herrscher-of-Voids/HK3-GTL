package com.sirin.hk3gtl.common.entity;


/**
 * 【文件职责】
 * - 维护 Hk3Entities 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * 实体注册中心 —— 使用 DeferredRegister 注册所有自定义实体类型。
 *
 * <h3>当前实体</h3>
 * 仅有终局唯一实体：空之律者·西琳（VOID_QUEEN_SIRIN）。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增实体：仿照 VOID_QUEEN_SIRIN 的模式添加 RegistryObject</li>
 *   <li>ENTITY_TYPES 需在模组构造时通过 register(modBus) 注册到事件总线</li>
 *   <li>新增实体后需同步注册渲染器（见 Hk3ClientSetup.onRegisterRenderers）</li>
 *   <li>碰撞箱大小通过 .sized(width, height) 设置</li>
 *   <li>clientTrackingRange 控制客户端接收实体更新的最大距离（chunk 为单位）</li>
 * </ul>
 */
/** 【变更记录 #1】2026-10-01 19:03:37（修订141）：删除：无；新增／修改：注册不保存的独立琪亚娜实体；用途：琪亚娜二审形象和终审统一称谓，保留其他会话行为。 */
public class Hk3Entities {

    /** 实体类型延迟注册器，命名空间为 hk3gtl */
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Hk3Constants.MOD_ID);

    /**
     * 空之律者·西琳实体类型。
     * 碰撞箱 0.6x1.8（玩家大小），追踪距离 64 chunk，免疫火焰。
     * 分类为 MISC（不计入生物上限）。
     */
    public static final RegistryObject<EntityType<VoidQueenSirinEntity>> VOID_QUEEN_SIRIN =
            ENTITY_TYPES.register("void_queen_sirin", () ->
                    EntityType.Builder.of(VoidQueenSirinEntity::new, MobCategory.MISC)
                            .sized(0.6F, 1.8F)
                            .clientTrackingRange(64)
                            .fireImmune()
                            .build("void_queen_sirin"));

    public static final RegistryObject<EntityType<Hk3KianaReviewEntity>> KIANA_REVIEW =
            ENTITY_TYPES.register("kiana_review", () ->
                    EntityType.Builder.<Hk3KianaReviewEntity>of(Hk3KianaReviewEntity::new, MobCategory.MISC)
                            .sized(0.6F, 1.8F).clientTrackingRange(10).updateInterval(3)
                            .fireImmune().noSave().build("kiana_review"));

    /** 虚数裂隙交互点（无模型，粒子由实体 tick 发出）。 */
    public static final RegistryObject<EntityType<ImaginaryRiftEntity>> IMAGINARY_RIFT =
            ENTITY_TYPES.register("imaginary_rift", () ->
                    EntityType.Builder.of(ImaginaryRiftEntity::new, MobCategory.MISC)
                            .sized(1.2F, 2.0F)
                            .clientTrackingRange(64)
                            .fireImmune()
                            .build("imaginary_rift"));
}
