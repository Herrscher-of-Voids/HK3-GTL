package com.sirin.hk3gtl.common.integration.ae.nexus.ui;

import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.ResourceTexture;
import com.lowdragmc.lowdraglib.gui.texture.IGuiTexture;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.gui.widget.TextFieldWidget;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

import java.util.function.Supplier;

public final class Hk3NexusTheme {
    public static final int TEXT = 0xffdceafa;
    public static final int ACCENT = 0xff73f5e8;
    public static final IGuiTexture BUTTON = frame(0xff26394f, 0xff587b96, 0xff111d2d, true);
    public static final IGuiTexture FIELD = frame(0xff142236, 0xff486b82, 0xff0b1422, false);
    public static final IGuiTexture SLOT = frame(0xff293b50, 0xff718aa3, 0xff111d2b, false);
    public static final IGuiTexture BACKGROUND = new IGuiTexture() {
        private final ResourceTexture chassis = new ResourceTexture("hk3gtl:textures/gui/nexus/background_r8.png");

        @OnlyIn(Dist.CLIENT)
        @Override public void draw(GuiGraphics graphics, int mouseX, int mouseY, float x, float y, int width, int height) {
            int left = (int) x;
            int top = (int) y;
            chassis.draw(graphics, mouseX, mouseY, x, y, width, height);
            bevel(graphics, left + 12, top + 60, width - 24, 217, 0xf3112031, 0xff56c9d3, 0xff302a53);
            bevel(graphics, left + 87, top + 277, 176, 79, 0xff1a2b3d, 0xff7192aa, 0xff101a29);
            graphics.fill(left + 17, top + 32, left + 174, top + 33, 0xff34cbd1);
            graphics.fill(left + 174, top + 32, left + width - 17, top + 33, 0xff9e70e9);
            graphics.fill(left + 17, top + 33, left + 174, top + 34, 0xff172b3d);
            graphics.fill(left + 174, top + 33, left + width - 17, top + 34, 0xff302548);
            graphics.fill(left + 316, top + 12, left + 319, top + 15, 0xff54f2c7);
            graphics.fill(left + 322, top + 12, left + 325, top + 15, 0xffe6b75a);
            graphics.fill(left + 328, top + 12, left + 331, top + 15, 0xffc17df0);
        }
    };

    private Hk3NexusTheme() {}

    public static IGuiTexture button(String text) {
        return new GuiTextureGroup(BUTTON, new TextTexture(text, TEXT).setDropShadow(false));
    }

    public static IGuiTexture tab(String text, int accent, boolean selected) {
        IGuiTexture plate = new IGuiTexture() {
            @OnlyIn(Dist.CLIENT)
            @Override public void draw(GuiGraphics graphics, int mouseX, int mouseY, float x, float y, int width, int height) {
                boolean active = selected || mouseX >= x && mouseX < x + width && mouseY >= y && mouseY < y + height;
                int fill = selected ? 0xff19364b : 0xff243449;
                int shade = selected ? 0xff18334a : 0xff101b2a;
                bevel(graphics, (int) x, (int) y, width, height, fill,
                        active ? 0xffd8ffff : 0xff66839b, shade);
                graphics.fill((int) x + 2, (int) y + height - (selected ? 3 : 2),
                        (int) x + width - 2, (int) y + height - 1, accent);
                if (active) graphics.fill((int) x + 2, (int) y + 1, (int) x + width - 2, (int) y + 2, accent);
            }
        };
        return new GuiTextureGroup(plate, new TextTexture(text, selected ? 0xffffffff : TEXT).setDropShadow(false));
    }

    public static LabelWidget label(int x, int y, String text) {
        return new LabelWidget(x, y, text).setTextColor(TEXT).setDropShadow(false);
    }

    public static LabelWidget label(int x, int y, Supplier<String> text) {
        return new LabelWidget(x, y, text).setTextColor(TEXT).setDropShadow(false);
    }

    public static TextFieldWidget field(TextFieldWidget field) {
        return field.setBackground(FIELD).setTextColor(0xffeff8ff);
    }

    private static IGuiTexture frame(int fill, int light, int shade, boolean hoverable) {
        return new IGuiTexture() {
            @OnlyIn(Dist.CLIENT)
            @Override public void draw(GuiGraphics graphics, int mouseX, int mouseY, float x, float y, int width, int height) {
                boolean hover = hoverable && mouseX >= x && mouseX < x + width && mouseY >= y && mouseY < y + height;
                bevel(graphics, (int) x, (int) y, width, height, hover ? 0xff17516a : fill,
                        hover ? 0xff9affed : light, hover ? 0xff0b3346 : shade);
            }
        };
    }

    @OnlyIn(Dist.CLIENT)
    private static void bevel(GuiGraphics graphics, int x, int y, int width, int height, int fill, int light, int shade) {
        graphics.fill(x, y, x + width, y + height, fill);
        graphics.fill(x, y, x + width, y + 1, light);
        graphics.fill(x, y + 1, x + 1, y + height, light);
        graphics.fill(x + 1, y + height - 2, x + width, y + height, shade);
        graphics.fill(x + width - 1, y + 1, x + width, y + height, shade);
    }
}
