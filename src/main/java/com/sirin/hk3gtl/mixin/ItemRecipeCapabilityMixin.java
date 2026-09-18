package com.sirin.hk3gtl.mixin;



import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.List;

/**
 * GTCEu 物品配方在 JEI/REI（XEI）展示层的空列表兜底 Mixin。
 *
 * <p><b>目标类</b>：{@link ItemRecipeCapability}
 * （GTCEu 1.4.4 的物品配方能力类，负责把配方中的物品输入输出转换为 XEI 可用的条目）。
 *
 * <p><b>注入目的</b>：GTCEu 原版 {@code createXEIContainerContents} 在收到
 * <b>空列表</b>或<b>畸形列表</b>时，内部直接访问 {@code contents.get(0)} 等逻辑，
 * 触发 {@link ArrayIndexOutOfBoundsException}。该异常会从 GTJEIPlugin 注册流程冒上来，
 * 中断整个 JEI 插件注册，导致 JEI 完全不显示 GT 配方。
 *
 * <p>本模组新增了大量"占位空输入/空输出"的配方（例如纯能耗机器、生命值恢复机），
 * 空 content 非常常见，所以必须兜底。
 *
 * <p><b>失效后影响</b>：
 * <ul>
 *   <li>JEI 注册抛 AIOOBE → 整个 JEI 丢失所有 GT 配方。</li>
 *   <li>玩家无法查看任何 GTM 机器的配方，游戏体验崩塌（但不会闪退游戏）。</li>
 * </ul>
 *
 * <p><b>修改指南</b>：
 * <ul>
 *   <li>兜底必须用 {@code new ArrayList<>()} 而不是 {@code List.of()} / {@code Collections.emptyList()}，
 *       因为 GTCEu/JEI 后续代码可能对返回值调 {@code .add()}，不可变列表会 UOE。</li>
 *   <li>这里采用"软兜底"：只拦空列表场景，非空仍交给原方法处理，最大限度保留
 *       GTCEu 原有逻辑，避免替换实现带来的副作用。</li>
 *   <li>若将来遇到非空但仍会抛异常的配方，可在此 Mixin 增加
 *       try-catch 风格的 {@code @Redirect} 兜底（参考 {@code FluidRecipeCapabilityMixin}）。</li>
 *   <li>{@code remap = false}（第三方模组类）。</li>
 * </ul>
 */
@Mixin(value = ItemRecipeCapability.class, remap = false)
public class ItemRecipeCapabilityMixin {

    /**
     * Hook 位置：{@code ItemRecipeCapability#createXEIContainerContents}
     * （把配方 Content 列表转成 XEI 可渲染的条目列表）。
     * <br>Hook 时机：{@code @At("HEAD")} + {@code cancellable = true} —— 仅在空/null 时接管，
     * 其他情况 {@code ci.setReturnValue} 未调用，Mixin 自动放行给原方法。
     * <br>返回：可变空 ArrayList，保证后续 {@code .add()} 不会 UOE。
     */
    @Inject(method = "createXEIContainerContents", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$safeCreateXEIContents(List<Content> contents, GTRecipe recipe, IO io, CallbackInfoReturnable<List<Object>> cir) {
        if (contents == null || contents.isEmpty()) {
            cir.setReturnValue(new ArrayList<>());
        }
    }
}
