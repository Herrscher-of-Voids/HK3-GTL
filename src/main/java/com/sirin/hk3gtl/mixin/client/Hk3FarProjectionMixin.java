package com.sirin.hk3gtl.mixin.client;

import com.sirin.hk3gtl.common.farview.Hk3FarViewConfig;
import net.minecraft.client.renderer.GameRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 统一原版与巨构远景的深度映射，仅延长裁切面，不改变加载和模拟距离。 */
@Mixin(GameRenderer.class)
public abstract class Hk3FarProjectionMixin {
    @Inject(method="getDepthFar",at=@At("RETURN"),cancellable=true)
    private void hk3gtl$depth(CallbackInfoReturnable<Float> callback) {
        if(Hk3FarViewConfig.ENABLED.get())callback.setReturnValue(Math.max(callback.getReturnValueF(),Hk3FarViewConfig.DISTANCE.get()+128f));
    }
}
