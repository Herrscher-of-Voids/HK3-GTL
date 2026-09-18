package com.sirin.hk3gtl.mixin;



import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.RecipeCapability;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.gregtechceu.gtceu.integration.GTRecipeWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.utils.Size;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchNodes;
import com.sirin.hk3gtl.common.research.Hk3ResearchNode;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.util.Mth;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.List;

/**
 * GTRecipeWidget Mixin —— JEI 配方查看器的增强与修复。
 *
 * <h3>职责</h3>
 * <ol>
 *   <li>修复电压等级选择上限：原版硬编码为14(MAX)，修改后支持扩展的 30 级电压</li>
 *   <li>追加研究认知标签：在配方信息区域下方显示"需要研究认知：XXX"</li>
 *   <li>异常兜底：wrap GT 的 createXEIContainerContents 调用，捕获异常返回空列表，避免整个配方类别丢失</li>
 * </ol>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>调整研究标签样式：修改 hk3gtl$repositionVoltageAndAddResearch 中的 LabelWidget</li>
 *   <li>修改电压上限：setTier 注入中使用 GTValues.VN.length - 1 作为最大值</li>
 *   <li>全部 remap = false（GT 无 Mojang 映射）</li>
 *   <li>@Redirect ordinal 必须与字节码中的调用位置精确对应</li>
 * </ul>
 */
@Mixin(value = GTRecipeWidget.class, remap = false)
public abstract class GTRecipeWidgetMixin {

    private static final org.slf4j.Logger LOGGER = LogUtils.getLogger();
    /** 研究认知标签行高 */
    private static final int LINE_H = 10;

    /** 当前选择的电压等级 */
    @Shadow
    private int tier;

    /** 当前展示的 GT 配方 */
    @Shadow
    private GTRecipe recipe;

    /** GT 原生的配方参数文字标签列表（用于计算追加标签的 Y 坐标） */
    @Shadow
    private List<LabelWidget> recipeParaTexts;

    /** X 偏移量（GT 内部布局用） */
    @Shadow
    private int xOffset;

    @Shadow
    protected abstract int getMinTier();

    /**
     * 保持 GT 原生电压/超频按钮布局不变，
     * 只在现有信息区域下方追加研究认知标签。
     */
    @Inject(method = "<init>", at = @At("RETURN"))
    private void hk3gtl$repositionVoltageAndAddResearch(CallbackInfo ci) {
        try {
            GTRecipeWidget self = (GTRecipeWidget) (Object) this;

            // 计算信息文字最后一行的 Y 坐标
            int lastTextY = 0;
            if (!recipeParaTexts.isEmpty()) {
                LabelWidget last = recipeParaTexts.get(recipeParaTexts.size() - 1);
                lastTextY = last.getPositionY() + last.getSizeHeight();
            }

            int nextY = lastTextY + 2;

            // 添加研究认知标签
            if (recipe != null) {
                String researchId = Hk3RecipeResearchGate.getRequiredResearch(recipe.id);
                if (researchId != null) {
                    Hk3ResearchNode node = Hk3ResearchNodes.get(researchId);
                    String nodeName = node != null
                            ? Hk3ResearchNodes.stripIdPrefix(I18n.get(node.nameKey()))
                            : researchId;
                    boolean locked = hk3gtl$isJeiRecipeLocked(recipe);
                    self.addWidget(new LabelWidget(3 - xOffset, nextY,
                            (locked ? "\u00a7c" : "\u00a7d") + I18n.get("hk3gtl.jei.requires_research", nodeName)));
                    nextY += LINE_H + 2;
                    if (locked) {
                        self.addWidget(new LabelWidget(3 - xOffset, nextY,
                                "\u00a76" + I18n.get("hk3gtl.jei.research_locked_hint")));
                        nextY += LINE_H + 2;
                    }
                }
            }

            // 扩展 widget 高度以容纳所有内容
            int requiredH = nextY + 4;
            if (requiredH > self.getSize().height) {
                self.setSize(new Size(self.getSize().width, requiredH));
            }
        } catch (Exception e) {
            LOGGER.debug("[HK3GTL] JEI 布局调整跳过: {}", e.getMessage());
        }
    }

    /** 扩展电压等级上限：将原版 clamp(0,14) 改为 clamp(minTier, VN.length-1) */
    @Inject(method = "setTier", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$extendMaxTier(int tier, CallbackInfo ci) {
        this.tier = Mth.clamp(tier, getMinTier(), GTValues.VN.length - 1);
        ci.cancel();
    }

    @Redirect(
            method = "collectStorage",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/gregtechceu/gtceu/api/capability/recipe/RecipeCapability;createXEIContainerContents(Ljava/util/List;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;Lcom/gregtechceu/gtceu/api/capability/recipe/IO;)Ljava/util/List;",
                    ordinal = 0
            )
    )
    private List<Object> hk3gtl$safeCreateInputContents0(RecipeCapability<?> capability, List<Content> contents, GTRecipe recipe, IO io) {
        return hk3gtl$safeCreateXEIContainerContents(capability, contents, recipe, io);
    }

    @Redirect(
            method = "collectStorage",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/gregtechceu/gtceu/api/capability/recipe/RecipeCapability;createXEIContainerContents(Ljava/util/List;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;Lcom/gregtechceu/gtceu/api/capability/recipe/IO;)Ljava/util/List;",
                    ordinal = 1
            )
    )
    private List<Object> hk3gtl$safeCreateInputContents1(RecipeCapability<?> capability, List<Content> contents, GTRecipe recipe, IO io) {
        return hk3gtl$safeCreateXEIContainerContents(capability, contents, recipe, io);
    }

    @Redirect(
            method = "collectStorage",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/gregtechceu/gtceu/api/capability/recipe/RecipeCapability;createXEIContainerContents(Ljava/util/List;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;Lcom/gregtechceu/gtceu/api/capability/recipe/IO;)Ljava/util/List;",
                    ordinal = 2
            )
    )
    private List<Object> hk3gtl$safeCreateOutputContents0(RecipeCapability<?> capability, List<Content> contents, GTRecipe recipe, IO io) {
        return hk3gtl$safeCreateXEIContainerContents(capability, contents, recipe, io);
    }

    @Redirect(
            method = "collectStorage",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/gregtechceu/gtceu/api/capability/recipe/RecipeCapability;createXEIContainerContents(Ljava/util/List;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;Lcom/gregtechceu/gtceu/api/capability/recipe/IO;)Ljava/util/List;",
                    ordinal = 3
            )
    )
    private List<Object> hk3gtl$safeCreateOutputContents1(RecipeCapability<?> capability, List<Content> contents, GTRecipe recipe, IO io) {
        return hk3gtl$safeCreateXEIContainerContents(capability, contents, recipe, io);
    }

    /**
     * 安全包装 createXEIContainerContents 调用。
     * 研究锁定只影响机器执行，不清空 JEI 内容；否则玩家无法搜索到被锁配方。
     * 捕获 RuntimeException 返回空列表，避免单个配方异常导致整个 JEI 类别丢失。
     * 返回 ArrayList（非 List.of()）以兼容后续可能的 .add() 操作。
     */
    private List<Object> hk3gtl$safeCreateXEIContainerContents(RecipeCapability<?> capability, List<Content> contents, GTRecipe recipe, IO io) {
        try {
            return capability.createXEIContainerContents(contents, recipe, io);
        } catch (RuntimeException exception) {
            LOGGER.warn("[HK3GTL] JEI 跳过异常配方内容，避免 GT 类别整体丢失。capability={}, io={}, recipe={}",
                    capability, io, recipe, exception);
            return new ArrayList<>();
        }
    }

    private static boolean hk3gtl$isJeiRecipeLocked(GTRecipe recipe) {
        if (recipe == null) return false;
        String researchId = Hk3RecipeResearchGate.getRequiredResearch(recipe.id);
        if (researchId == null) return false;
        var player = Minecraft.getInstance().player;
        if (player == null) return false;
        return !Hk3ResearchManager.isCompleted(player, researchId);
    }
}
