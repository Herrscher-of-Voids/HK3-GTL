package com.sirin.hk3gtl.mixin.gtceu;

import com.lowdragmc.lowdraglib.client.scene.WorldSceneRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

import java.util.concurrent.atomic.AtomicReference;

/** 测试页只读真实缓存状态，避免把完成后清零的进度误判成仍在编译。 */
@Mixin(value = WorldSceneRenderer.class, remap = false)
public interface Hk3PreviewCacheAccessor {
    @Accessor("cacheState") AtomicReference<?> hk3gtl$cacheState();
}
