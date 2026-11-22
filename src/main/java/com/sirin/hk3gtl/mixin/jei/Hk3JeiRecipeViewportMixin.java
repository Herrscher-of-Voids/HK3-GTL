package com.sirin.hk3gtl.mixin.jei;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.mojang.blaze3d.platform.InputConstants;
import mezz.jei.api.gui.IRecipeLayoutDrawable;
import mezz.jei.common.input.IInternalKeyMappings;
import mezz.jei.common.util.ImmutableRect2i;
import mezz.jei.gui.input.IClickableIngredientInternal;
import mezz.jei.gui.input.IUserInputHandler;
import mezz.jei.gui.input.UserInput;
import mezz.jei.gui.recipes.RecipeGuiLayouts;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.util.Mth;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

@Mixin(value = RecipeGuiLayouts.class, remap = false)
abstract class Hk3JeiRecipeViewportMixin implements IUserInputHandler {
    @Shadow public abstract void updateLayout(ImmutableRect2i area, int recipesPerPage);

    @Unique private ImmutableRect2i hk3gtl$viewport;
    @Unique private int hk3gtl$scrollY;
    @Unique private int hk3gtl$maxScroll;
    @Unique private IUserInputHandler hk3gtl$recipeInput;

    @Inject(method = "setRecipeLayoutsWithButtons", at = @At("HEAD"))
    private void hk3gtl$resetScroll(List<?> layouts, CallbackInfo ci) {
        hk3gtl$scrollY = 0;
        hk3gtl$maxScroll = 0;
    }

    @Inject(method = "updateLayout", at = @At("HEAD"))
    private void hk3gtl$setViewport(ImmutableRect2i area, int recipesPerPage, CallbackInfo ci) {
        hk3gtl$viewport = area;
    }

    @ModifyExpressionValue(method = "updateLayout", at = @At(value = "INVOKE", target = "Ljava/lang/Math;max(II)I"))
    private int hk3gtl$measureOverflow(int layoutHeight) {
        hk3gtl$maxScroll = layoutHeight - hk3gtl$viewport.getHeight();
        hk3gtl$scrollY = Math.min(hk3gtl$scrollY, hk3gtl$maxScroll);
        return layoutHeight;
    }

    @ModifyExpressionValue(method = "updateLayout", at = @At(value = "INVOKE", target =
            "Lmezz/jei/common/util/ImmutableRect2i;getY()I"))
    private int hk3gtl$applyScroll(int y) {
        return y - hk3gtl$scrollY;
    }

    @Inject(method = "createInputHandler", at = @At("RETURN"), cancellable = true)
    private void hk3gtl$useViewportInput(CallbackInfoReturnable<IUserInputHandler> cir) {
        hk3gtl$recipeInput = cir.getReturnValue();
        cir.setReturnValue(this);
    }

    @Override
    public Optional<IUserInputHandler> handleUserInput(Screen screen, UserInput input, IInternalKeyMappings keys) {
        return hk3gtl$isVisible(input.getMouseX(), input.getMouseY())
                ? hk3gtl$recipeInput.handleUserInput(screen, input, keys) : Optional.empty();
    }

    @Override
    public void unfocus() {
        hk3gtl$recipeInput.unfocus();
    }

    @Override
    public Optional<IUserInputHandler> handleMouseScrolled(double mouseX, double mouseY, double delta) {
        if (!hk3gtl$isVisible(mouseX, mouseY)) return Optional.empty();
        var handled = hk3gtl$recipeInput.handleMouseScrolled(mouseX, mouseY, delta);
        if (handled.isPresent() || hk3gtl$maxScroll == 0 || delta == 0) return handled;

        int step = (int) Math.copySign(Math.ceil(Math.abs(delta) * 16), delta);
        hk3gtl$scrollY = Mth.clamp(hk3gtl$scrollY - step, 0, hk3gtl$maxScroll);
        updateLayout(hk3gtl$viewport, 1);
        return Optional.of(this);
    }

    @Inject(method = "draw", at = @At("HEAD"))
    private void hk3gtl$clipRecipe(GuiGraphics graphics, int mouseX, int mouseY,
                                    CallbackInfoReturnable<Optional<IRecipeLayoutDrawable<?>>> cir) {
        if (hk3gtl$maxScroll == 0) return;
        var view = hk3gtl$viewport;
        graphics.enableScissor(view.getX(), view.getY(), view.getX() + view.getWidth(), view.getY() + view.getHeight());
    }

    @Inject(method = "draw", at = @At("RETURN"), cancellable = true)
    private void hk3gtl$endClip(GuiGraphics graphics, int mouseX, int mouseY,
                                 CallbackInfoReturnable<Optional<IRecipeLayoutDrawable<?>>> cir) {
        if (hk3gtl$maxScroll == 0) return;
        graphics.disableScissor();
        var view = hk3gtl$viewport;
        int x = view.getX() + view.getWidth() + 2;
        int height = view.getHeight();
        int thumb = Math.min(height, Math.max(6, height * height / (height + hk3gtl$maxScroll)));
        int thumbY = view.getY() + (height - thumb) * hk3gtl$scrollY / hk3gtl$maxScroll;
        graphics.fill(x, view.getY(), x + 2, view.getY() + height, 0x60000000);
        graphics.fill(x, thumbY, x + 2, thumbY + thumb, 0xFFC0C0C0);
        if (!hk3gtl$isVisible(mouseX, mouseY)) cir.setReturnValue(Optional.empty());
    }

    @Inject(method = "drawTooltips", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$clipTooltips(GuiGraphics graphics, int mouseX, int mouseY, CallbackInfo ci) {
        if (!hk3gtl$isVisible(mouseX, mouseY)) ci.cancel();
    }

    @Inject(method = "getIngredientUnderMouse", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$clipIngredientLookup(double mouseX, double mouseY,
                                               CallbackInfoReturnable<Stream<IClickableIngredientInternal<?>>> cir) {
        if (!hk3gtl$isVisible(mouseX, mouseY)) cir.setReturnValue(Stream.empty());
    }

    @Inject(method = "getRecipeLayoutUnderMouse", at = @At("HEAD"), cancellable = true, require = 0)
    private void hk3gtl$clipRecipeLookup(double mouseX, double mouseY, CallbackInfoReturnable<Optional<?>> cir) {
        if (!hk3gtl$isVisible(mouseX, mouseY)) cir.setReturnValue(Optional.empty());
    }

    @Inject(method = "mouseMoved", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$clipMouseMoved(double mouseX, double mouseY, CallbackInfo ci) {
        if (!hk3gtl$isVisible(mouseX, mouseY)) ci.cancel();
    }

    @Inject(method = "mouseDragged", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$clipMouseDrag(double mouseX, double mouseY, InputConstants.Key key, double dx, double dy,
                                        CallbackInfoReturnable<Boolean> cir) {
        if (!hk3gtl$isVisible(mouseX, mouseY)) cir.setReturnValue(false);
    }

    @Unique
    private boolean hk3gtl$isVisible(double mouseX, double mouseY) {
        return hk3gtl$maxScroll == 0 || hk3gtl$viewport.contains(mouseX, mouseY);
    }
}
