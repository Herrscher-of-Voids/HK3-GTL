package com.sirin.hk3gtl.client.compat;

import com.lowdragmc.lowdraglib.gui.widget.SlotWidget;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.lowdragmc.lowdraglib.jei.ClickableIngredient;
import com.sirin.hk3gtl.client.preview.Hk3PreviewFullscreenScreen;
import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.gui.handlers.IGlobalGuiHandler;
import mezz.jei.api.gui.handlers.IGuiProperties;
import mezz.jei.api.registration.IGuiHandlerRegistration;
import mezz.jei.api.runtime.IClickableIngredient;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.common.MinecraftForge;

import java.lang.ref.WeakReference;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/** 异步材料槽直接提供给 JEI 焦点源，书签和查配方继续使用玩家绑定的按键。 */
@JeiPlugin
public final class Hk3PreviewJeiPlugin implements IModPlugin, IGlobalGuiHandler {
    private record Presented(WeakReference<WidgetGroup> preview, int x, int y) {}
    private static final List<Presented> VISIBLE = new ArrayList<>();
    private static WeakReference<Screen> owner = new WeakReference<>(null);

    @Override public ResourceLocation getPluginUid() { return new ResourceLocation("hk3gtl", "preview_materials"); }

    @Override public void registerGuiHandlers(IGuiHandlerRegistration registration) {
        registration.addGlobalGuiHandler(this);
        registration.addGuiScreenHandler(Hk3PreviewFullscreenScreen.class,
                screen -> new FullscreenProperties(Minecraft.getInstance().getWindow().getGuiScaledWidth(),
                        Minecraft.getInstance().getWindow().getGuiScaledHeight()));
        MinecraftForge.EVENT_BUS.addListener((ScreenEvent.Render.Pre event) -> VISIBLE.clear());
    }

    public static void present(WidgetGroup preview) {
        present(preview, 0, 0);
    }

    public static void present(WidgetGroup preview, GuiGraphics graphics) {
        // JEI 以矩阵平移配方，组件与原生材料槽仍使用页内坐标。
        var matrix = graphics.pose().last().pose();
        present(preview, Math.round(matrix.m30()), Math.round(matrix.m31()));
    }

    private static void present(WidgetGroup preview, int x, int y) {
        owner = new WeakReference<>(Minecraft.getInstance().screen);
        VISIBLE.add(new Presented(new WeakReference<>(preview), x, y));
    }

    @Override public Optional<IClickableIngredient<?>> getClickableIngredientUnderMouse(double mouseX, double mouseY) {
        if (Minecraft.getInstance().screen != owner.get()) return Optional.empty();
        for (int i = VISIBLE.size() - 1; i >= 0; i--) {
            var shown = VISIBLE.get(i);
            var preview = shown.preview().get();
            if (preview == null) continue;
            var ingredient = ingredientAt(preview, mouseX - shown.x(), mouseY - shown.y());
            if (ingredient.isPresent()) return Optional.of(translate(ingredient.get(), shown.x(), shown.y()));
        }
        return Optional.empty();
    }

    private static <T> IClickableIngredient<T> translate(IClickableIngredient<T> ingredient, int x, int y) {
        var area = ingredient.getArea();
        return new ClickableIngredient<>(ingredient.getTypedIngredient(), area.getX() + x, area.getY() + y,
                area.getWidth(), area.getHeight());
    }

    private static Optional<IClickableIngredient<?>> ingredientAt(Widget widget, double mouseX, double mouseY) {
        var pos = widget.getPosition();
        var size = widget.getSize();
        if (!widget.isVisible() || !Widget.isMouseOver(pos.x, pos.y, size.width, size.height, mouseX, mouseY))
            return Optional.empty();
        if (widget instanceof SlotWidget slot) {
            var ingredient = slot.getXEIIngredientOverMouse(mouseX, mouseY);
            if (ingredient instanceof IClickableIngredient<?> clickable) return Optional.of(clickable);
            if (ingredient instanceof List<?> cycle)
                for (var candidate : cycle)
                    if (candidate instanceof IClickableIngredient<?> clickable) return Optional.of(clickable);
        }
        if (widget instanceof WidgetGroup group)
            for (int i = group.widgets.size() - 1; i >= 0; i--) {
                var ingredient = ingredientAt(group.widgets.get(i), mouseX, mouseY);
                if (ingredient.isPresent()) return ingredient;
            }
        return Optional.empty();
    }

    private record FullscreenProperties(int width, int height) implements IGuiProperties {
        @Override public Class<? extends Screen> getScreenClass() { return Hk3PreviewFullscreenScreen.class; }
        @Override public int getGuiLeft() { return 8; }
        @Override public int getGuiTop() { return 8; }
        @Override public int getGuiXSize() { return width - 16; }
        @Override public int getGuiYSize() { return height - 16; }
        @Override public int getScreenWidth() { return width; }
        @Override public int getScreenHeight() { return height; }
    }
}
