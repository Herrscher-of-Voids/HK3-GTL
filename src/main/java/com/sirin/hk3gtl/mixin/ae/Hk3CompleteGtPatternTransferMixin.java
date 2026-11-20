package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEFluidKey;
import appeng.api.stacks.GenericStack;
import appeng.integration.modules.jei.transfer.EncodePatternTransferHandler;
import appeng.integration.modules.jeirei.EncodingHelper;
import appeng.menu.me.items.PatternEncodingTermMenu;
import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.gregtechceu.gtceu.api.recipe.ingredient.IntProviderIngredient;
import com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient;
import com.gregtechceu.gtceu.integration.jei.recipe.GTRecipeWrapper;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.llamalad7.mixinextras.sugar.Share;
import com.llamalad7.mixinextras.sugar.ref.LocalRef;
import mezz.jei.api.gui.ingredient.IRecipeSlotsView;
import mezz.jei.api.recipe.transfer.IRecipeTransferError;
import mezz.jei.api.recipe.transfer.IRecipeTransferHandlerHelper;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import org.gtlcore.gtlcore.client.gui.PatterEncodingTermMenuModify;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.List;

@Mixin(value = EncodePatternTransferHandler.class, remap = false)
public abstract class Hk3CompleteGtPatternTransferMixin {
    @Unique private static final String HK3GTL_TRANSFER =
            "transferRecipe(Lappeng/menu/me/items/PatternEncodingTermMenu;Ljava/lang/Object;Lmezz/jei/api/gui/ingredient/IRecipeSlotsView;Lnet/minecraft/world/entity/player/Player;ZZ)Lmezz/jei/api/recipe/transfer/IRecipeTransferError;";
    @Shadow @Final private IRecipeTransferHandlerHelper helper;

    @ModifyExpressionValue(method = HK3GTL_TRANSFER, at = @At(value = "INVOKE", target =
            "Lappeng/integration/modules/jei/GenericEntryStackHelper;ofInputs(Lmezz/jei/api/gui/ingredient/IRecipeSlotsView;)Ljava/util/List;"))
    private List<List<GenericStack>> hk3gtl$recipeInputs(List<List<GenericStack>> visible,
            PatternEncodingTermMenu menu, Object displayed, @Share("transferProblem") LocalRef<Component> problem) {
        if (!(displayed instanceof GTRecipeWrapper wrapper)) return visible;
        var recipe = wrapper.recipe;
        if (!recipe.getTickInputContents(ItemRecipeCapability.CAP).isEmpty()
                || !recipe.getTickInputContents(FluidRecipeCapability.CAP).isEmpty()) {
            problem.set(Component.translatable("hk3gtl.pattern_transfer.variable"));
            return visible;
        }
        var inputs = new ArrayList<List<GenericStack>>();
        for (var content : recipe.getInputContents(ItemRecipeCapability.CAP)) {
            if (hk3gtl$variableItem(content)) {
                problem.set(Component.translatable("hk3gtl.pattern_transfer.variable"));
                return visible;
            }
            inputs.add(hk3gtl$itemChoices(content));
        }
        for (var content : recipe.getInputContents(FluidRecipeCapability.CAP)) inputs.add(hk3gtl$fluidChoices(content));
        if (inputs.stream().anyMatch(List::isEmpty)) problem.set(Component.translatable("hk3gtl.pattern_transfer.missing"));
        return inputs;
    }

    @ModifyExpressionValue(method = HK3GTL_TRANSFER, at = @At(value = "INVOKE", target =
            "Lappeng/integration/modules/jei/GenericEntryStackHelper;ofOutputs(Lmezz/jei/api/gui/ingredient/IRecipeSlotsView;)Ljava/util/List;"))
    private List<GenericStack> hk3gtl$recipeOutputs(List<GenericStack> visible,
            PatternEncodingTermMenu menu, Object displayed, @Share("transferProblem") LocalRef<Component> problem) {
        if (!(displayed instanceof GTRecipeWrapper wrapper)) return visible;
        var recipe = wrapper.recipe;
        var outputs = new ArrayList<GenericStack>();
        for (var content : recipe.getOutputContents(ItemRecipeCapability.CAP))
            if (hk3gtl$guaranteed(content) && !(hk3gtl$variableItem(content)))
                hk3gtl$addOutput(hk3gtl$itemChoices(content), outputs, problem);
        for (var content : recipe.getOutputContents(FluidRecipeCapability.CAP))
            if (hk3gtl$guaranteed(content)) hk3gtl$addOutput(hk3gtl$fluidChoices(content), outputs, problem);
        if (outputs.isEmpty() && problem.get() == null)
            problem.set(Component.translatable("hk3gtl.pattern_transfer.no_output"));
        return outputs;
    }

    @WrapOperation(method = HK3GTL_TRANSFER, at = @At(value = "INVOKE", target =
            "Lappeng/integration/modules/jeirei/EncodingHelper;encodeProcessingRecipe(Lappeng/menu/me/items/PatternEncodingTermMenu;Ljava/util/List;Ljava/util/List;)V"))
    private void hk3gtl$checkCapacity(PatternEncodingTermMenu menu, List<List<GenericStack>> inputs,
            List<GenericStack> outputs, Operation<Void> original, PatternEncodingTermMenu sourceMenu, Object displayed,
            @Share("transferProblem") LocalRef<Component> problem) {
        if (!(displayed instanceof GTRecipeWrapper)) {
            original.call(menu, inputs, outputs);
            return;
        }
        if (problem.get() != null) return;
        var priorities = EncodingHelper.getIngredientPriorities(menu, Hk3EncodingHelperAccess.hk3gtl$entryComparator());
        var mergedInputs = new ArrayList<GenericStack>();
        for (var choices : inputs) {
            if (!choices.isEmpty()) Hk3EncodingHelperAccess.hk3gtl$merge(mergedInputs,
                    Hk3EncodingHelperAccess.hk3gtl$best(priorities, choices));
        }
        var mergedOutputs = new ArrayList<GenericStack>();
        for (var output : outputs) Hk3EncodingHelperAccess.hk3gtl$merge(mergedOutputs, output);
        int inputLimit = menu.getProcessingInputSlots().length;
        int outputLimit = menu.getProcessingOutputSlots().length;
        if (mergedInputs.size() > inputLimit || mergedOutputs.size() > outputLimit) {
            problem.set(Component.translatable("hk3gtl.pattern_transfer.capacity",
                    mergedInputs.size(), inputLimit, mergedOutputs.size(), outputLimit));
            return;
        }
        original.call(menu, mergedInputs.stream().map(List::of).toList(), mergedOutputs);
    }

    @Inject(method = HK3GTL_TRANSFER, at = @At("RETURN"), cancellable = true)
    private void hk3gtl$showProblem(PatternEncodingTermMenu menu, Object displayed, IRecipeSlotsView slots,
            Player player, boolean maxTransfer, boolean doTransfer, CallbackInfoReturnable<IRecipeTransferError> result,
            @Share("transferProblem") LocalRef<Component> problem) {
        var message = problem.get();
        if (message == null) return;
        if (menu instanceof PatterEncodingTermMenuModify quickUpload) quickUpload.gTLCore$setQuickUploadRecipeType(null);
        if (doTransfer) player.displayClientMessage(message, false);
        result.setReturnValue(helper.createUserErrorWithTooltip(message));
    }

    @Unique
    private static boolean hk3gtl$variableItem(Content content) {
        return content.content instanceof IntProviderIngredient
                || content.content instanceof SizedIngredient sized && sized.getInner() instanceof IntProviderIngredient;
    }

    @Unique
    private static List<GenericStack> hk3gtl$itemChoices(Content content) {
        var choices = new ArrayList<GenericStack>();
        for (var item : ItemRecipeCapability.CAP.of(content.content).getItems())
            if (!item.isEmpty()) choices.add(GenericStack.fromItemStack(item));
        return choices;
    }

    @Unique
    private static List<GenericStack> hk3gtl$fluidChoices(Content content) {
        var choices = new ArrayList<GenericStack>();
        for (var fluid : FluidRecipeCapability.CAP.of(content.content).getStacks())
            if (!fluid.isEmpty()) choices.add(new GenericStack(AEFluidKey.of(fluid.getFluid(), fluid.getTag()), fluid.getAmount()));
        return choices;
    }

    @Unique
    private static void hk3gtl$addOutput(List<GenericStack> choices, List<GenericStack> outputs,
            LocalRef<Component> problem) {
        if (!choices.isEmpty()) outputs.add(choices.get(0));
        else if (problem.get() == null) problem.set(Component.translatable("hk3gtl.pattern_transfer.missing"));
    }

    @Unique
    private static boolean hk3gtl$guaranteed(Content content) {
        return content.chance > 0 && content.chance >= content.maxChance;
    }
}
