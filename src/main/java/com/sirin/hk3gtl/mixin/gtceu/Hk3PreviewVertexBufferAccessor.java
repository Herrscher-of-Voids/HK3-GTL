package com.sirin.hk3gtl.mixin.gtceu;

import com.mojang.blaze3d.vertex.VertexBuffer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** 读取预览四边形缓存的索引数，用于限制离屏显存保留。 */
@Mixin(VertexBuffer.class)
public interface Hk3PreviewVertexBufferAccessor {
    @Accessor("indexCount") int hk3gtl$indexCount();
}
