package com.sirin.hk3gtl.mixin;



import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Re-Avaritia 着色器注册阻断 Mixin。
 *
 * <p><b>目标类</b>：{@code committee.nova.mods.avaritia.client.AvaritiaClient}
 * （Re-Avaritia 客户端主类，负责注册无尽合金/宇宙材质所需的着色器程序）。
 *
 * <p><b>注入目的</b>：在开发环境（deobf/dev）下，Re-Avaritia 的着色器会尝试把
 * {@code Uniform} 当作 {@code CCUniform} 使用，触发 {@code ClassCastException}，
 * 导致 RenderSystem 初始化失败，进而整个客户端白屏/崩溃。
 * 因为项目目前用不到 Avaritia 的花哨着色器，直接整体取消其着色器注册最安全。
 *
 * <p><b>失效后影响</b>：
 * <ul>
 *   <li>开发环境启动即崩（ClassCastException on Uniform → CCUniform）。</li>
 *   <li>发布到正式环境若 Re-Avaritia 修复了此问题，可以考虑移除本 Mixin，
 *       但移除前必须在 dev 环境验证不再闪退。</li>
 * </ul>
 *
 * <p><b>修改指南</b>：
 * <ul>
 *   <li>本 Mixin 使用 {@link Pseudo}，仅在 Re-Avaritia 存在时生效；{@code require = 0}
 *       允许目标方法不存在时静默放行，避免未装 Avaritia 时崩溃。</li>
 *   <li>如果 Re-Avaritia 后续把 {@code onRegisterShaders} 改名，需要同步修改此处 method 名。</li>
 *   <li>如果将来需要启用 Avaritia 的宇宙渲染，请删除本 Mixin 并同时处理
 *       {@link CosmicBakeModelMixin}。</li>
 *   <li>{@code remap = false} 是强制的，因为目标是第三方模组类，不能走 Mojang 映射。</li>
 * </ul>
 */
@Pseudo
@Mixin(targets = "committee.nova.mods.avaritia.client.AvaritiaClient", remap = false)
public class AvaritiaShaderMixin {

    /**
     * Hook 位置：{@code AvaritiaClient#onRegisterShaders}（着色器注册回调）。
     * <br>Hook 时机：{@code @At("HEAD")} —— 方法入口处立即取消。
     * <br>效果：{@code ci.cancel()} 直接阻止原方法执行，跳过所有 {@code ShaderInstance} 的
     * 注册（宇宙、无尽、彩虹等），从根源避免后续 Uniform 类型不匹配问题。
     */
    @Inject(method = "onRegisterShaders", at = @At("HEAD"), cancellable = true, require = 0)
    private static void hk3gtl$cancelShaderRegistration(CallbackInfo ci) {
        ci.cancel();
    }
}
