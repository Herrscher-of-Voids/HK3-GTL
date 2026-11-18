package com.sirin.hk3gtl.client.preview;

import com.lowdragmc.lowdraglib.client.scene.WorldSceneRenderer;
import com.mojang.blaze3d.vertex.VertexBuffer;
import com.sirin.hk3gtl.mixin.gtceu.Hk3PreviewCacheAccessor;
import com.sirin.hk3gtl.mixin.gtceu.Hk3PreviewVertexBufferAccessor;
import net.minecraftforge.fml.ModList;

import java.lang.reflect.Field;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

public final class Hk3PreviewCacheBridge {
    private static final boolean GTL_CACHE = ModList.get().isLoaded("gtlcore");

    private Hk3PreviewCacheBridge() {}

    public static boolean isReady(WorldSceneRenderer renderer) {
        AtomicReference<?> state = GTL_CACHE ? GtlCache.read(GtlCache.STATE, renderer)
                : ((Hk3PreviewCacheAccessor) renderer).hk3gtl$cacheState();
        if (!"COMPILED".equals(String.valueOf(state.get()))) return false;
        if (GTL_CACHE) {
            // COMPILED仅表示CPU网格完成，全部渲染层仍须转交并上传到VBO。
            List<List<?>> pending = GtlCache.read(GtlCache.PENDING, renderer);
            for (var batch : pending) if (!batch.isEmpty()) return false;
            List<List<VertexBuffer>> batches = GtlCache.read(GtlCache.BUFFERS, renderer);
            boolean uploaded = false;
            for (var batch : batches) {
                for (var buffer : batch) {
                    if (buffer.getFormat() == null) return false;
                    uploaded = true;
                }
            }
            return uploaded;
        }
        for (var buffer : ((Hk3PreviewCacheAccessor) renderer).hk3gtl$vertexBuffers())
            if (buffer.getFormat() == null) return false;
        return true;
    }

    public static long cacheBytes(WorldSceneRenderer renderer) {
        long bytes = 0;
        if (GTL_CACHE) {
            List<List<VertexBuffer>> batches = GtlCache.read(GtlCache.BUFFERS, renderer);
            for (var batch : batches)
                for (var buffer : batch) bytes += bufferBytes(buffer);
        } else {
            for (var buffer : ((Hk3PreviewCacheAccessor) renderer).hk3gtl$vertexBuffers())
                bytes += bufferBytes(buffer);
        }
        return bytes;
    }

    private static long bufferBytes(VertexBuffer buffer) {
        if (buffer == null || buffer.getFormat() == null) return 0;
        long indices = ((Hk3PreviewVertexBufferAccessor) buffer).hk3gtl$indexCount();
        return indices / 6 * 4 * buffer.getFormat().getVertexSize() + indices * 4;
    }

    private static final class GtlCache {
        private static final Field STATE = field("gTLCore$cacheState");
        private static final Field PENDING = field("gTLCore$compiledBufferData");
        private static final Field BUFFERS = field("gTLCore$vertexBufferBatches");

        private static Field field(String name) {
            try {
                var field = WorldSceneRenderer.class.getDeclaredField(name);
                field.setAccessible(true);
                return field;
            } catch (NoSuchFieldException failure) { throw new ExceptionInInitializerError(failure); }
        }

        @SuppressWarnings("unchecked")
        private static <T> T read(Field field, WorldSceneRenderer renderer) {
            try { return (T) field.get(renderer); }
            catch (IllegalAccessException failure) { throw new IllegalStateException(failure); }
        }
    }
}
