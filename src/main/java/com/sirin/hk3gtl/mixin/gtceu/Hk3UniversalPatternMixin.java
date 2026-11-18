package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3MultiblockLoading;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * 保留HK3自动建造入口，将GT结构匹配转入分批世界读取。
 */
@Mixin(value = BlockPattern.class, remap = false)
public abstract class Hk3UniversalPatternMixin {
    @Inject(method="checkPatternAt(Lcom/gregtechceu/gtceu/api/pattern/MultiblockState;Z)Z",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$batchWorldReads(MultiblockState state,boolean savePredicate,CallbackInfoReturnable<Boolean> callback){
        if(Hk3MultiblockLoading.intercept(state))callback.setReturnValue(false);
    }

    @Inject(method = "autoBuild", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$useUniversalBuilder(Player player, MultiblockState state, CallbackInfo callback) {
        if (state.getController() != null
                && "hk3gtl".equals(state.getController().self().getDefinition().getId().getNamespace())) {
            Hk3UniversalTerminalBuilder.use(player, state, null);
            callback.cancel();
        }
    }
}
