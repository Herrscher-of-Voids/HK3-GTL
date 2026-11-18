package com.sirin.hk3gtl.common.machine.w03;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IDisplayUIMachine;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.gui.fancy.IFancyUIProvider;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderManagementPage;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3MultiblockLoading;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.network.PacketDistributor;
import java.util.ArrayList;
import java.util.List;

public final class Hk3W03Machine extends com.sirin.hk3gtl.common.machine.wonder.Hk3WonderProductionMachine implements IDisplayUIMachine {
    private static final TicketType<Long> FIELD=TicketType.create("hk3gtl_w03_field",Long::compare);
    private boolean running,ticket,visualActive;
    private long elapsed,epoch;
    private String status="等待GTL原生成型检查";
    public Hk3W03Machine(IMachineBlockEntity holder){super(holder,"W03");}
    @Override public void onLoad(){
        super.onLoad();if(getLevel() instanceof ServerLevel)subscribeServerTick(this::tickField);
    }
    @Override public void onUnload(){
        if(getLevel() instanceof ServerLevel level&&ticket){
            ticket=false;level.getChunkSource().removeRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());
        }
        super.onUnload();
    }
    @Override public boolean verified(){return isFormed();}
    public String commissionStatus(){return status+"；运行="+running+"；tick="+(elapsed+(running?getLevel().getGameTime()-epoch:0));}
    @Override public void onStructureInvalid(){
        super.onStructureInvalid();running=false;visualActive=false;elapsed=0;
        status="GTL原生结构未成型，场效演示已停止";
        if(getLevel() instanceof ServerLevel level){
            if(ticket){ticket=false;level.getChunkSource().removeRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());}
            sync();
        }
    }
    @Override public void onStructureFormed(){
        super.onStructureFormed();status="GTL原生结构已成型，准备生产";
        updateTicket((ServerLevel)getLevel());sync();
    }
    public void requestIntegrityCheck(){
        if(!(getLevel() instanceof ServerLevel)||Hk3UniversalTerminalBuilder.isBuilding(this))return;
        Hk3MultiblockLoading.recheck(this);status="GTL原生完整结构检查已排队";
    }
    public void toggleField(Player player){
        if(!(getLevel() instanceof ServerLevel level)||!player.isCreative()||!isFormed())return;
        running=!running;updateVisualClock();
        updateTicket(level);
        status=running?"场效演示运行中，仅供创造模式预览":"场效演示已暂停";sync();
        com.mojang.logging.LogUtils.getLogger().info("W03 C9场调试：{}，运行{}，累计{}tick",getPos(),running,elapsed);
    }
    private void tickField(){
        updateVisualClock();
        if(getLevel().getGameTime()%40==0){updateTicket((ServerLevel)getLevel());sync();}
    }
    private void updateVisualClock(){
        boolean active=running||getRecipeLogic().isActive();
        if(active==visualActive)return;
        if(visualActive)elapsed+=getLevel().getGameTime()-epoch;else epoch=getLevel().getGameTime();
        visualActive=active;sync();
    }
    private void updateTicket(ServerLevel level){
        boolean needed=isFormed()&&(running||getRecipeLogic().isActive()||level.players().stream().anyMatch(player->
                player.distanceToSqr(getPos().getX(),getPos().getY(),getPos().getZ())<2500d*2500));
        if(needed==ticket)return;
        ticket=needed;
        if(needed)level.getChunkSource().addRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());
        else level.getChunkSource().removeRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());
    }
    private void sync(){
        if(!(getLevel() instanceof ServerLevel level))return;
        var packet=new Hk3W03FieldPacket(level.dimension().location(),getPos(),getFrontFacing(),isFormed(),visualActive,elapsed,epoch);
        for(var player:level.players())if(player.distanceToSqr(getPos().getX(),getPos().getY(),getPos().getZ())<2500d*2500)
            Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),packet);
    }
    public Hk3LargeStructurePattern.Bounds bounds(){
        var r=Hk3UniversalTerminalBuilder.rotation(Direction.NORTH,getFrontFacing());
        var a=new BlockPos(-416,-27,-187).rotate(r).offset(getPos());
        var b=new BlockPos(416,608,645).rotate(r).offset(getPos());
        return new Hk3LargeStructurePattern.Bounds(new BlockPos(Math.min(a.getX(),b.getX()),a.getY(),Math.min(a.getZ(),b.getZ())),
                new BlockPos(Math.max(a.getX(),b.getX()),b.getY(),Math.max(a.getZ(),b.getZ())));
    }
    @Override public void addDisplayText(List<Component> textList){
        super.addDisplayText(textList);textList.add(Component.literal(status));
    }
    @Override public List<IFancyUIProvider> getSubTabs(){
        var tabs=new ArrayList<>(super.getSubTabs());
        tabs.add(new Hk3WonderManagementPage(this,this::createManagementWidget));return tabs;
    }
    private Widget createManagementWidget(Player player){
        return new WidgetGroup(0,0,330,185)
            .addWidget(new LabelWidget(8,8,"hk3gtl.w03.title"))
            .addWidget(new LabelWidget(8,25,"hk3gtl.w03.size"))
            .addWidget(new LabelWidget(8,41,"GTL原生成型检测 · 正式生产与创造调试"))
            .addWidget(new LabelWidget(8,58,()->status))
            .addWidget(new LabelWidget(8,74,()->Hk3UniversalTerminalBuilder.progress(this)))
            .addWidget(button(8,101,102,"hk3gtl.w03.build",()->Hk3UniversalTerminalBuilder.use(player,getMultiblockState(),null)))
            .addWidget(button(114,101,102,"GTL原生检查",this::requestIntegrityCheck))
            .addWidget(button(220,101,102,"hk3gtl.w03.cancel",()->Hk3UniversalTerminalBuilder.cancel(player,this)))
            .addWidget(button(8,126,314,"hk3gtl.w03.toggle",()->toggleField(player)))
            .addWidget(button(8,150,314,"启停正式生产",()->getRecipeLogic().setWorkingEnabled(!getRecipeLogic().isWorkingEnabled())))
            .addWidget(new LabelWidget(8,175,()->"生产："+(getRecipeLogic().isActive()?"运行中":getRecipeLogic().isWorkingEnabled()?"等待物料、供能或许可":"已暂停")));
    }
    private ButtonWidget button(int x,int y,int width,String label,Runnable action){
        return new ButtonWidget(x,y,width,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture(label)),click->{if(!click.isRemote)action.run();});
    }
}
