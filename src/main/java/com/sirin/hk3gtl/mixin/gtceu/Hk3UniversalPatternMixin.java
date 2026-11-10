package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 【文件职责】将标准GT Pattern的HK3GTL构建请求转入模组分批器，其他模组不受影响。
 * 【变更记录 #1】2026-10-30 01:36:10（修订184）：新增标准Pattern自动建造入口拦截。
 */
@Mixin(value = BlockPattern.class, remap = false)
public abstract class Hk3UniversalPatternMixin {
    @Inject(method = "autoBuild", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$useUniversalBuilder(Player player, MultiblockState state, CallbackInfo callback) {
        if (state.getController() != null
                && "hk3gtl".equals(state.getController().self().getDefinition().getId().getNamespace())) {
            Hk3UniversalTerminalBuilder.use(player, state, null);
            callback.cancel();
        }
    }
}
