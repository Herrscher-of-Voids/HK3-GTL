package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiController;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import net.minecraft.world.entity.player.Player;
import org.gtlcore.gtlcore.common.item.UltimateTerminalBehavior;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 在终端转换Pattern之前分流，避免巨构占位Pattern及增强版拆除队列吞掉真实建筑。 */
@Mixin(value = UltimateTerminalBehavior.class, remap = false, priority = 2000)
public abstract class Hk3TerminalDismantleMixin {
    @Inject(method = "dismantleMultiblock", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$dismantle(IMultiController controller, Player player,
            UltimateTerminalBehavior.AutoBuildSetting settings, CallbackInfo callback) {
        if ("hk3gtl".equals(controller.self().getDefinition().getId().getNamespace())) {
            Hk3UniversalTerminalBuilder.use(player, controller.getMultiblockState(), settings);
            callback.cancel();
        }
    }
}
