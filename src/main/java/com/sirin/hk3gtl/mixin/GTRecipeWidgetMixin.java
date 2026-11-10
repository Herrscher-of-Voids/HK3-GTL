package com.sirin.hk3gtl.mixin;




/** 中文说明：该处说明已按当前代码行为整理。*/
import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.RecipeCapability;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.gregtechceu.gtceu.integration.GTRecipeWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.gui.widget.TextBoxWidget;
import com.lowdragmc.lowdraglib.utils.Size;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3ResearchRequirementPolicy;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import com.sirin.hk3gtl.common.research.Hk3ResearchPlans;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;
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
import java.util.Locale;
import java.util.HashSet;
import java.util.Set;

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
/**
 * 【变更记录 #1】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：JEI显示并校验全部研究前置，不只读第一条。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #2】2026-10-17 15:35:03（第2次备注 · 修订164）
 * 删除：完成数量摘要、通用悬停提示及重复的祖先课题名称。
 * 新增：直接前置名称的自动换行，电路分支名称和逐项状态详情。
 * 修改：只对展示列表去除被其他条件包含的祖先；服务端仍完整校验原有全部条件。
 * 用途：让玩家直接看清所需研究，不把依赖树的上游课题重复展开，不改配方或研究权限。
 */
/**
 * 【变更记录 #3】2026-10-17 16:27:36（第3次备注 · 修订165）
 * 删除：无；新增：高阶工况同源额定电压与真实EU/t文字。
 * 修改：与服务器共读配方数据，不使用GTL钳MAX的euTier显示门槛。
 * 用途：玩家能看到真实单路要求，研究与参数布局继续按实际高度延展；不宣称硬件已验收。
 */
public abstract class GTRecipeWidgetMixin {

    private static final org.slf4j.Logger LOGGER = LogUtils.getLogger();
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

            if (Hk3RecipePower.marked(recipe)) {
                int textX = 3 - xOffset;
                int textWidth = Math.max(40, self.getSize().width - Math.max(0, textX) - 3);
                var powerText = new TextBoxWidget(textX, nextY, textWidth,
                        List.of(Hk3RecipePower.tooltip(recipe).getString())).setShadow(true);
                self.addWidget(powerText);
                nextY += powerText.getSize().height + 2;
            }

            // 历史记录：修订163 · 2026-10-17 15:07:57：固定两行摘要，全部门槛移到悬停详情，JEI不隐藏配方。
            // 修订164 · 2026-10-17 15:35:03：只列直接前置名称，移除重复祖先；按实际宽度换行，悬停保留逐项状态。
            if (recipe != null) {
                var requirements = Hk3RecipeAccess.effectiveRequirements(recipe);
                var player = Minecraft.getInstance().player;
                var state = Hk3ResearchRequirementPolicy.evaluate(requirements,
                        id -> player != null && Hk3ResearchManager.isCompleted(player, id));
                if (!requirements.requirements().isEmpty() || !requirements.valid()) {
                    var details = new ArrayList<Component>();
                    var names = new ArrayList<String>();
                    for (String researchId : hk3gtl$directResearch(requirements.requirements())) {
                        String nodeName = hk3gtl$researchName(researchId);
                        boolean done = !state.missing().contains(researchId);
                        names.add((done ? "\u00a7a" : "\u00a7c") + nodeName);
                        details.add(Component.literal((done ? "\u00a7a" : "\u00a7c") + researchId + " · " + nodeName
                                + " [" + I18n.get(done ? "hk3gtl.jei.research_status_done"
                                : "hk3gtl.jei.research_status_locked") + "]"));
                    }
                    for (String invalid : requirements.invalid()) {
                        if (!requirements.requirements().contains(invalid)) {
                            names.add("\u00a7c" + I18n.get("hk3gtl.jei.research_invalid"));
                            details.add(Component.literal("\u00a7c"
                                    + I18n.get("hk3gtl.jei.research_status_locked") + ": " + invalid));
                        }
                    }
                    int textX = 3 - xOffset;
                    int textWidth = Math.max(40, self.getSize().width - Math.max(0, textX) - 3);
                    String researchText = "\u00a78" + I18n.get("hk3gtl.jei.research_summary",
                            String.join("\u00a78" + I18n.get("hk3gtl.jei.research_separator"), names));
                    var researchNames = new TextBoxWidget(textX, nextY, textWidth, List.of(researchText))
                            .setShadow(true);
                    researchNames.setHoverTooltips(details);
                    self.addWidget(researchNames);
                    nextY += researchNames.getSize().height + 2;
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

    private static String hk3gtl$researchName(String researchId) {
        var plan = Hk3ResearchPlans.get(researchId);
        if (plan != null) return I18n.get(plan.nameKey());
        if (researchId.startsWith(Hk3ResearchData.CIRCUIT_PREFIX)) {
            String tier = researchId.substring(Hk3ResearchData.CIRCUIT_PREFIX.length());
            if (Hk3ResearchData.CIRCUIT_TIERS.contains(tier))
                return I18n.get("hk3gtl.jei.research_circuit_branch", tier.toUpperCase(Locale.ROOT));
        }
        return researchId;
    }

    /** 仅精简展示；独立并列条件保留，未知条件不按猜测隐藏。 */
    private static List<String> hk3gtl$directResearch(List<String> requirements) {
        Set<String> ancestors = new HashSet<>();
        for (String id : requirements) hk3gtl$collectAncestors(id, ancestors);
        return requirements.stream().filter(id -> !ancestors.contains(id)).toList();
    }

    private static void hk3gtl$collectAncestors(String id, Set<String> ancestors) {
        if (id.startsWith(Hk3ResearchData.CIRCUIT_PREFIX)) {
            if (Hk3ResearchData.CIRCUIT_TIERS.contains(id.substring(Hk3ResearchData.CIRCUIT_PREFIX.length()))) {
                if (ancestors.add(Hk3ResearchData.CORE_RESEARCH))
                    hk3gtl$collectAncestors(Hk3ResearchData.CORE_RESEARCH, ancestors);
            }
            return;
        }
        var topic = Hk3ResearchCatalog.bundled().get(id);
        if (topic == null) return;
        for (String prerequisite : topic.prerequisites())
            if (ancestors.add(prerequisite)) hk3gtl$collectAncestors(prerequisite, ancestors);
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

}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
