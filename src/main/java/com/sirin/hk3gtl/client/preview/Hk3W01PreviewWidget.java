package com.sirin.hk3gtl.client.preview;

import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.lowdragmc.lowdraglib.gui.editor.ColorPattern;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.*;
import com.lowdragmc.lowdraglib.jei.IngredientIO;
import com.lowdragmc.lowdraglib.utils.CycleItemStackHandler;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallPattern;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01PreviewIndex;
import com.sirin.hk3gtl.mixin.gtceu.Hk3PreviewCacheAccessor;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 【文件职责】原生GT JEI分类内的W01完整MC模型场景、全部材料、旋转缩放与逐层浏览。
 * 【变更记录 #1】2026-10-29 23:12:35（第1次备注 · 本轮高度与预览修复）
 * 删除：无；新增：仅显示时创建稀疏场景并沿LDLib后台VBO缓存烘焙；修改：无。
 * 用途：保留全部1933767格及其原坐标，绕开密集数组和重复方块对象；不替换终端搭建。
 */
/** 【变更记录 #2】2026-10-29 23:18:13（第2次备注 · 本轮高度与预览修复）：删除对玩家世界零坐标的材料取样；新增完整只读视图共用；修改拾取为每状态首个真实坐标；用途为材料清单与实际预览一致，不依赖该位置的真实世界方块实体。 */
public final class Hk3W01PreviewWidget extends WidgetGroup {
    private final MultiblockMachineDefinition definition;
    private final Hk3W01HallLayout layout;
    private final Hk3W01PreviewIndex index;
    private final BlockState[] states;
    private final Hk3W01PreviewWorld fullWorld;
    private SparseScene scene;
    private int layer = -1;

    public Hk3W01PreviewWidget(MultiblockMachineDefinition definition) {
        this(definition, Hk3W01HallPattern.layout(), w01States(definition), Direction.WEST, Map.of());
    }

    /** 显式测试入口共用真实MC场景，状态、坐标和方块实体均来自原蓝图。 */
    public Hk3W01PreviewWidget(MultiblockMachineDefinition definition, Hk3W01HallLayout layout,
            BlockState[] states, Direction front, Map<Long, CompoundTag> entities) {
        super(0, 0, 160, 160);
        setClientSideWidget();
        this.definition = definition;
        this.layout = layout;
        this.index = new Hk3W01PreviewIndex(layout);
        this.states = states;
        fullWorld = new Hk3W01PreviewWorld(definition, layout, index, states, -1, front, entities);
        addWidget(new ImageWidget(3, 3, 154, 10,
                new TextTexture(definition.getDescriptionId(), -1).setType(TextTexture.TextType.ROLL).setWidth(154).setDropShadow(true)));
        button(104, "−", () -> changeLayer(layer <= 0 ? -1 : layer - 1));
        button(122, "ALL", () -> changeLayer(-1));
        button(140, "+", () -> changeLayer(layer + 1 >= layout.height() ? -1 : layer + 1));
        addWidget(new ImageWidget(3, 118, 99, 10, new TextTexture(() -> layer < 0
                ? Component.translatable("hk3gtl.w01.preview.all", layout.cells().length).getString()
                : "Y=" + layer + " / " + (layout.height() - 1)).setWidth(99)));
        materials();
    }

    private static BlockState[] w01States(MultiblockMachineDefinition definition) {
        var pattern = new Hk3W01HallPattern(definition);
        var result = new BlockState[Hk3W01HallPattern.layout().palette().size()];
        for (int i = 0; i < result.length; i++) result[i] = pattern.expectedState(i, 0);
        return result;
    }

    private void button(int x, String text, Runnable action) {
        addWidget(new ButtonWidget(x, 116, 17, 14, new GuiTextureGroup(ColorPattern.T_GRAY.rectTexture(),
                new TextTexture(text)), click -> action.run()).setHoverBorderTexture(1, -1));
    }

    private void materials() {
        Map<Item, ItemStack> materials = new LinkedHashMap<>();
        materials.put(definition.asStack().getItem(), definition.asStack());
        int controllerPalette = index.stateAt(layout.controllerX(), layout.controllerY(), layout.controllerZ());
        for (int i = 0; i < states.length; i++) {
            int amount = index.countMaterial(i) - (i == controllerPalette ? 1 : 0);
            if (amount == 0) continue;
            long sample = index.firstCell(i);
            BlockPos pos = new BlockPos(Hk3W01HallLayout.x(sample), Hk3W01HallLayout.y(sample), Hk3W01HallLayout.z(sample));
            ItemStack stack = states[i].getBlock().getCloneItemStack(fullWorld, pos, states[i]);
            if (stack.isEmpty()) continue;
            ItemStack existing = materials.get(stack.getItem());
            if (existing == null) { stack.setCount(amount); materials.put(stack.getItem(), stack); }
            else existing.grow(amount);
        }
        List<List<ItemStack>> parts = new ArrayList<>();
        materials.values().forEach(stack -> parts.add(List.of(stack)));
        var items = new CycleItemStackHandler(parts);
        var scroll = new DraggableScrollableWidgetGroup(3, 132, 154, 22)
                .setXScrollBarHeight(4).setXBarStyle(GuiTextures.SLIDER_BACKGROUND, GuiTextures.BUTTON)
                .setScrollable(true).setDraggable(true);
        scroll.setScrollWheelDirection(DraggableScrollableWidgetGroup.ScrollWheelDirection.HORIZONTAL);
        for (int i = 0; i < parts.size(); i++) scroll.addWidget(new SlotWidget(items, i, 4 + i * 18, 0, false, false)
                .setBackgroundTexture(ColorPattern.T_GRAY.rectTexture()).setIngredientIO(IngredientIO.INPUT));
        addWidget(scroll);
    }

    private void changeLayer(int next) {
        layer = next;
        if (scene != null) {
            scene.releaseCacheBuffer();
            removeWidget(scene);
            scene = null;
        }
    }

    /** 仅供原型测试页记录真实缓存状态和释放；不更改蓝图。 */
    public void testLayer(int next) {
        if (next < -1 || next >= layout.height()) throw new IllegalArgumentException("预览层越界");
        changeLayer(next);
    }

    public boolean testReady() {
        return scene != null && "COMPILED".equals(String.valueOf(
                ((Hk3PreviewCacheAccessor) scene.getRenderer()).hk3gtl$cacheState().get()));
    }

    public double testProgress() { return scene == null ? 0 : testReady() ? 1 : scene.getRenderer().getCompileProgress(); }

    public void closePreview() {
        if (scene != null) { scene.releaseCacheBuffer(); removeWidget(scene); scene = null; }
    }

    @Override public void drawInBackground(GuiGraphics graphics, int mouseX, int mouseY, float partialTicks) {
        // JEI注册所有配方时只统计材料；真正打开本页才申请VBO，后台线程逐模型烘焙。
        if (scene == null) {
            scene = new SparseScene(layer < 0 ? fullWorld : new Hk3W01PreviewWorld(definition, layout, index, states,
                    layer, fullWorld.front, fullWorld.entities));
            addWidget(0, scene);
        }
        super.drawInBackground(graphics, mouseX, mouseY, partialTicks);
    }

    private static final class SparseScene extends SceneWidget {
        SparseScene(Hk3W01PreviewWorld world) {
            super(3, 16, 154, 100, world);
            setClientSideWidget();
            setRenderFacing(false);
            core = world.positions();
            renderer.addRenderedBlocks(core, null);
            center = new Vector3f(world.layout.width() / 2f,
                    world.layer < 0 ? world.layout.height() / 2f : world.layer + 0.5f, world.layout.depth() / 2f);
            setCenter(center);
            setZoom(Math.max(world.layout.width(), world.layout.depth()) * 2.2f);
            setCameraYawAndPitch(25, -135);
            // LDLib的正常场景缓存后台编译；不每帧重画193万模型，也不在JEI注册阶段烘焙。
            useCacheBuffer();
        }

        @Override public boolean mouseWheelMove(double mouseX, double mouseY, double delta) {
            if (!isMouseOverElement(mouseX, mouseY) || delta == 0) return super.mouseWheelMove(mouseX, mouseY, delta);
            // 原组件滚轮把距离截到999，会令大型礼堂第一次缩放突然跳进建筑。
            setZoom((float) Math.max(1, Math.min(20_000, zoom * Math.pow(0.9, delta))));
            return true;
        }
    }
}
