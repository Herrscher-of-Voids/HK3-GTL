package com.sirin.hk3gtl.mixin;



import com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.util.GsonHelper;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.registries.ForgeRegistries;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * GTCEu {@code FluidIngredient} JSON 解析增强 Mixin。
 *
 * <p><b>目标类</b>：{@link FluidIngredient}（GTCEu 1.4.4 的流体配方材料类，
 * 负责把配方 JSON 里的 {@code "fluid"} / {@code "tag"} 反序列化成可用的流体条件）。
 *
 * <p><b>注入目的</b>：修复 GTCEu 原版在解析"模组自定义流体"时会退化为
 * {@code minecraft:empty} 的问题。
 * 原版实现只查询 {@link BuiltInRegistries#FLUID}（Vanilla 注册表），但 Forge 模组常见做法
 * 是把流体注册在 {@link ForgeRegistries#FLUIDS}。两个注册表在大部分情况下是同步的，
 * 但在部分加载顺序/平台流体场景下不同步，导致 GTCEu 拿到空流体，JEI 显示 0mB。
 *
 * <p><b>失效后影响</b>：
 * <ul>
 *   <li>某些模组流体配方 JEI 显示为空气、输入输出 0 mB。</li>
 *   <li>{@code FluidIngredient.getStacks()} 返回空数组，可能导致合成/配方匹配失败。</li>
 *   <li>不会崩溃，但用户会"看不到"配方所需流体，属于体验级严重 bug。</li>
 * </ul>
 *
 * <p><b>修改指南</b>：
 * <ul>
 *   <li>GTCEu 未来若自行修复该问题，可在确认后删除本 Mixin。</li>
 *   <li>不要把"同时包含 fluid 和 tag 即报错"的语义去掉，这是保持与原版一致的契约。</li>
 *   <li>{@code remap = false} 因 GTCEu 是第三方，必加。</li>
 *   <li>本 Mixin 使用 {@code @At("HEAD") + cancellable}，整体接管 JSON 解析，
 *       未来若 GTCEu 的 {@code valueFromJson} 增加了新 JSON 字段（如 "amount"），
 *       需同步在此处补齐处理，否则会丢字段。</li>
 * </ul>
 */
@Mixin(value = FluidIngredient.class, remap = false)
public class FluidIngredientMixin {

    /**
     * Hook 位置：{@code FluidIngredient#valueFromJson(JsonObject)}（JSON 反序列化入口）。
     * <br>Hook 时机：{@code @At("HEAD")} + {@code cancellable = true} —— 完整接管原方法。
     * <br>流程：
     * <ol>
     *   <li>若同时出现 fluid 和 tag → 与原版一致抛 {@link JsonParseException}；</li>
     *   <li>若是 fluid 分支：先查 Vanilla 注册表，拿到空流体时再回退到 Forge 注册表；</li>
     *   <li>若是 tag 分支：直接构造 {@link TagKey}，保持原行为。</li>
     * </ol>
     */
    @Inject(method = "valueFromJson", at = @At("HEAD"), cancellable = true, require = 1)
    private static void hk3gtl$readModFluid(JsonObject json,
                                            CallbackInfoReturnable<FluidIngredient.Value> cir) {
        if (json.has("fluid") && json.has("tag")) {
            throw new JsonParseException("A fluid ingredient entry is either a tag or a fluid, not both");
        }
        if (json.has("fluid")) {
            ResourceLocation id = new ResourceLocation(GsonHelper.getAsString(json, "fluid"));
            Fluid fluid = BuiltInRegistries.FLUID.get(id);
            if (fluid == Fluids.EMPTY && !id.equals(BuiltInRegistries.FLUID.getKey(Fluids.EMPTY))) {
                Fluid forgeFluid = ForgeRegistries.FLUIDS.getValue(id);
                if (forgeFluid != null) {
                    fluid = forgeFluid;
                }
            }
            cir.setReturnValue(new FluidIngredient.FluidValue(fluid));
            return;
        }
        if (json.has("tag")) {
            ResourceLocation id = new ResourceLocation(GsonHelper.getAsString(json, "tag"));
            TagKey<Fluid> tagKey = TagKey.create(Registries.FLUID, id);
            cir.setReturnValue(new FluidIngredient.TagValue(tagKey));
        }
    }
}
