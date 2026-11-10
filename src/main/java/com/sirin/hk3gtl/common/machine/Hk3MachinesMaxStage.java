package com.sirin.hk3gtl.common.machine;

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;


/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import com.gregtechceu.gtceu.api.GTValues;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-24 16:37:18（内测5修订66）
 * 删除：注入器通用中型盒形Pattern。新增：独立谐振线圈与输运管路布局。
 * 修改：仅允许水平朝向；用途：保持原注册ID并落实液态线终端结构。
 *
 * 【变更记录 #2】2026-09-24 18:56:36（内测5修订67）
 * 修改：网络注入器显式声明 MAX 控制器等级，与液态工业线的结构材料和配方电压一致。
 */
/**
 * 【变更记录 #3】2026-10-01 21:41:57（第3次备注 · 内测5修订151）
 * 删除：内测1—4旧结构相关入口。新增：无替代结构。
 * 修改：删除旧注册与字段；仅调用仍有内测5机器的初始化模块。
 * 用途：落实旧结构全部退役；内测5未审批设备仍待接入，不保留空注册兼容。
 */
public class Hk3MachinesMaxStage {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    public static MultiblockMachineDefinition HONKAI_NETWORK_INJECTOR;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {






        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        HONKAI_NETWORK_INJECTOR = reg()
                .multiblock("honkai_network_injector", com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiNetworkInjectorMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3IndustrialRecipeTypes.NETWORK_INJECTION)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLinePatterns.create(def,
                        com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLineLayout.Kind.INJECTION))
                .workableCasingRenderer(tex("industrial_controller_shell"), OVERLAY)
                .tooltips(
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.honkai_network_injector.tooltip.0"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.honkai_network_injector.tooltip.1"),
                        net.minecraft.network.chat.Component.translatable("hk3gtl.machine.honkai_network_injector.tooltip.2"))
                .register();



        LOGGER.info("[HK3GTL] machine registration completed");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
