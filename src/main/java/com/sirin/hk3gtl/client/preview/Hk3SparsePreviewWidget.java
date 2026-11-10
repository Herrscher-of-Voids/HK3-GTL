package com.sirin.hk3gtl.client.preview;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.sirin.hk3gtl.common.multiblock.pattern.*;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.level.block.state.BlockState;
import java.util.concurrent.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.HashSet;
import java.util.Set;

/** 首次显示才解码；百万方块不在JEI注册时展开或申请显存。 */
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3SparsePreviewWidget extends WidgetGroup {
    private static final ExecutorService LOADER=new ThreadPoolExecutor(1,1,30,TimeUnit.SECONDS,new ArrayBlockingQueue<>(2),task->{
        var thread=new Thread(task,"hk3gtl-preview-load");thread.setDaemon(true);thread.setPriority(Thread.NORM_PRIORITY-1);return thread;
    },new ThreadPoolExecutor.AbortPolicy());
    private static final Set<Hk3SparsePreviewWidget> OPEN=new HashSet<>();
    private final MultiblockMachineDefinition definition;
    private Future<Hk3SparsePreviewData.Data> loading;
    private Hk3W01PreviewWidget preview;
    private long lastDraw;
    private boolean attached;
    public Hk3SparsePreviewWidget(MultiblockMachineDefinition definition) {
        super(0,0,160,160);this.definition=definition;setClientSideWidget();
        addWidget(new LabelWidget(4,70,"hk3gtl.preview.loading"));
    }
    @Override public void drawInBackground(GuiGraphics graphics,int mouseX,int mouseY,float partialTicks) {
        lastDraw=System.nanoTime();OPEN.add(this);
        if(!attached && loading==null) {
            try { loading=LOADER.submit(()->Hk3SparsePreviewData.load(definition)); }
            catch(RejectedExecutionException busy) { super.drawInBackground(graphics,mouseX,mouseY,partialTicks);return; }
        }
        if(!attached && loading.isDone()) {
            attached=true;clearAllWidgets();
            try {
                var data=loading.get();
                BlockState[] states=data.layout().palette().stream().map(Hk3LargeArchitectureShapes::state).toArray(BlockState[]::new);
                preview=new Hk3W01PreviewWidget(definition,data.layout(),states,data.front(),data.entities());addWidget(preview);
            }catch(InterruptedException failure) {
                Thread.currentThread().interrupt();addWidget(new LabelWidget(4,70,"hk3gtl.preview.failed"));
            }catch(ExecutionException|RuntimeException failure) {
                com.mojang.logging.LogUtils.getLogger().error("自家完整预览失败：{}",definition.getId(),failure);
                addWidget(new LabelWidget(4,70,"hk3gtl.preview.failed"));
            }finally { loading=null; }
        }
        super.drawInBackground(graphics,mouseX,mouseY,partialTicks);
    }
    @SubscribeEvent public static void expire(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        long now=System.nanoTime();
        OPEN.removeIf(widget->{
            if(now-widget.lastDraw<2_000_000_000L)return false;
            if(widget.loading!=null)widget.loading.cancel(true);
            if(widget.preview!=null)widget.preview.closePreview();
            widget.loading=null;widget.preview=null;widget.attached=false;widget.clearAllWidgets();
            widget.addWidget(new LabelWidget(4,70,"hk3gtl.preview.loading"));return true;
        });
    }
}
