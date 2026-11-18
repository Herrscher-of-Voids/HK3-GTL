package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.gui.fancy.IFancyUIProvider;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderManagementPage;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3MultiblockLoading;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import java.util.List;

public abstract class Hk3CommissionMachine extends com.sirin.hk3gtl.common.machine.wonder.Hk3WonderProductionMachine {
    private boolean running;
    private long ticks;
    private String status="等待GTL原生成型检查";
    protected Hk3CommissionMachine(IMachineBlockEntity holder,String role){super(holder,role);}
    protected abstract String commissionTitle();
    @Override public void onLoad(){
        super.onLoad();
        if(getLevel() instanceof ServerLevel)subscribeServerTick(this::tickCommission);
    }
    @Override public boolean verified(){return isFormed();}
    public boolean commissioning(){return running&&isFormed();}
    public long commissionTicks(){return ticks;}
    public String commissionStatus(){return status;}
    @Override public void onStructureInvalid(){
        super.onStructureInvalid();running=false;ticks=0;
        status="GTL原生结构未成型，调试已停止";
    }
    @Override public void onStructureFormed(){
        super.onStructureFormed();
        status="GTL原生结构已成型 · 正式生产需研究、二审及真实供能";
    }
    public void requestIntegrityCheck(){
        if(!(getLevel() instanceof ServerLevel)||Hk3UniversalTerminalBuilder.isBuilding(this))return;
        if(!com.sirin.hk3gtl.common.machine.wonder.Hk3WonderCatalog.hasBlueprint(researchRole())){status="完整建筑蓝图尚未完成，不能成型或运行";return;}
        Hk3MultiblockLoading.recheck(this);status="GTL原生完整结构检查已排队";
    }
    public void toggleCommission(Player player){
        if(getLevel() instanceof ServerLevel&&player.isCreative()&&isFormed()){
            running=!running;status=running?"创造调试运行中 · 不产出、不计毕业":"创造调试已暂停";
            com.mojang.logging.LogUtils.getLogger().info("{}创造调试：{}，运行{}，累计{}tick",commissionTitle(),getPos(),running,ticks);
        }
    }
    private void tickCommission(){
        if(commissioning()||getRecipeLogic().isActive())ticks++;
    }
    @Override public List<IFancyUIProvider> getSubTabs(){
        var tabs=new java.util.ArrayList<>(super.getSubTabs());
        tabs.add(new Hk3WonderManagementPage(this,this::createManagementWidget));
        return tabs;
    }
    @Override public void addDisplayText(List<Component> text){
        super.addDisplayText(text);
        text.add(Component.literal(status));
    }
    private Widget createManagementWidget(Player player){
        var group=new WidgetGroup(0,0,330,185);
        group.addWidget(new LabelWidget(8,8,commissionTitle()));
        group.addWidget(new LabelWidget(8,27,"GTL原生成型检测 · 正式生产与创造调试"));
        group.addWidget(new LabelWidget(8,47,()->status));
        group.addWidget(new LabelWidget(8,65,()->Hk3UniversalTerminalBuilder.progress(this)));
        group.addWidget(new LabelWidget(8,83,()->"运行："+ticks+" tick"));
        group.addWidget(button(8,102,102,"搭建／暂停",()->Hk3UniversalTerminalBuilder.use(player,getMultiblockState(),null)));
        group.addWidget(button(114,102,102,"GTL原生检查",this::requestIntegrityCheck));
        group.addWidget(button(220,102,102,"取消搭建",()->Hk3UniversalTerminalBuilder.cancel(player,this)));
        group.addWidget(button(8,127,314,"启动／暂停创造调试",()->toggleCommission(player)));
        group.addWidget(button(8,151,314,"启停正式生产",()->getRecipeLogic().setWorkingEnabled(!getRecipeLogic().isWorkingEnabled())));
        group.addWidget(new LabelWidget(8,176,()->"生产："+(getRecipeLogic().isActive()?"运行中":getRecipeLogic().isWorkingEnabled()?"等待物料、供能或许可":"已暂停")));
        return group;
    }
    private ButtonWidget button(int x,int y,int width,String label,Runnable action){
        return new ButtonWidget(x,y,width,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture(label)),click->{if(!click.isRemote)action.run();});
    }
}
