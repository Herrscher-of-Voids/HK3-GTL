package com.sirin.hk3gtl.mixin.client;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.platform.TextureUtil;
import com.mojang.logging.LogUtils;
import net.minecraft.client.renderer.texture.TextureAtlas;
import org.slf4j.Logger;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

import java.io.IOException;
import java.nio.file.Path;

@Mixin(TextureAtlas.class)
public abstract class Hk3AtlasDumpMixin {
    @Unique
    private static final int HK3GTL_MAX_DUMP_SIZE = 4096;
    @Unique
    private static final Logger HK3GTL_LOGGER = LogUtils.getLogger();

    @Redirect(method = "dumpContents(Lnet/minecraft/resources/ResourceLocation;Ljava/nio/file/Path;)V",
            at = @At(value = "INVOKE", target = "Lcom/mojang/blaze3d/platform/TextureUtil;writeAsPNG(Ljava/nio/file/Path;Ljava/lang/String;IIII)V"))
    private void hk3gtl$dumpAtlas(Path directory, String name, int textureId, int mipLevel, int width, int height) {
        if (Math.max(width, height) <= HK3GTL_MAX_DUMP_SIZE) {
            TextureUtil.writeAsPNG(directory, name, textureId, mipLevel, width, height);
            return;
        }
        int firstLevel = 0;
        while (firstLevel <= mipLevel && Math.max(width >> firstLevel, height >> firstLevel) > HK3GTL_MAX_DUMP_SIZE) {
            firstLevel++;
        }
        if (firstLevel > mipLevel) {
            HK3GTL_LOGGER.warn("纹理图集 {} 为 {}×{}，现有 mip 无法限制到 {} 像素，跳过图像导出", name, width, height, HK3GTL_MAX_DUMP_SIZE);
            return;
        }
        GlStateManager._bindTexture(textureId);
        for (int level = firstLevel; level <= mipLevel; level++) {
            Path path = directory.resolve(name + "_" + level + ".png");
            try (NativeImage image = new NativeImage(width >> level, height >> level, false)) {
                image.downloadTexture(level, false);
                image.writeToFile(path);
                HK3GTL_LOGGER.debug("纹理图集已导出到 {}", path.toAbsolutePath());
            } catch (IOException exception) {
                HK3GTL_LOGGER.debug("无法导出纹理图集 {}", path.toAbsolutePath(), exception);
            }
        }
    }
}
