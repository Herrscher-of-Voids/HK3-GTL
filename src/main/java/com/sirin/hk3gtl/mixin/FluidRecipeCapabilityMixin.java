package com.sirin.hk3gtl.mixin;



import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import com.lowdragmc.lowdraglib.utils.CycleFluidTransfer;
import com.mojang.datafixers.util.Either;
import com.mojang.datafixers.util.Pair;
import com.mojang.logging.LogUtils;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import org.slf4j.Logger;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * GTCEu 流体配方在 JEI/REI（XEI）展示层的修复 Mixin。
 *
 * <p><b>目标类</b>：{@link FluidRecipeCapability}
 * （GTCEu 1.4.4 流体配方能力类，负责将配方中的流体输入输出转成 XEI 可渲染的条目）。
 *
 * <p><b>注入目的</b>：修复两类 JEI 展示故障。
 * <ol>
 *   <li><b>空内容崩溃</b>：GTCEu 原版 {@code createXEIContainerContents} 遇到
 *       空列表 / null Content 时没有兜底，会直接抛异常中断整个 GTJEIPlugin 注册，
 *       进而导致 JEI 不显示任何 GT 配方。</li>
 *   <li><b>流体退化为空气</b>：原版用 {@code TagOrCycleFluidTransfer} 适配层展示流体，
 *       在自定义流体 / 模组流体场景下会把流体值转换成 {@link Fluids#EMPTY}，
 *       表现为 JEI 条目显示 0 mB 或空占位。这里改用 {@link CycleFluidTransfer}
 *       并自己负责 Either &lt;Tag, FluidStack&gt; 的展开，减少中间转换丢失。</li>
 * </ol>
 *
 * <p><b>失效后影响</b>：
 * <ul>
 *   <li>JEI 注册期可能整体崩溃，GT 所有配方消失。</li>
 *   <li>即便不崩，模组流体/标签流体展示异常，玩家无法通过 JEI 查看配方。</li>
 * </ul>
 *
 * <p><b>修改指南</b>：
 * <ul>
 *   <li>异常兜底必须返回 {@code new ArrayList<>()} 而不是 {@code List.of()}，
 *       因为 XEI 后续流程可能对该 List 调用 {@code .add()}，不可变列表会 UOE。</li>
 *   <li>{@link #hk3gtl$unwrapEntry(Object)} 处理 Either 的左右分支：
 *       <ul>
 *         <li>右值：直接是 {@code List<FluidStack>}，过滤空流体后返回；</li>
 *         <li>左值：是 {@code List<Pair<TagKey, Long>>}，展开 Tag → 多个 FluidStack。</li>
 *       </ul>
 *       若将来 GTCEu 修改该 Either 的泛型结构，必须同步修改此方法。</li>
 *   <li>所有 {@code RuntimeException} 都要捕获并降级为"跳过此条目"，绝不能让单个
 *       有问题的配方拖垮整个 JEI 注册（项目规则：异常兜底）。</li>
 *   <li>{@code remap = false}（第三方模组类）。</li>
 * </ul>
 */
@Mixin(value = FluidRecipeCapability.class, remap = false)
public class FluidRecipeCapabilityMixin {

    private static final Logger LOGGER = LogUtils.getLogger();

    /**
     * Hook 位置：{@code FluidRecipeCapability#createXEIContainerContents}
     * （把配方的 Content 列表转成 XEI 可用的条目列表）。
     * <br>Hook 时机：{@code @At("HEAD")} + {@code cancellable} —— 完全接管，不让原方法执行。
     * <br>策略：遍历每个 Content，转成 {@link FluidIngredient}，调用
     * {@code FluidRecipeCapability.mapFluid} 生成展示条目；任何一步失败都记日志并填 null，
     * 保证列表长度和原 contents 对齐，不影响 XEI 的占位逻辑。
     */
    @Inject(method = "createXEIContainerContents", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$safeCreateXEIContents(List<Content> contents, GTRecipe recipe, IO io,
                                              CallbackInfoReturnable<List<Object>> cir) {
        if (contents == null || contents.isEmpty()) {
            cir.setReturnValue(new ArrayList<>());
            return;
        }

        List<Object> entryLists = new ArrayList<>(contents.size());
        for (Content content : contents) {
            if (content == null || content.content == null) {
                entryLists.add(null);
                continue;
            }

            try {
                FluidIngredient ingredient = FluidRecipeCapability.CAP.of(content.content);
                if (ingredient == null || ingredient.isEmpty() || ingredient.getStacks().length == 0) {
                    LOGGER.warn("[HK3GTL] JEI 流体内容转换后为空，rawClass={}, recipe={}, io={}",
                            content.content.getClass().getName(), recipe.id, io);
                    entryLists.add(null);
                    continue;
                }
                entryLists.add(FluidRecipeCapability.mapFluid(ingredient));
            } catch (RuntimeException exception) {
                LOGGER.warn("[HK3GTL] JEI 流体内容转换失败，rawClass={}, recipe={}, io={}",
                        content.content.getClass().getName(), recipe.id, io, exception);
                entryLists.add(null);
            }
        }
        cir.setReturnValue(entryLists);
    }

    /**
     * Hook 位置：{@code FluidRecipeCapability#createXEIContainer}
     * （把上一步生成的条目列表包装成 XEI 的容器对象，用于点击展开/循环展示）。
     * <br>Hook 时机：{@code @At("HEAD")} + {@code cancellable} —— 接管并改用
     * {@link CycleFluidTransfer}（纯流体循环展示器），规避原版 TagOrCycleFluidTransfer
     * 的退化问题。
     * <br>null 兜底：contents == null 时返回空的循环容器，不让 XEI 拿到 null。
     */
    @Inject(method = "createXEIContainer", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$useCycleFluidTransfer(List<?> contents, CallbackInfoReturnable<Object> cir) {
        if (contents == null) {
            cir.setReturnValue(new CycleFluidTransfer(Collections.emptyList()));
            return;
        }

        List<List<FluidStack>> normalized = new ArrayList<>(contents.size());
        for (Object entry : contents) {
            normalized.add(hk3gtl$unwrapEntry(entry));
        }
        cir.setReturnValue(new CycleFluidTransfer(normalized));
    }

    /**
     * 辅助方法：展开一个 XEI 条目为 {@code List<FluidStack>}。
     * <p>GTCEu 的条目类型是 {@code Either<List<Pair<TagKey<Fluid>, Long>>, List<FluidStack>>}：
     * <ul>
     *   <li>右值分支（直接流体列表）：过滤掉 empty 流体；</li>
     *   <li>左值分支（Tag + 数量）：查 Tag 下所有流体，每个展开成一个 FluidStack；</li>
     *   <li>其他情况（包括非 Either）：返回空列表，确保循环展示器位数对齐。</li>
     * </ul>
     */
    private static List<FluidStack> hk3gtl$unwrapEntry(Object entry) {
        if (!(entry instanceof Either<?, ?> either)) {
            return Collections.emptyList();
        }

        Object right = either.right().orElse(null);
        if (right instanceof List<?> rightList) {
            List<FluidStack> fluids = new ArrayList<>();
            for (Object obj : rightList) {
                if (obj instanceof FluidStack stack && !stack.isEmpty() && stack.getFluid() != Fluids.EMPTY) {
                    fluids.add(stack);
                }
            }
            return fluids;
        }

        Object left = either.left().orElse(null);
        if (left instanceof List<?> leftList) {
            List<FluidStack> fluids = new ArrayList<>();
            for (Object obj : leftList) {
                if (!(obj instanceof Pair<?, ?> pair)) {
                    continue;
                }
                if (!(pair.getFirst() instanceof TagKey<?> rawTag)) {
                    continue;
                }
                if (!(pair.getSecond() instanceof Long amount) || amount <= 0) {
                    continue;
                }
                @SuppressWarnings("unchecked")
                TagKey<Fluid> tag = (TagKey<Fluid>) rawTag;
                for (Holder<Fluid> holder : BuiltInRegistries.FLUID.getTagOrEmpty(tag)) {
                    Fluid fluid = holder.value();
                    if (fluid != Fluids.EMPTY) {
                        fluids.add(FluidStack.create(fluid, amount, null));
                    }
                }
            }
            return fluids;
        }

        return Collections.emptyList();
    }
}
