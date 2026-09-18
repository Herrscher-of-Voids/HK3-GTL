package com.sirin.hk3gtl.mixin;



import com.mojang.blaze3d.shaders.Shader;
import committee.nova.mods.avaritia.api.client.shader.CCUniform;
import committee.nova.mods.avaritia.api.client.shader.UniformType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.gen.Invoker;

@Pseudo
@Mixin(value = CCUniform.class, remap = false)
public interface AvaritiaCCUniformInvoker {

    @Invoker("makeUniform")
    static CCUniform hk3gtl$makeUniform(String name, UniformType type, int count, Shader shader) {
        throw new AssertionError();
    }
}
