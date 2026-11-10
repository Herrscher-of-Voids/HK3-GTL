package com.sirin.hk3gtl.common.recipe;



import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.common.data.GTSoundEntries;

import static com.lowdragmc.lowdraglib.gui.texture.ProgressTexture.FillDirection.LEFT_TO_RIGHT;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-24 16:36:00（内测5修订66）
 * 删除：液态各设备共用全工艺类型的关联。新增：稳定、再生、调配、校准与浓缩专用类型。
 * 修改：保留原精炼ID供离心分离工艺使用；用途：存档标识不变并落实设备分工。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：在既有注册生命周期接入独立工艺类型。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public final class Hk3IndustrialRecipeTypes {
    private Hk3IndustrialRecipeTypes() {}

    /** 初始采样与采集塔工艺：探测器/编程电路为催化输入，输出液体或中间样本。 */
    public static final GTRecipeType COLLECTION = GTRecipeTypes.register(
            "industrial_honkai_collection", "multiblock")
            .setMaxIOSize(6, 4, 2, 3)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /** 原精炼ID保留，现在只由离心分离中心执行分离与净化。 */
    public static final GTRecipeType LIQUID_REFINING = GTRecipeTypes.register(
            "industrial_liquid_honkai_refining", "multiblock")
            .setMaxIOSize(8, 6, 4, 4)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /** 初始光谱实验与后续探测器校准。 */
    public static final GTRecipeType SPECTRUM_ANALYSIS = GTRecipeTypes.register(
            "industrial_honkai_spectrum_analysis", "multiblock")
            .setMaxIOSize(6, 4, 2, 2)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /** 液态崩坏能向文明能源网络的正式注入入口。 */
    public static final GTRecipeType NETWORK_INJECTION = GTRecipeTypes.register(
            "industrial_honkai_network_injection", "multiblock")
            .setMaxIOSize(8, 4, 4, 2)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    public static final GTRecipeType STABILIZATION = GTRecipeTypes.register("industrial_honkai_stabilization", "multiblock")
            .setMaxIOSize(8, 6, 4, 4).setEUIO(IO.IN).setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT).setSound(GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType REGENERATION = GTRecipeTypes.register("industrial_medium_regeneration", "multiblock")
            .setMaxIOSize(8, 6, 4, 4).setEUIO(IO.IN).setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT).setSound(GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType FUEL_BLENDING = GTRecipeTypes.register("industrial_fuel_blending", "multiblock")
            .setMaxIOSize(8, 6, 4, 4).setEUIO(IO.IN).setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT).setSound(GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType CALIBRATION = GTRecipeTypes.register("industrial_detector_calibration", "multiblock")
            .setMaxIOSize(8, 4, 0, 0).setEUIO(IO.IN).setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT).setSound(GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType CORE_CRYSTALLIZATION = GTRecipeTypes.register("industrial_core_crystallization", "multiblock")
            .setMaxIOSize(8, 4, 4, 4).setEUIO(IO.IN).setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT).setSound(GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType CONCENTRATION = GTRecipeTypes.register("industrial_fuel_concentration", "multiblock")
            .setMaxIOSize(8, 6, 4, 4).setEUIO(IO.IN).setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT).setSound(GTSoundEntries.ELECTROLYZER);

    /** 注册入口由数据生成阶段调用；字段初始化即完成 GT 注册。 */
    public static void init() {
        Hk3ResearchProcessTypes.init();
        // 静态字段注册，保留显式入口便于启动健康检查与未来分阶段迁移。
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
