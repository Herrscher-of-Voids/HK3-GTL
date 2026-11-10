package com.sirin.hk3gtl.mixin;


/**
 * 【文件职责】
 * - 处理 CosmicBakeModelMixin 的 Mixin 注入逻辑。
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
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Re-Avaritia 宇宙材质渲染跳过 Mixin。
 *
 * <p><b>目标类</b>：{@code committee.nova.mods.avaritia.client.model.CosmicBakeModel}
 * （Re-Avaritia 自定义的烘焙模型，用于绘制无尽合金/无尽催化剂等物品的星空/宇宙动态效果）。
 *
 * <p><b>注入目的</b>：与 {@link AvaritiaShaderMixin} 配套使用。
 * 着色器被我们取消注册后，{@code CosmicBakeModel#renderItem} 里引用的
 * {@code ShaderInstance} 会是 {@code null}，调用其 uniform 时直接 NPE，
 * 导致该物品在 GUI / 手上 / 掉落物渲染时闪退。
 * 所以这里把整个宇宙渲染流程直接短路，退化成普通物品模型。
 *
 * <p><b>失效后影响</b>：
 * <ul>
 *   <li>任何包含 Avaritia 宇宙贴图的物品（无尽合金锭、催化剂等）渲染时 NPE，
 *       可能整个 Inventory / HUD / JEI 页面渲染中断。</li>
 *   <li>与 {@link AvaritiaShaderMixin} 必须同生共死，只开一个会崩。</li>
 * </ul>
 *
 * <p><b>修改指南</b>：
 * <ul>
 *   <li>如果要恢复 Avaritia 的宇宙效果，必须同时删除本 Mixin 和
 *       {@link AvaritiaShaderMixin}，并验证 dev 环境不再 ClassCast。</li>
 *   <li>{@code require = 0} 保证未装 Avaritia 时不会因为目标类缺失而崩。</li>
 *   <li>{@code remap = false} 第三方模组类必加。</li>
 * </ul>
 */
@Pseudo
@Mixin(targets = "committee.nova.mods.avaritia.client.model.CosmicBakeModel", remap = false)
public class CosmicBakeModelMixin {

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Inject(method = "renderItem", at = @At("HEAD"), cancellable = true, require = 0)
    private void hk3gtl$skipCosmicRender(CallbackInfo ci) {
        ci.cancel();
    }
}
