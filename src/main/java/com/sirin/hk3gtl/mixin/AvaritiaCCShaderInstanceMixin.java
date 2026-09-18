package com.sirin.hk3gtl.mixin;



import com.mojang.blaze3d.shaders.Uniform;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.logging.LogUtils;
import committee.nova.mods.avaritia.api.client.shader.CCShaderInstance;
import committee.nova.mods.avaritia.api.client.shader.CCUniform;
import committee.nova.mods.avaritia.api.client.shader.UniformType;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceProvider;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Overwrite;
import org.spongepowered.asm.mixin.Pseudo;
import org.slf4j.Logger;

import java.io.IOException;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 修复 Re-Avaritia 在 Forge dev 环境下把原版 Uniform 强转为 CCUniform 的崩溃。
 */
@Pseudo
@Mixin(value = CCShaderInstance.class, remap = false)
public abstract class AvaritiaCCShaderInstanceMixin extends ShaderInstance {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Set<String> HK3GTL$COSMIC_UNIFORMS = Set.of(
            "time", "yaw", "pitch", "externalScale", "opacity", "cosmicuvs");
    private static final ConcurrentHashMap<Class<?>, List<Field>> HK3GTL$CONTAINER_FIELDS = new ConcurrentHashMap<>();
    private static final Set<String> HK3GTL$WARNED_MISSING_UNIFORMS = ConcurrentHashMap.newKeySet();
    private volatile Map<String, CCUniform> hk3gtl$adaptedUniforms;

    private AvaritiaCCShaderInstanceMixin(ResourceProvider resourceProvider, ResourceLocation location, VertexFormat vertexFormat) throws IOException {
        super(resourceProvider, location, vertexFormat);
    }

    private Map<String, CCUniform> hk3gtl$getAdaptedUniforms() {
        Map<String, CCUniform> cache = this.hk3gtl$adaptedUniforms;
        if (cache == null) {
            synchronized (this) {
                cache = this.hk3gtl$adaptedUniforms;
                if (cache == null) {
                    cache = new ConcurrentHashMap<>();
                    this.hk3gtl$adaptedUniforms = cache;
                }
            }
        }
        return cache;
    }

    /**
     * @author HK3GTL
     * @reason Re-Avaritia 要求返回 CCUniform；普通 Uniform 必须保留真实元数据并进入父类上传容器。
     */
    @Overwrite
    public CCUniform getUniform(String name) {
        Map<String, CCUniform> adaptedUniforms = this.hk3gtl$getAdaptedUniforms();
        CCUniform cached = adaptedUniforms.get(name);
        if (cached != null) {
            return cached;
        }

        for (Field field : HK3GTL$CONTAINER_FIELDS.computeIfAbsent(this.getClass(),
                AvaritiaCCShaderInstanceMixin::hk3gtl$findContainerFields)) {
            try {
                Object value = field.get(this);
                if (!(value instanceof List<?> list)) continue;
                for (Object element : list) {
                    if (element instanceof CCUniform ccUniform && name.equals(ccUniform.getName())) {
                        return ccUniform;
                    }
                }
            } catch (ReflectiveOperationException | RuntimeException ignored) {
            }
        }

        Uniform vanilla = super.getUniform(name);
        if (vanilla instanceof CCUniform ccUniform) {
            return ccUniform;
        }
        if (vanilla != null) {
            UniformType type = hk3gtl$mapUniformType(vanilla);
            if (type == null) {
                hk3gtl$warnOnce(name, "Re-Avaritia 着色器不支持原版 Uniform 类型 " + vanilla.getType() + "：");
                return null;
            }

            CCUniform adapter = AvaritiaCCUniformInvoker.hk3gtl$makeUniform(
                    name, type, vanilla.getCount(), this);
            adapter.setLocation(vanilla.getLocation());
            hk3gtl$replaceUniformContainers(name, vanilla, adapter);
            adaptedUniforms.put(name, adapter);
            return adapter;
        }

        hk3gtl$warnOnce(name, "Re-Avaritia 着色器缺少 Uniform：");
        return null;
    }

    private void hk3gtl$replaceUniformContainers(String name, Uniform vanilla, CCUniform adapter) {
        for (Field field : HK3GTL$CONTAINER_FIELDS.computeIfAbsent(this.getClass(),
                AvaritiaCCShaderInstanceMixin::hk3gtl$findContainerFields)) {
            try {
                Object value = field.get(this);
                if (value instanceof List<?> list) {
                    hk3gtl$replaceListUniform(list, name, vanilla, adapter);
                } else if (value instanceof Map<?, ?> map) {
                    hk3gtl$replaceMapUniform(map, name, vanilla, adapter);
                }
            } catch (ReflectiveOperationException | RuntimeException ignored) {
            }
        }
    }

    @SuppressWarnings("unchecked")
    private static void hk3gtl$replaceListUniform(List<?> list, String name, Uniform vanilla, CCUniform adapter) {
        List<Object> mutableList = (List<Object>) list;
        for (int index = 0; index < mutableList.size(); index++) {
            Object element = mutableList.get(index);
            if (element == vanilla || element instanceof Uniform uniform && name.equals(uniform.getName())) {
                mutableList.set(index, adapter);
            }
        }
    }

    @SuppressWarnings("unchecked")
    private static void hk3gtl$replaceMapUniform(Map<?, ?> map, String name, Uniform vanilla, CCUniform adapter) {
        Object value = map.get(name);
        if (value == vanilla || value instanceof Uniform uniform && name.equals(uniform.getName())) {
            ((Map<Object, Object>) map).put(name, adapter);
        }
    }

    private static UniformType hk3gtl$mapUniformType(Uniform vanilla) {
        UniformType declaredType = switch (vanilla.getName()) {
            case "ModelViewMat", "ProjMat" -> UniformType.MAT4;
            case "ColorModulator", "FogColor" -> UniformType.VEC4;
            case "FogStart", "FogEnd", "time", "yaw", "pitch", "externalScale", "opacity" -> UniformType.FLOAT;
            case "FogShape" -> UniformType.INT;
            case "cosmicuvs" -> UniformType.MAT2;
            default -> null;
        };
        if (declaredType != null) return declaredType;

        int count = vanilla.getCount();
        int vanillaType = vanilla.getType();
        if (vanillaType == 8 && count % 4 == 0) return UniformType.MAT2;
        if (vanillaType == 9 && count % 9 == 0) return UniformType.MAT3;
        if (vanillaType == 10 && count % 16 == 0) return UniformType.MAT4;
        if (vanillaType >= 0 && vanillaType <= 3 && vanilla.getIntBuffer() != null) {
            return switch (count) {
                case 1 -> UniformType.INT;
                case 2 -> UniformType.I_VEC2;
                case 3 -> UniformType.I_VEC3;
                case 4 -> UniformType.I_VEC4;
                default -> null;
            };
        }
        if (vanilla.getFloatBuffer() == null) return null;

        return switch (count) {
            case 1 -> UniformType.FLOAT;
            case 2 -> UniformType.VEC2;
            case 3 -> UniformType.VEC3;
            case 4 -> UniformType.VEC4;
            default -> count > 4 ? UniformType.FLOAT : null;
        };
    }

    private static List<Field> hk3gtl$findContainerFields(Class<?> shaderClass) {
        List<Field> preferredFields = new ArrayList<>();
        List<Field> fallbackFields = new ArrayList<>();
        Class<?> cursor = shaderClass;
        while (cursor != null) {
            for (Field field : cursor.getDeclaredFields()) {
                if (!List.class.isAssignableFrom(field.getType()) && !Map.class.isAssignableFrom(field.getType())) continue;
                try {
                    field.setAccessible(true);
                    if ("uniforms".equals(field.getName()) || "uniformMap".equals(field.getName())) {
                        preferredFields.add(field);
                    } else {
                        fallbackFields.add(field);
                    }
                } catch (RuntimeException ignored) {
                }
            }
            cursor = cursor.getSuperclass();
        }
        preferredFields.addAll(fallbackFields);
        return List.copyOf(preferredFields);
    }

    private static void hk3gtl$warnOnce(String name, String message) {
        if (HK3GTL$COSMIC_UNIFORMS.contains(name) && HK3GTL$WARNED_MISSING_UNIFORMS.add(name)) {
            LOGGER.warn("[HK3GTL] {} {}", message, name);
        }
    }


}
