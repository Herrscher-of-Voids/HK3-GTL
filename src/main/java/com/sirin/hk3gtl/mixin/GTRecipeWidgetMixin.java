package com.sirin.hk3gtl.mixin;

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
import com.sirin.hk3gtl.client.compat.Hk3WorldMiningJei;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3ResearchRequirementPolicy;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import com.sirin.hk3gtl.common.research.Hk3ResearchPlans;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipeVoltageDisplay;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.HashSet;
import java.util.Set;

@Mixin(value = GTRecipeWidget.class, remap = false)
public abstract class GTRecipeWidgetMixin {

    private static final org.slf4j.Logger LOGGER = LogUtils.getLogger();
    @Shadow
    private int tier;

    @Shadow
    private GTRecipe recipe;

    @Shadow
    private List<LabelWidget> recipeParaTexts;

    @Shadow
    private LabelWidget voltageTextWidget;

    @Shadow
    private int xOffset;

    @Shadow
    protected abstract int getMinTier();

    @ModifyVariable(method = "<init>", at = @At("HEAD"), argsOnly = true)
    private static GTRecipe hk3gtl$worldBubbleOutputs(GTRecipe recipe) {
        return Hk3WorldMiningJei.display(recipe);
    }

    @Inject(method = "<init>", at = @At("RETURN"))
    private void hk3gtl$repositionVoltageAndAddResearch(CallbackInfo ci) {
        GTRecipeWidget self = (GTRecipeWidget) (Object) this;

        int lastTextY = 0;
        if (!recipeParaTexts.isEmpty()) {
            LabelWidget last = recipeParaTexts.get(recipeParaTexts.size() - 1);
            lastTextY = last.getPositionY() + last.getSizeHeight();
        }
        if (recipe.recipeType.registryName.getPath().equals("industrial_process_i26")) {
            lastTextY = self.widgets.stream().filter(w -> w instanceof LabelWidget && w != voltageTextWidget)
                    .mapToInt(w -> w.getPositionY() + w.getSizeHeight()).max().orElse(lastTextY);
        }

        int nextY = lastTextY + 2;

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
            long networkCredit = recipe.data.getLong(Hk3LiquidProcessMachine.CREDIT);
            if (networkCredit > 0) {
                int textX = 3 - xOffset;
                int textWidth = Math.max(40, self.getSize().width - Math.max(0, textX) - 3);
                var outputLines = new ArrayList<String>();
                outputLines.add(I18n.get("hk3gtl.jei.honkai_energy_output", networkCredit));
                switch (recipe.recipeType.registryName.getPath()) {
                    case "industrial_process_i19", "industrial_process_i20", "industrial_process_i21", "industrial_process_i22" ->
                            outputLines.add(0, I18n.get("hk3gtl.jei.honkai_energy_rate",
                                    String.format(Locale.ROOT, "%.8f", (double) networkCredit / recipe.duration)));
                }
                var outputText = new TextBoxWidget(textX, nextY, textWidth, outputLines).setShadow(true);
                self.addWidget(outputText);
                nextY += outputText.getSize().height + 2;
            }
        }

        int requiredH = nextY + 4;
        if (requiredH > self.getSize().height) {
            self.setSize(new Size(self.getSize().width, requiredH));
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

    /** 原生电压查询在int以上钳为MAX；只让显示读取配方实际工作档，保留高安培MAX原义。 */
    @Inject(method = "getMinTier", at = @At("RETURN"), cancellable = true, require = 1)
    private void hk3gtl$displayRequiredTier(CallbackInfoReturnable<Integer> cir) {
        if (Hk3RecipePower.marked(recipe)) {
            int count = Math.min(GTValues.V.length, GTValues.VNF.length);
            cir.setReturnValue(Hk3RecipeVoltageDisplay.minimumTier(
                    cir.getReturnValue(), Hk3RecipePower.tier(recipe), count));
        }
    }

    /** 高阶缩写均为三字母，按实际字宽保留原有右侧留白。 */
    @Inject(method = "getVoltageXOffset", at = @At("RETURN"), cancellable = true, require = 1)
    private void hk3gtl$fitExtendedTierName(CallbackInfoReturnable<Integer> cir) {
        if (tier > GTValues.MAX && tier < GTValues.VNF.length) {
            int extra = Math.max(0, Minecraft.getInstance().font.width(GTValues.VNF[tier]) - 12);
            cir.setReturnValue(cir.getReturnValue() - extra);
        }
    }

    @Inject(method = "setTier", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$extendMaxTier(int tier, CallbackInfo ci) {
        this.tier = Mth.clamp(tier, getMinTier(), GTValues.VN.length - 1);
        // 服务端显式工况不超频，查看器也不能预演不存在的耗电和工期。
        if (Hk3RecipePower.marked(recipe)) {
            int count = Math.min(GTValues.V.length, GTValues.VNF.length);
            this.tier = Hk3RecipeVoltageDisplay.minimumTier(this.tier, Hk3RecipePower.tier(recipe), count);
        }
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

    /** 研究锁定仍展示配方；单项内容异常不影响其余JEI类别。 */
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

