package com.sirin.hk3gtl.common.material;


/**
 * 【文件职责】
 * - 维护 Hk3Materials 的核心功能实现。
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
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;
import com.gregtechceu.gtceu.api.data.chemical.material.Material;
import com.gregtechceu.gtceu.api.data.chemical.material.info.MaterialIconSet;
import net.minecraft.resources.ResourceLocation;
import com.sirin.hk3gtl.common.constants.Hk3Constants;

/**
 * GT 化学材料注册总入口。
 *
 * <h3>职责</h3>
 * 在 {@code MaterialEvent} 阶段调用 {@link #register()}，
 * 注册所有 HK3GTL 自定义 GT 材料（魂钢、液态崩坏能等）。
 *
 * <h3>注册流程</h3>
 * <ol>
 *   <li>{@link SouliumMaterial#register()} — 注册魂钢及其全部派生形态（锭/板/杆/细丝等）</li>
 *   <li>液态崩坏能（{@link #LIQUID_HONKAI_ENERGY}）— 紫色流体，用于海渊电路等配方</li>
 * </ol>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增材料 → 在本类 {@link #register()} 末尾追加，或创建新的子材料类</li>
 *   <li>引用本模组材料：{@code SouliumMaterial.SOULIUM} / {@code Hk3Materials.LIQUID_HONKAI_ENERGY}</li>
 * </ul>
 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
public class Hk3Materials {

    private static final Logger LOGGER = LogUtils.getLogger();

    /**
     * 注册所有 HK3GTL GT 材料。由 {@code Hk3GtAddon} 在 MaterialEvent 中调用。
     */
    public static void register() {
        LOGGER.info("[HK3GTL] 开始注册魂钢材料...");
        com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids.register();
        SouliumMaterial.register();
        LOGGER.info("[HK3GTL] 魂钢材料注册完成。");

        LIQUID_HONKAI_ENERGY = new Material.Builder(
                new ResourceLocation(Hk3Constants.MOD_ID, "liquid_honkai_energy"))
                .fluid(com.gregtechceu.gtceu.api.fluids.store.FluidStorageKeys.LIQUID,
                        new com.gregtechceu.gtceu.api.fluids.FluidBuilder().textures(true, true))
                .color(0x7B2FBE)
                .iconSet(MaterialIconSet.FLUID)
                .buildAndRegister();

    }

    /** 液态崩坏能，紫色流体（0x7B2FBE），用于海渊电路和高级配方中的流体输入 */
    public static Material LIQUID_HONKAI_ENERGY;

}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
