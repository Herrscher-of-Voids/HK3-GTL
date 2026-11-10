package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiController;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import net.minecraft.world.entity.player.Player;
import org.gtlcore.gtlcore.api.pattern.AdvancedBlockPattern;
import org.gtlcore.gtlcore.common.item.UltimateTerminalBehavior;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 【文件职责】接管HK3GTL高级Pattern建造与拆除；真实终端入口在转换Pattern前另行分流。
 * 【变更记录 #1】2026-10-30 01:36:10（修订184）
 * - 修改：由仅分流W01改为统一分流全部HK3GTL控制器；其他模组仍走GTLCore原路径。
 * - 用途：保留AutoBuildSetting传入统一层，并只在有活动建造任务时接管拆解入口。
 * 【变更记录 #2】2026-10-30：拆除转入统一任务；高于增强版默认1000优先级，避免占位Pattern进入旧拆除队列。
 */
@Mixin(value = AdvancedBlockPattern.class, remap = false, priority = 2000)
public abstract class Hk3W01TerminalMixin {
    @Inject(method = "autoBuild", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$buildW01(Player player, MultiblockState state,
            UltimateTerminalBehavior.AutoBuildSetting settings, CallbackInfo callback) {
        if (state.getController() != null && "hk3gtl".equals(state.getController().self().getDefinition().getId().getNamespace())) {
            Hk3UniversalTerminalBuilder.use(player, state, settings);
            callback.cancel();
        }
    }

    @Inject(method = "dismantleMultiblock", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$routeDismantle(IMultiController controller, Player player,
            UltimateTerminalBehavior.AutoBuildSetting settings, CallbackInfo callback) {
        if ("hk3gtl".equals(controller.self().getDefinition().getId().getNamespace())) {
            Hk3UniversalTerminalBuilder.use(player,controller.getMultiblockState(),settings);
            callback.cancel();
        }
    }
}
