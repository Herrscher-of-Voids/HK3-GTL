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
    private record Prepared(MultiblockMachineDefinition definition,Hk3SparsePreviewData.Data data,
                            BlockState[] states,Hk3W01PreviewIndex index) {}
    private static Prepared cached;
    private static Hk3SparsePreviewWidget warm;
    private final MultiblockMachineDefinition definition;
    private final Runnable onShown;
    private Future<Prepared> loading;
    private Hk3W01PreviewWidget preview;
    private long lastDraw;
    private boolean attached;
    private boolean shown;
    private long began;
    private boolean logged;
    private long readyAt;
    private int frames;
    public Hk3SparsePreviewWidget(MultiblockMachineDefinition definition) {
        this(definition,()->{});
    }
    public Hk3SparsePreviewWidget(MultiblockMachineDefinition definition,Runnable onShown) {
        super(0,0,160,160);this.definition=definition;this.onShown=onShown;setClientSideWidget();
        addWidget(new LabelWidget(4,70,"hk3gtl.preview.loading"));
    }
    @Override public void drawInBackground(GuiGraphics graphics,int mouseX,int mouseY,float partialTicks) {
        long now=System.nanoTime();
        if(lastDraw==0||logged&&now-lastDraw>500_000_000L){began=now;logged=false;}
        lastDraw=now;OPEN.add(this);
        warm=this;
        if(!attached && loading==null) {
            began=lastDraw;
            try { loading=LOADER.submit(()->prepare(definition)); }
            catch(RejectedExecutionException busy) { super.drawInBackground(graphics,mouseX,mouseY,partialTicks);return; }
        }
        if(!attached && loading.isDone()) {
            attached=true;clearAllWidgets();
            try {
                var prepared=loading.get();var data=prepared.data();
                preview=new Hk3W01PreviewWidget(definition,data.layout(),prepared.states(),data.front(),data.entities(),prepared.index());
                preview.setKeepAlive(this::touchPreview);addWidget(preview);
            }catch(InterruptedException failure) {
                Thread.currentThread().interrupt();addWidget(new LabelWidget(4,70,"hk3gtl.preview.failed"));
            }catch(ExecutionException|RuntimeException failure) {
                com.mojang.logging.LogUtils.getLogger().error("自家完整预览失败：{}",definition.getId(),failure);
                addWidget(new LabelWidget(4,70,"hk3gtl.preview.failed"));
            }finally { loading=null; }
        }
        super.drawInBackground(graphics,mouseX,mouseY,partialTicks);
        if(preview!=null&&preview.testReady()){
            if(!shown){shown=true;onShown.run();}
            if(!logged){logged=true;
                readyAt=System.nanoTime();frames=0;
                com.mojang.logging.LogUtils.getLogger().info("自家预览就绪：{}，加载及烘焙{}ms",definition.getId(),(readyAt-began)/1_000_000);
            }
            if(readyAt!=0)frames++;
            if(readyAt!=0&&System.nanoTime()-readyAt>=5_000_000_000L){
                long elapsed=System.nanoTime()-readyAt;
                long direct=java.lang.management.ManagementFactory.getPlatformMXBeans(java.lang.management.BufferPoolMXBean.class).stream()
                        .filter(pool->pool.getName().equals("direct")).mapToLong(java.lang.management.BufferPoolMXBean::getMemoryUsed).sum();
                com.mojang.logging.LogUtils.getLogger().info("自家预览采样：{}，5秒均帧{}，堆{}MiB，直接缓冲{}MiB",definition.getId(),
                        frames*1e9/elapsed,java.lang.management.ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getUsed()/1048576,direct/1048576);
                readyAt=0;
            }
        }
    }
    private void touchPreview() { lastDraw=System.nanoTime();OPEN.add(this);warm=this; }
    private static Prepared prepare(MultiblockMachineDefinition definition) {
        if(cached!=null&&cached.definition()==definition)return cached;
        cached=null;
        Hk3SparsePreviewData.Data data;
        if(definition.getId().getPath().equals("w07_matter_regeneration_ark")
                ||definition.getId().getPath().equals("w15_tree_sea_audience_throne")){
            boolean w15=definition.getId().getPath().equals("w15_tree_sea_audience_throne");
            var w07meta=w15?null:com.sirin.hk3gtl.client.wonder.Hk3W07SceneModel.loadMetadata();
            var w15meta=w15?com.sirin.hk3gtl.client.wonder.Hk3W15SceneModel.loadMetadata():null;
            int[] size=w15?w15meta.sizeXYZ():w07meta.sizeXYZ(),
                    control=w15?w15meta.controller_blueprint():w07meta.controller_blueprint(),
                    offset=w15?w15meta.blueprint_to_export_offset_xyz():w07meta.blueprint_to_export_offset_xyz();
            String[] palette=w15?w15meta.palette():w07meta.palette();
            int controllerState=java.util.stream.IntStream.range(0,palette.length)
                    .filter(i->palette[i].split("\\[",2)[0].equals(definition.getId().toString())).findFirst().orElseThrow();
            int cx=control[0]+offset[0],cy=control[1]+offset[1],cz=control[2]+offset[2];
            var layout=new Hk3W01HallLayout(size[0],size[1],size[2],cx,cy,cz,java.util.List.of(palette),
                    new long[]{Hk3W01HallLayout.pack(cx,cy,cz,controllerState)});
            data=new Hk3SparsePreviewData.Data(layout,java.util.Map.of(),net.minecraft.core.Direction.SOUTH);
        }else if(definition.getId().getPath().equals("w14_world_bubble_recurrence_engine")){
            var meta=com.sirin.hk3gtl.client.wonder.Hk3W14SceneModel.loadMetadata();
            int[] size=meta.sizeXYZ(),control=meta.controller_blueprint(),offset=meta.blueprint_to_export_offset_xyz();
            String[] palette=meta.palette();
            int controllerState=java.util.stream.IntStream.range(0,palette.length)
                    .filter(i->palette[i].split("\\[",2)[0].equals(definition.getId().toString())).findFirst().orElseThrow();
            int cx=control[0]+offset[0],cy=control[1]+offset[1],cz=control[2]+offset[2];
            long[] cells=new long[meta.native_blocks().length+1];
            cells[0]=Hk3W01HallLayout.pack(cx,cy,cz,controllerState);
            for(int i=0;i<meta.native_blocks().length;i++){
                var block=meta.native_blocks()[i];int[] pos=block.pos();
                cells[i+1]=Hk3W01HallLayout.pack(pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2],block.state()-1);
            }
            java.util.Arrays.sort(cells);
            var layout=new Hk3W01HallLayout(size[0],size[1],size[2],cx,cy,cz,java.util.List.of(palette),cells);
            data=new Hk3SparsePreviewData.Data(layout,java.util.Map.of(),net.minecraft.core.Direction.SOUTH);
        }else if(definition.getId().getPath().equals("w11_distributed_industrial_command")
                ||definition.getId().getPath().equals("w13_self_computing_research_mother")){
            boolean w13=definition.getId().getPath().equals("w13_self_computing_research_mother");
            var w11meta=w13?null:com.sirin.hk3gtl.client.wonder.Hk3W11FxModel.loadMetadata();
            var w13meta=w13?com.sirin.hk3gtl.client.wonder.Hk3W13FxModel.loadMetadata():null;
            int[] size=w13?w13meta.sizeXYZ():w11meta.sizeXYZ(),
                    control=w13?w13meta.controller_blueprint():w11meta.controller_blueprint(),
                    offset=w13?w13meta.blueprint_to_export_offset_xyz():w11meta.blueprint_to_export_offset_xyz();
            String[] palette=w13?w13meta.palette():w11meta.palette();
            int controllerState=java.util.stream.IntStream.range(0,palette.length)
                    .filter(i->palette[i].split("\\[",2)[0].equals(definition.getId().toString())).findFirst().orElseThrow();
            int cx=control[0]+offset[0],cy=control[1]+offset[1],cz=control[2]+offset[2];
            var layout=new Hk3W01HallLayout(size[0],size[1],size[2],cx,cy,cz,java.util.List.of(palette),
                    new long[]{Hk3W01HallLayout.pack(cx,cy,cz,controllerState)});
            data=new Hk3SparsePreviewData.Data(layout,java.util.Map.of(),net.minecraft.core.Direction.SOUTH);
        }else data=Hk3SparsePreviewData.load(definition);
        BlockState[] states=data.layout().palette().stream().map(Hk3LargeArchitectureShapes::state).toArray(BlockState[]::new);
        var result=new Prepared(definition,data,states,Hk3W01PreviewWidget.prepareIndex(data.layout(),states));
        com.mojang.logging.LogUtils.getLogger().info("自家预览准备：{}，完整{}格，全景烘焙{}格",definition.getId(),data.layout().cells().length,result.index().renderCells().length);
        // CPU只保留最近一份且不超过64MiB；不缓存方块实体或GPU对象。
        long bytes=8L*data.layout().cells().length+result.index().byteSize()
                +data.entities().values().stream().mapToLong(net.minecraft.nbt.CompoundTag::sizeInBytes).sum();
        if(bytes<=64L*1024*1024)cached=result;
        return result;
    }
    @SubscribeEvent public static void expire(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        long now=System.nanoTime();
        OPEN.removeIf(widget->{
            if(now-widget.lastDraw<2_000_000_000L)return false;
            // 最近一页短时复用已烘焙场景，其余离屏页及时释放。
            if(widget==warm&&widget.preview!=null&&widget.preview.testReady()
                    &&widget.preview.cacheBytes()<=64L*1024*1024&&now-widget.lastDraw<30_000_000_000L)return false;
            if(widget.loading!=null)widget.loading.cancel(true);
            if(widget.preview!=null)widget.preview.closePreview();
            widget.loading=null;widget.preview=null;widget.attached=false;widget.shown=false;widget.clearAllWidgets();
            if(widget==warm)warm=null;
            widget.addWidget(new LabelWidget(4,70,"hk3gtl.preview.loading"));return true;
        });
    }
}
