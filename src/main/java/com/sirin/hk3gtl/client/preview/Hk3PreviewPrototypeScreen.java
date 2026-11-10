package com.sirin.hk3gtl.client.preview;

import com.sirin.hk3gtl.common.machine.Hk3LateIndustrialMachines;
import com.sirin.hk3gtl.common.machine.Hk3W01Machines;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3PreviewPrototype;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

import java.lang.management.BufferPoolMXBean;
import java.lang.management.ManagementFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;

/** 只在测试开关启用且已进入独立测试世界后按F8打开的原生MC预览试验台。 */
@Mod.EventBusSubscriber(modid = "hk3gtl", value = Dist.CLIENT)
public final class Hk3PreviewPrototypeScreen extends Screen {
    private final Screen parent;
    private Hk3W01PreviewWidget preview;
    private String id = "w01";
    private int layer = -1;
    private long began;
    private long readyAt;
    private int frames;
    private int step = -1;
    private final List<String> samples = new ArrayList<>();
    private String status = "原型：完整MC模型；旋转、缩放和逐层浏览";

    private Hk3PreviewPrototypeScreen(Screen parent) {
        super(Component.literal("HK3GTL独立预览原型测试"));
        this.parent = parent;
    }

    @SubscribeEvent public static void open(ScreenEvent.KeyPressed.Pre event) {
        if (Boolean.getBoolean(Hk3PreviewPrototype.PROPERTY) && Minecraft.getInstance().level != null
                && event.getKeyCode() == GLFW.GLFW_KEY_F8
                && !(event.getScreen() instanceof Hk3PreviewPrototypeScreen)) {
            Minecraft.getInstance().setScreen(new Hk3PreviewPrototypeScreen(event.getScreen()));
            event.setCanceled(true);
        }
    }

    @Override protected void init() {
        addRenderableWidget(Button.builder(Component.literal("W01"), b -> choose("w01")).bounds(8, 6, 45, 18).build());
        addRenderableWidget(Button.builder(Component.literal("I34"), b -> choose("i34")).bounds(56, 6, 45, 18).build());
        addRenderableWidget(Button.builder(Component.literal("轮测并截图"), b -> { samples.clear(); step = 0; choose("w01"); })
                .bounds(104, 6, 90, 18).build());
        addRenderableWidget(Button.builder(Component.literal("返回"), b -> onClose()).bounds(width - 52, 6, 45, 18).build());
        choose(id);
    }

    private void choose(String next) {
        if (preview != null) preview.closePreview();
        id = next;
        layer = -1;
        if (id.equals("w01")) preview = new Hk3W01PreviewWidget(Hk3W01Machines.HALL);
        else {
            var data = Hk3PreviewPrototype.i34();
            BlockState[] states = data.layout().palette().stream().map(Hk3LargeArchitectureShapes::state).toArray(BlockState[]::new);
            preview = new Hk3W01PreviewWidget(Hk3LateIndustrialMachines.get("i34"), data.layout(), states,
                    Direction.NORTH, data.entities());
        }
        preview.setSelfPosition((width - 160) / 2, (height - 160) / 2);
        preview.initWidget();
        began = System.nanoTime(); readyAt = 0; frames = 0;
    }

    @Override public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTicks) {
        graphics.fill(0, 0, width, height, 0xff111824);
        super.render(graphics, mouseX, mouseY, partialTicks);
        preview.drawInBackground(graphics, mouseX, mouseY, partialTicks);
        preview.drawInForeground(graphics, mouseX, mouseY, partialTicks);
        long now = System.nanoTime();
        if (preview.testReady()) {
            if (readyAt == 0) readyAt = now;
            frames++;
        }
        var memory = ManagementFactory.getMemoryMXBean().getHeapMemoryUsage();
        graphics.drawString(font, id.toUpperCase() + " · Y=" + layer + " · 缓存 "
                + String.format(java.util.Locale.ROOT, "%.1f%%", preview.testProgress() * 100)
                + " · 堆 " + memory.getUsed() / 1048576 + "MiB", 8, height - 28, 0xffd7edf9);
        graphics.drawString(font, status, 8, height - 15, 0xff9fb5ca);
        if (step >= 0 && readyAt != 0 && now - readyAt >= 5_000_000_000L) finishStep(now);
    }

    private void finishStep(long now) {
        long direct = ManagementFactory.getPlatformMXBeans(BufferPoolMXBean.class).stream()
                .filter(pool -> pool.getName().equals("direct")).mapToLong(BufferPoolMXBean::getMemoryUsed).sum();
        samples.add(String.format(java.util.Locale.ROOT,
                "{\"id\":\"%s\",\"layer\":%d,\"bake_ms\":%.1f,\"mean_fps_5s\":%.2f,\"heap_used_bytes\":%d,\"direct_buffer_bytes\":%d}",
                id, layer, (readyAt - began) / 1e6, frames * 1e9 / (now - readyAt),
                ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getUsed(), direct));
        Screenshot.grab(minecraft.gameDirectory, "hk3gtl-preview-prototype-" + step + ".png",
                minecraft.getMainRenderTarget(), message -> {});
        step++;
        if (step == 1 || step == 3) {
            layer = id.equals("w01") ? 150 : 80;
            preview.testLayer(layer);
            began = System.nanoTime(); readyAt = 0; frames = 0;
        } else if (step == 2) choose("i34");
        else {
            step = -1;
            status = "轮测完成：两座全景与逐层图；结果已保存至游戏目录";
            try {
                Files.writeString(minecraft.gameDirectory.toPath().resolve("hk3gtl-preview-prototype-results.json"),
                        "[\n" + String.join(",\n", samples) + "\n]\n", StandardCharsets.UTF_8);
            } catch (java.io.IOException failure) { throw new IllegalStateException("预览测试结果保存失败", failure); }
        }
    }

    @Override public void tick() { if (preview != null) preview.updateScreen(); }
    @Override public boolean mouseClicked(double x, double y, int button) {
        return super.mouseClicked(x, y, button) || preview.mouseClicked(x, y, button);
    }
    @Override public boolean mouseReleased(double x, double y, int button) {
        return preview.mouseReleased(x, y, button) || super.mouseReleased(x, y, button);
    }
    @Override public boolean mouseDragged(double x, double y, int button, double dx, double dy) {
        return preview.mouseDragged(x, y, button, dx, dy) || super.mouseDragged(x, y, button, dx, dy);
    }
    @Override public boolean mouseScrolled(double x, double y, double delta) {
        return preview.mouseWheelMove(x, y, delta) || super.mouseScrolled(x, y, delta);
    }
    @Override public void removed() { if (preview != null) preview.closePreview(); }
    @Override public void onClose() { minecraft.setScreen(parent); }
}
