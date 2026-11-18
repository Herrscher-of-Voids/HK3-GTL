package com.sirin.hk3gtl.mixin.height;

import com.sirin.hk3gtl.common.dimension.height.Hk3HeightService;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.progress.ChunkProgressListener;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 在服务器首个Level构造、Radium缓存与区段分配之前应用世界合同。
 */
@Mixin(MinecraftServer.class)
public abstract class Hk3MinecraftServerHeightMixin {
    @Inject(method="createLevels", at=@At("HEAD"))
    private void hk3gtl$applyHeight(ChunkProgressListener listener, CallbackInfo ci) {
        Hk3HeightService.applyBeforeLevels((MinecraftServer)(Object)this);
    }
}
