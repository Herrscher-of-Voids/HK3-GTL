package com.sirin.hk3gtl.mixin;


/**
 * 【文件职责】
 * - 处理 AvaritiaCCUniformInvoker 的 Mixin 注入逻辑。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
