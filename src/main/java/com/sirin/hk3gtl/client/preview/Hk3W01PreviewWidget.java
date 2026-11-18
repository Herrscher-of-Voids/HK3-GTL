package com.sirin.hk3gtl.client.preview;

import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.lowdragmc.lowdraglib.gui.editor.ColorPattern;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.*;
import com.lowdragmc.lowdraglib.client.scene.WorldSceneRenderer;
import com.lowdragmc.lowdraglib.jei.IngredientIO;
import com.lowdragmc.lowdraglib.utils.CycleItemStackHandler;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallPattern;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01PreviewIndex;
import com.sirin.hk3gtl.client.wonder.Hk3W03FxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W08FxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W10FxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W12FxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W11FxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W11FxModel;
import com.sirin.hk3gtl.client.wonder.Hk3W13FxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W13FxModel;
import com.sirin.hk3gtl.client.wonder.Hk3W07SceneModel;
import com.sirin.hk3gtl.client.wonder.Hk3W07SceneRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W07FxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W14SceneModel;
import com.sirin.hk3gtl.client.wonder.Hk3W14SceneRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W14FxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W15SceneModel;
import com.sirin.hk3gtl.client.wonder.Hk3W15SceneRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3W15FxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3WonderFxRenderer;
import com.sirin.hk3gtl.client.wonder.Hk3WonderFxScenes;
import com.sirin.hk3gtl.client.tree.Hk3TreeProjectionRenderer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.EmptyBlockGetter;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.AbstractCollection;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class Hk3W01PreviewWidget extends WidgetGroup {
    private static final java.util.concurrent.ExecutorService MESHER = java.util.concurrent.Executors.newSingleThreadExecutor(task -> {
        var thread = new Thread(task, "hk3gtl-preview-mesh");
        thread.setDaemon(true);
        return thread;
    });
    private final MultiblockMachineDefinition definition;
    private final Hk3W01HallLayout layout;
    private final Hk3W01PreviewIndex index;
    private final BlockState[] states;
    private final Hk3W01PreviewWorld fullWorld;
    private SparseScene scene;
    private SparseScene movingScene;
    private java.util.concurrent.Future<Hk3PreviewGreedyMesh.Prepared> meshing;
    private Hk3PreviewGreedyMesh mesh;
    private int[] fallbackCells;
    private java.util.concurrent.CompletableFuture<Hk3PreviewGreedyMesh.Prepared> animationMeshing;
    private Hk3PreviewGreedyMesh animationMesh;
    private int[] animationFallback;
    private final List<ButtonWidget> layerButtons = new ArrayList<>();
    private ImageWidget title;
    private ImageWidget layerText;
    private DraggableScrollableWidgetGroup materialBar;
    private ButtonWidget animationButton;
    private ButtonWidget fullscreenButton;
    private Runnable keepAlive = () -> {};
    private boolean effectsEnabled;
    private long animationStart;
    private String sampleMode = "";
    private long sampleStart;
    private int sampleFrames;
    private int layer = -1;

    public Hk3W01PreviewWidget(MultiblockMachineDefinition definition) {
        this(definition, Hk3W01HallPattern.layout(), w01States(definition), Direction.WEST, Map.of());
    }

    /** 显式测试入口共用真实MC场景，状态、坐标和方块实体均来自原蓝图。 */
    public Hk3W01PreviewWidget(MultiblockMachineDefinition definition, Hk3W01HallLayout layout,
            BlockState[] states, Direction front, Map<Long, CompoundTag> entities) {
        this(definition, layout, states, front, entities, prepareIndex(layout, states));
    }

    static Hk3W01PreviewIndex prepareIndex(Hk3W01HallLayout layout, BlockState[] states) {
        boolean[] entityStates = new boolean[states.length];
        boolean[] opaqueStates = new boolean[states.length];
        for (int i = 0; i < states.length; i++) {
            var state = states[i];
            entityStates[i] = state.hasBlockEntity();
            opaqueStates[i] = state.canOcclude() && !state.getBlock().hasDynamicShape()
                    && state.isSolidRender(EmptyBlockGetter.INSTANCE, BlockPos.ZERO);
        }
        return new Hk3W01PreviewIndex(layout, entityStates, opaqueStates);
    }

    Hk3W01PreviewWidget(MultiblockMachineDefinition definition, Hk3W01HallLayout layout,
            BlockState[] states, Direction front, Map<Long, CompoundTag> entities, Hk3W01PreviewIndex index) {
        super(0, 0, 160, 160);
        setClientSideWidget();
        this.definition = definition;
        this.layout = layout;
        this.index = index;
        this.states = states;
        fullWorld = new Hk3W01PreviewWorld(definition, layout, index, states, -1, front, entities);
        title = new ImageWidget(3, 3, 154, 10,
                new TextTexture(definition.getDescriptionId(), -1).setType(TextTexture.TextType.ROLL).setWidth(154).setDropShadow(true));
        title.setHoverTooltips(Component.translatable("hk3gtl.preview.controls"),
                Component.translatable("hk3gtl.preview.interfaces"));
        addWidget(title);
        button(104, "−", () -> changeLayer(layer <= 0 ? -1 : layer - 1));
        button(122, "ALL", () -> changeLayer(-1));
        button(140, "+", () -> changeLayer(layer + 1 >= layout.height() ? -1 : layer + 1));
        layerText = new ImageWidget(3, 104, 154, 10, new TextTexture(() -> layer < 0
                ? Component.translatable("hk3gtl.w01.preview.all",hasSceneModel()?java.util.Arrays.stream(sceneMaterialCounts()).sum():layout.cells().length).getString()
                : "Y=" + layer + " / " + (layout.height() - 1)).setWidth(154));
        addWidget(layerText);
        animationButton = new ButtonWidget(3, 116, 43, 14, new GuiTextureGroup(ColorPattern.T_GRAY.rectTexture(),
                new TextTexture(() -> Component.translatable("hk3gtl.preview.animation." +
                        (hasAnimation() ? effectsEnabled ? "on" : "off" : "none")).getString())),
                click -> toggleAnimation());
        animationButton.setActive(hasAnimation());
        addWidget(animationButton);
        fullscreenButton = new ButtonWidget(49, 116, 49, 14, new GuiTextureGroup(ColorPattern.T_GRAY.rectTexture(),
                new TextTexture(() -> Component.translatable(Minecraft.getInstance().screen instanceof Hk3PreviewFullscreenScreen
                        ? "hk3gtl.preview.back" : "hk3gtl.preview.fullscreen").getString())),
                click -> Hk3PreviewFullscreenScreen.open(this, keepAlive));
        addWidget(fullscreenButton);
        materials();
    }

    private static BlockState[] w01States(MultiblockMachineDefinition definition) {
        var pattern = new Hk3W01HallPattern(definition);
        var result = new BlockState[Hk3W01HallPattern.layout().palette().size()];
        for (int i = 0; i < result.length; i++) result[i] = pattern.expectedState(i, 0);
        return result;
    }

    private void button(int x, String text, Runnable action) {
        var button = new ButtonWidget(x, 116, 17, 14, new GuiTextureGroup(ColorPattern.T_GRAY.rectTexture(),
                new TextTexture(text)), click -> action.run());
        button.setHoverBorderTexture(1, -1);
        layerButtons.add(button);
        addWidget(button);
    }

    private void materials() {
        Map<Item, ItemStack> materials = new LinkedHashMap<>();
        materials.put(definition.asStack().getItem(), definition.asStack());
        int controllerPalette = index.stateAt(layout.controllerX(), layout.controllerY(), layout.controllerZ());
        for (int i = 0; i < states.length; i++) {
            int amount = (hasSceneModel()?Math.toIntExact(sceneMaterialCounts()[i]):index.countMaterial(i)) - (i == controllerPalette ? 1 : 0);
            if (amount == 0) continue;
            long sample = hasSceneModel()?layout.cells()[0]:index.firstCell(i);
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
        var scroll = new DraggableScrollableWidgetGroup(3, 134, 154, 22)
                .setXScrollBarHeight(4).setXBarStyle(GuiTextures.SLIDER_BACKGROUND, GuiTextures.BUTTON)
                .setScrollable(true).setDraggable(true);
        scroll.setScrollWheelDirection(DraggableScrollableWidgetGroup.ScrollWheelDirection.HORIZONTAL);
        materialBar = scroll;
        materialBar.setHoverTooltips(Component.translatable("hk3gtl.preview.interfaces"));
        for (int i = 0; i < parts.size(); i++) scroll.addWidget(new SlotWidget(items, i, 4 + i * 18, 0, false, false)
                .setBackgroundTexture(ColorPattern.T_GRAY.rectTexture()).setIngredientIO(IngredientIO.INPUT));
        addWidget(scroll);
    }

    private void changeLayer(int next) {
        effectsEnabled = false;
        layer = next;
        if (movingScene != null) { movingScene.close(); removeWidget(movingScene); movingScene = null; }
        if (scene != null) {
            scene.close();
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
        if(hasSceneModel())return scene!=null&&(isW07()?Hk3W07SceneRenderer.ready():isW14()?Hk3W14SceneRenderer.ready():isW15()?Hk3W15SceneRenderer.ready():isW13()?Hk3W13FxRenderer.ready():Hk3W11FxRenderer.previewReady(layer))&&Hk3PreviewCacheBridge.isReady(scene.getRenderer());
        var visible = movingScene != null && movingScene.isVisible() ? movingScene : scene;
        return visible != null && Hk3PreviewCacheBridge.isReady(visible.getRenderer())
                && (visible == movingScene ? !partialMovingModel() || animationMesh != null && animationMesh.ready()
                        : layer >= 0 || mesh != null && mesh.ready());
    }

    public double testProgress() { return scene == null ? 0 : testReady() ? 1 : scene.getRenderer().getCompileProgress(); }

    public long cacheBytes() {
        if(hasSceneModel())return isW07()?Hk3W07SceneRenderer.vertexBytes():isW14()?Hk3W14SceneRenderer.vertexBytes():isW15()?Hk3W15SceneRenderer.vertexBytes():isW13()?Hk3W13FxRenderer.vertexBytes():Hk3W11FxRenderer.vertexBytes();
        return (scene == null ? 0 : Hk3PreviewCacheBridge.cacheBytes(scene.getRenderer()))
                + (movingScene == null ? 0 : Hk3PreviewCacheBridge.cacheBytes(movingScene.getRenderer()))
                + (mesh == null ? 0 : mesh.vertexBytes()) + (animationMesh == null ? 0 : animationMesh.vertexBytes());
    }

    public void closePreview() {
        if (scene != null) { scene.close(); removeWidget(scene); scene = null; }
        if (movingScene != null) { movingScene.close(); removeWidget(movingScene); movingScene = null; }
        if (mesh != null) { mesh.close(); mesh = null; }
        if (meshing != null) { meshing.cancel(true); meshing = null; }
        if (animationMesh != null) { animationMesh.close(); animationMesh = null; }
        if (animationMeshing != null) { animationMeshing.cancel(true); animationMeshing = null; }
    }

    public void setKeepAlive(Runnable keepAlive) { this.keepAlive = keepAlive; }

    public void fullscreenLease(boolean fullscreen) {
        if (scene != null) scene.useCacheBuffer(!fullscreen);
        if (movingScene != null) movingScene.useCacheBuffer(!fullscreen);
    }

    public void resizePreview(int width, int height) {
        setSize(width, height);
        title.setSizeWidth(width - 6);
        layerText.setSelfPositionY(height - 56);
        layerText.setSizeWidth(width - 6);
        animationButton.setSelfPositionY(height - 44);
        fullscreenButton.setSelfPositionY(height - 44);
        for (int i = 0; i < layerButtons.size(); i++) layerButtons.get(i).setSelfPosition(width - 56 + 18 * i, height - 44);
        materialBar.setSelfPositionY(height - 26);
        materialBar.setSizeWidth(width - 6);
        if (scene != null) scene.resize(width, height);
        if (movingScene != null) movingScene.resize(width, height);
    }

    private boolean isTree() { return definition.getId().getPath().equals("i34_imaginary_tree_observation_array"); }
    private boolean isW07(){return definition.getId().getPath().equals("w07_matter_regeneration_ark");}
    private boolean isW13(){return definition.getId().getPath().equals("w13_self_computing_research_mother");}
    private boolean isW14(){return definition.getId().getPath().equals("w14_world_bubble_recurrence_engine");}
    private boolean isW15(){return definition.getId().getPath().equals("w15_tree_sea_audience_throne");}
    private boolean isW11(){return definition.getId().getPath().equals("w11_distributed_industrial_command");}
    private boolean hasSceneModel(){return isW07()||isW14()||isW15()||isW13()||isW11();}
    private long[] sceneMaterialCounts(){return isW07()?Hk3W07SceneModel.loadMetadata().material_counts():isW14()?Hk3W14SceneModel.loadMetadata().material_counts():isW15()?Hk3W15SceneModel.loadMetadata().material_counts():isW13()?Hk3W13FxModel.loadMetadata().material_counts():Hk3W11FxModel.loadMetadata().material_counts();}
    private String partialRole(){return definition.getId().getPath().equals("w05_ideal_fluid_circulation_array")?"W05":"W06";}
    private boolean partialMovingModel(){return switch(definition.getId().getPath()){
        case "w05_ideal_fluid_circulation_array","w06_cryogenic_condensed_factory"->true;default->false;
    };}
    private boolean hasMovingModel() {
        return switch (definition.getId().getPath()) {
            case "void_anchor_ring", "w08_stellar_casting_furnace", "w10_gravitational_singularity_forge",
                    "w12_global_energy_constraint_wall", "w11_distributed_industrial_command", "w13_self_computing_research_mother", "w05_ideal_fluid_circulation_array", "w06_cryogenic_condensed_factory" -> true;
            default -> false;
        };
    }
    private boolean hasAnimation() { return isW07() || isW14() || isW15() || hasMovingModel() || isTree(); }
    private boolean prepareMovingModel() {
        return switch (definition.getId().getPath()) {
            case "void_anchor_ring" -> Hk3W03FxRenderer.preparePreview();
            case "w08_stellar_casting_furnace" -> Hk3W08FxRenderer.preparePreview();
            case "w10_gravitational_singularity_forge" -> Hk3W10FxRenderer.preparePreview();
            case "w12_global_energy_constraint_wall" -> Hk3W12FxRenderer.preparePreview();
            case "w05_ideal_fluid_circulation_array", "w06_cryogenic_condensed_factory" -> Hk3WonderFxRenderer.preparePreview(partialRole());
            default -> false;
        };
    }

    private boolean prepareAnimationStatic(){
        if(animationMesh==null){
            if(animationMeshing==null){
                String role=partialRole();
                var captured=Hk3PreviewGreedyMesh.capture(layout,index,states,fullWorld,pos->Hk3WonderFxScenes.hiddenPreview(role,pos));
                animationMeshing=java.util.concurrent.CompletableFuture.supplyAsync(()->Hk3PreviewGreedyMesh.prepare(captured),MESHER);
            }
            if(!animationMeshing.isDone())return false;
            var prepared=animationMeshing.join();animationFallback=prepared.fallbackCells();animationMesh=new Hk3PreviewGreedyMesh(prepared);
        }
        animationMesh.step(8192);return animationMesh.ready();
    }

    private void toggleAnimation() {
        if (layer >= 0) changeLayer(-1);
        effectsEnabled = !effectsEnabled;
        animationStart = System.nanoTime();
        if (movingScene != null && scene != null) {
            if (effectsEnabled) movingScene.copyCamera(scene);
            else scene.copyCamera(movingScene);
        }
        if (scene != null && !isTree()) scene.frame.invalidate();
        com.mojang.logging.LogUtils.getLogger().info("自家预览动画：{}，{}", definition.getId(), effectsEnabled ? "开启" : "关闭");
    }

    private void drawEffects(SparseScene target) {
        if (!effectsEnabled) return;
        double seconds = (System.nanoTime() - animationStart) / 1e9;
        switch (definition.getId().getPath()) {
            case "void_anchor_ring" -> Hk3W03FxRenderer.drawPreview(seconds);
            case "w08_stellar_casting_furnace" -> Hk3W08FxRenderer.drawPreview(seconds);
            case "w10_gravitational_singularity_forge" -> Hk3W10FxRenderer.drawPreview(seconds);
            case "w12_global_energy_constraint_wall" -> Hk3W12FxRenderer.drawPreview(seconds);
            case "w05_ideal_fluid_circulation_array", "w06_cryogenic_condensed_factory" -> Hk3WonderFxRenderer.drawPreview(partialRole(),seconds);
        }
        if (isTree()) {
            double scale = Minecraft.getInstance().getWindow().getGuiScale();
            Hk3TreeProjectionRenderer.drawPreview(seconds, (int) (target.getSizeWidth() * scale), (int) (target.getSizeHeight() * scale));
        }
    }

    @Override public void drawInBackground(GuiGraphics graphics, int mouseX, int mouseY, float partialTicks) {
        if(hasSceneModel()){
            if((isW07()?Hk3W07SceneRenderer.preparePreview():isW14()?Hk3W14SceneRenderer.preparePreview():isW15()?Hk3W15SceneRenderer.preparePreview():isW13()?Hk3W13FxRenderer.preparePreview():Hk3W11FxRenderer.preparePreview(layer))&&scene==null){
                scene=new SparseScene(layer<0?fullWorld:new Hk3W01PreviewWorld(definition,layout,index,states,layer,fullWorld.front,fullWorld.entities),false);
                scene.resize(getSizeWidth(),getSizeHeight());addWidget(0,scene);
            }
            super.drawInBackground(graphics,mouseX,mouseY,partialTicks);
            if(isW11()&&scene==null){
                var pos=getPosition();
                graphics.drawCenteredString(Minecraft.getInstance().font,Component.translatable(
                        Hk3W11FxRenderer.previewFailed(layer)?"hk3gtl.preview.w11.failed":"hk3gtl.preview.w11.loading"),
                        pos.x+getSizeWidth()/2,pos.y+getSizeHeight()/2-26,0xFFFFFF);
            }
            return;
        }
        if (mesh != null && !mesh.valid() || animationMesh != null && !animationMesh.valid()) {
            closePreview();
        }
        if (layer < 0 && mesh == null) {
            if (meshing == null) {
                var captured = Hk3PreviewGreedyMesh.capture(layout, index, states, fullWorld);
                meshing = MESHER.submit(() -> Hk3PreviewGreedyMesh.prepare(captured));
            }
            if (!meshing.isDone()) { super.drawInBackground(graphics, mouseX, mouseY, partialTicks); return; }
            Hk3PreviewGreedyMesh.Prepared prepared;
            try { prepared = meshing.get(); }
            catch (InterruptedException failure) {
                Thread.currentThread().interrupt();
                throw new java.util.concurrent.CompletionException(failure);
            } catch (java.util.concurrent.ExecutionException failure) {
                throw new java.util.concurrent.CompletionException(failure.getCause());
            }
            fallbackCells = prepared.fallbackCells();
            mesh = new Hk3PreviewGreedyMesh(prepared);
            com.mojang.logging.LogUtils.getLogger().info("自家预览合面：{}，原{}面，合并{}面，复杂模型回退{}格", definition.getId(),
                    prepared.sourceFaces(), prepared.mergedFaces(), fallbackCells.length);
        }
        if (mesh != null) mesh.step(8192);
        // JEI注册所有配方时只统计材料；真正打开本页才申请VBO，后台线程逐模型烘焙。
        if (scene == null) {
            scene = new SparseScene(layer < 0 ? fullWorld : new Hk3W01PreviewWorld(definition, layout, index, states,
                    layer, fullWorld.front, fullWorld.entities), false);
            scene.resize(getSizeWidth(), getSizeHeight());
            addWidget(0, scene);
        }
        boolean modelReady = effectsEnabled && hasMovingModel() && prepareMovingModel();
        if(modelReady&&partialMovingModel())modelReady=prepareAnimationStatic();
        if (modelReady && movingScene == null) {
            movingScene = new SparseScene(fullWorld, true);
            movingScene.copyCamera(scene);
            movingScene.resize(getSizeWidth(), getSizeHeight());
            addWidget(0, movingScene);
        }
        if (effectsEnabled && isTree()) Hk3TreeProjectionRenderer.preparePreview();
        boolean moving = modelReady && movingScene != null;
        scene.setVisible(!moving);
        scene.setActive(!moving);
        if (movingScene != null) { movingScene.setVisible(moving); movingScene.setActive(moving); }
        super.drawInBackground(graphics, mouseX, mouseY, partialTicks);
        sampleFrame();
    }

    private void sampleFrame() {
        if (!testReady()) return;
        String mode = (Minecraft.getInstance().screen instanceof Hk3PreviewFullscreenScreen ? "全屏" : "JEI")
                + (effectsEnabled ? "动画" : "静态") + "/" + layer;
        if (!mode.equals(sampleMode)) { sampleMode = mode; sampleStart = System.nanoTime(); sampleFrames = 0; }
        if (sampleStart == 0) return;
        sampleFrames++;
        long elapsed = System.nanoTime() - sampleStart;
        if (elapsed < 5_000_000_000L) return;
        com.mojang.logging.LogUtils.getLogger().info("自家预览模式采样：{}，{}，5秒均帧{}，几何{}KiB", definition.getId(),
                mode, sampleFrames * 1e9 / elapsed, cacheBytes() / 1024);
        sampleStart = 0;
    }

    private final class SparseScene extends SceneWidget {
        private final Hk3PreviewFrameCache frame = new Hk3PreviewFrameCache();
        private boolean renderedReady;
        private int dragButton = -1;
        SparseScene(Hk3W01PreviewWorld world, boolean portsOnly) {
            super(3, 16, 154, 88, world);
            getDummyWorld().setRenderFilter(null);
            setClientSideWidget();
            setRenderFacing(false);
            core = hasSceneModel() ? world.positions() : portsOnly && partialMovingModel() ? world.positions(animationFallback) : portsOnly ? java.util.stream.IntStream.of(-18, -14, -10, -6, 0, 6, 10, 14, 18)
                    .mapToObj(dx -> new BlockPos(layout.controllerX() + dx, layout.controllerY(), layout.controllerZ()))
                    .collect(java.util.stream.Collectors.toSet()) : world.layer < 0 ? world.positions(fallbackCells) : world.positions();
            renderer.addRenderedBlocks(new AbstractCollection<BlockPos>() {
                @Override public int size() { return core.size(); }
                @Override public Iterator<BlockPos> iterator() { return core.iterator(); }
            }, null);
            center = new Vector3f(world.layout.width() / 2f,
                    world.layer < 0 ? world.layout.height() / 2f : world.layer + 0.5f, world.layout.depth() / 2f);
            setCenter(center);
            setZoom(Math.max(world.layout.width(), world.layout.depth()) * (isW11() ? 1.65f : 1.1f));
            setCameraYawAndPitch(25, -135);
            // LDLib的正常场景缓存后台编译；不每帧重画193万模型，也不在JEI注册阶段烘焙。
            useCacheBuffer(!(Minecraft.getInstance().screen instanceof Hk3PreviewFullscreenScreen));
            renderer.setAfterWorldRender(ignored -> {
                if(hasSceneModel()){
                    double seconds=(System.nanoTime()-animationStart)/1e9;
                    if(isW07()){
                        Hk3W07SceneRenderer.drawPreview(layer,seconds,effectsEnabled&&layer<0);
                        if(effectsEnabled&&layer<0)Hk3W07FxRenderer.drawPreview(seconds);
                    }else if(isW14()){
                        Hk3W14SceneRenderer.drawPreview(layer);
                        if(effectsEnabled&&layer<0)Hk3W14FxRenderer.drawPreview(seconds);
                    }else if(isW15()){
                        Hk3W15SceneRenderer.drawPreview(layer);
                        if(effectsEnabled&&layer<0)Hk3W15FxRenderer.drawPreview(seconds);
                    }else if(isW13())Hk3W13FxRenderer.drawPreview(seconds,effectsEnabled,layer);
                    else Hk3W11FxRenderer.drawPreview(seconds,effectsEnabled,layer);
                    return;
                }
                if (!portsOnly && world.layer < 0 && mesh != null) mesh.draw(
                        new org.joml.Matrix4f(com.mojang.blaze3d.systems.RenderSystem.getModelViewMatrix()),
                        new org.joml.Matrix4f(com.mojang.blaze3d.systems.RenderSystem.getProjectionMatrix()));
                if(portsOnly&&partialMovingModel())animationMesh.draw(
                        new org.joml.Matrix4f(com.mojang.blaze3d.systems.RenderSystem.getModelViewMatrix()),
                        new org.joml.Matrix4f(com.mojang.blaze3d.systems.RenderSystem.getProjectionMatrix()));
                if (effectsEnabled && portsOnly) drawEffects(this);
                if (isTree() && testReady() && renderedReady) frame.captureScene();
            });
        }

        void resize(int width, int height) { setSize(width - 6, height - 72); frame.invalidate(); }
        void close() { frame.close(); renderer.deleteCacheBuffer(); }
        void copyCamera(SparseScene other) {
            setCenter(new Vector3f(other.center));
            setZoom(other.zoom);
            setCameraYawAndPitch(other.rotationYaw, other.rotationPitch);
            frame.invalidate();
        }

        @Override public void drawInBackground(GuiGraphics graphics, int mouseX, int mouseY, float partialTicks) {
            var pos = getPosition();
            if ((!effectsEnabled || isTree()) && frame.valid()) { drawFrame(graphics, pos.x, pos.y); return; }
            super.drawInBackground(graphics, mouseX, mouseY, partialTicks);
            boolean ready = testReady();
            if (isTree()) {
                if (frame.valid() && effectsEnabled) drawFrame(graphics, pos.x, pos.y);
            } else if (!effectsEnabled && ready && renderedReady) frame.capture(graphics, pos.x, pos.y, getSizeWidth(), getSizeHeight());
            renderedReady = ready;
        }

        private void drawFrame(GuiGraphics graphics, int x, int y) {
            if (isTree() && effectsEnabled && Hk3TreeProjectionRenderer.ready())
                frame.drawScene(graphics, x, y, getSizeWidth(), getSizeHeight(), () -> drawEffects(this));
            else frame.draw(graphics, x, y, getSizeWidth(), getSizeHeight());
        }

        @Override public boolean mouseClicked(double x, double y, int button) {
            if (!intractable || !draggable || button > 1 || !isMouseOverElement(x, y)) return false;
            dragButton = button;
            dragging = true;
            return true;
        }

        @Override public boolean mouseDragged(double x, double y, int button, double dx, double dy) {
            if (!intractable || !dragging || button != dragButton) return false;
            if (button == 0) super.mouseDragged(x, y, button, dx, dy);
            else {
                var forward = new Vector3f(renderer.getLookAt()).sub(renderer.getEyePos()).normalize();
                var right = new Vector3f(forward).cross(renderer.getWorldUp()).normalize();
                var up = new Vector3f(right).cross(forward);
                float scale = 2 * camZoom() * (float) Math.tan(Math.toRadians(renderer.getFov() / 2)) / getSizeHeight();
                setCenter(new Vector3f(center).fma((float) -dx * scale, right).fma((float) dy * scale, up));
            }
            frame.invalidate();
            return true;
        }

        @Override public boolean mouseReleased(double x, double y, int button) {
            if (button != dragButton) return false;
            dragButton = -1;
            dragging = false;
            return true;
        }

        // LDLib的未命中回退逐帧遍历整机；预览只保留拖转、缩放及独立材料栏。
        @Override public void renderBlockOverLay(WorldSceneRenderer renderer) {}

        @Override public boolean mouseWheelMove(double mouseX, double mouseY, double delta) {
            if (!isMouseOverElement(mouseX, mouseY) || delta == 0) return super.mouseWheelMove(mouseX, mouseY, delta);
            // 原组件滚轮把距离截到999，会令大型礼堂第一次缩放突然跳进建筑。
            setZoom((float) Math.max(1, Math.min(20_000, zoom * Math.pow(0.9, delta))));
            frame.invalidate();
            return true;
        }
    }
}
