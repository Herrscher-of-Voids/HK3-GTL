package com.sirin.hk3gtl.mixin;



import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 本模组 RecipeType 注册搭车 Mixin。
 *
 * <p><b>目标类</b>：{@link GTRecipeTypes}
 * （GTCEu 的配方类型总注册入口，{@code ASSEMBLER} / {@code CHEMICAL_REACTOR} 等都在这注册）。
 *
 * <p><b>注入目的</b>：{@code RecipeType} 是 Minecraft 的 Registry 对象，必须在注册表冻结前注册。
 * GTCEu 在自己的 {@code init()} 里统一注册所有配方类型，本模组想加的自定义配方类型
 * （见 {@link Hk3RecipeTypes}）也必须在这个时间点挤进去，才能被 GTCEu 的机器、
 * JEI 插件、DataGen 识别。
 *
 * <p><b>失效后影响</b>：
 * <ul>
 *   <li>本模组自定义的 RecipeType 全部没注册 → 相关机器运行时 NPE。</li>
 *   <li>JEI 看不到我们的新配方类别，玩家无法查询。</li>
 *   <li>配方 JSON 加载时会报 "unknown recipe type"。</li>
 * </ul>
 *
 * <p><b>修改指南</b>：
 * <ul>
 *   <li>职责纯粹：仅调用 {@link Hk3RecipeTypes#init()}，具体 RecipeType 构造全部写在该类里，
 *       避免 Mixin 堆积业务逻辑（SRP 原则）。</li>
 *   <li>GTCEu 若修改 {@code init} 方法签名或拆分注册阶段（例如分成
 *       {@code initServerOnly} / {@code initCommon}），需要同步修改此处 method 名。</li>
 *   <li>Architectury 项目提醒：common 模块添加新 RecipeType 后，
 *       Fabric/Forge 双平台都要验证一次。</li>
 *   <li>{@code remap = false} 强制。</li>
 * </ul>
 */
@Mixin(value = GTRecipeTypes.class, remap = false)
public class GTRecipeTypesMixin {

    /**
     * Hook 位置：{@code GTRecipeTypes#init}（static，启动期调用一次，注册所有 GT 配方类型）。
     * <br>Hook 时机：{@code @At("HEAD")} —— 抢在 GTCEu 本身的注册之前执行，保证注册表未冻结。
     * <br>调用：{@link Hk3RecipeTypes#init()} 是本模组 RecipeType 的唯一入口。
     */
    @Inject(method = "init", at = @At("HEAD"), require = 1)
    private static void hk3gtl$registerRecipeTypes(CallbackInfo ci) {
        Hk3RecipeTypes.init();
    }
}
