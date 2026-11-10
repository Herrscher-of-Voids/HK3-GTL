package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallPattern;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;

/** W01按负责人指定原作建筑接入；运行档WSV不改，本轮只注册结构、无接口与配方。 */
/** 【变更记录 #1】2026-10-29 23:12:35（第1次备注 · 本轮高度与预览修复）：删除W01禁用JEI预览的设置；新增原生分类稀疏完整预览入口；修改XEI预览为开启；用途为游戏内查看原建筑全部实体，世界投影渲染仍由原独立设置控制。 */
public final class Hk3W01Machines {
    public static MultiblockMachineDefinition HALL;
    private Hk3W01Machines() {}
    public static void init() {
        HALL = Hk3Gtl.REGISTRATE.multiblock("w01_origin_stellar_concert_court", Hk3W01HallMachine::new)
                .tier(Hk3Tiers.WSV).rotationState(RotationState.NON_Y_AXIS)
                .allowFlip(false).allowExtendedFacing(false)
                .appearanceBlock(() -> Blocks.SMOOTH_QUARTZ)
                .pattern(Hk3W01HallPattern::new)
                .multiblockPreviewRenderer(false, true)
                .workableCasingRenderer(new ResourceLocation("hk3gtl", "block/casings/industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/w01_hall"))
                .tooltips(Component.translatable("hk3gtl.w01.structure_only"), Component.translatable("hk3gtl.w01.sparse"))
                .register();
    }
}
