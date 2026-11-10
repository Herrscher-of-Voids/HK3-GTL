package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.gui.UITemplate;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IDisplayUIMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.sirin.hk3gtl.common.multiblock.build.Hk3BuildPlan;
import com.sirin.hk3gtl.common.multiblock.build.Hk3BuildState;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.sirin.hk3gtl.common.multiblock.build.Hk3HyperionIntegrityTask;
import com.sirin.hk3gtl.common.multiblock.build.Hk3IntegrityHost;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/** 创造调试先逐格核验真实实体，再允许启停；正式生产和毕业资格另行验收。 */
public abstract class Hk3CommissionMachine extends MultiblockControllerMachine implements IDisplayUIMachine,Hk3IntegrityHost {
    private static final Set<Hk3CommissionMachine> LOADED=ConcurrentHashMap.newKeySet();
    private Hk3HyperionIntegrityTask check;
    private Hk3BuildPlan plan;
    private Direction verifiedFacing;
    private boolean verified,running;
    private long ticks;
    private long inspected;
    private String status="尚未检查完整结构";
    protected Hk3CommissionMachine(IMachineBlockEntity holder){super(holder);}
    protected abstract String commissionTitle();
    @Override public MultiblockControllerMachine integrityController(){return this;}
    @Override public boolean captureFarView(){return true;}
    @Override public void onLoad(){
        super.onLoad();
        if(getLevel() instanceof ServerLevel){
            boolean previous=isFormed();onStructureInvalid();LOADED.add(this);subscribeServerTick(this::tickCommission);
            if(previous)requestIntegrityCheck();
        }
    }
    @Override public void onUnload(){LOADED.remove(this);onStructureInvalid();super.onUnload();}
    @Override public void onPartUnload(){onStructureInvalid();super.onPartUnload();}
    @Override public void asyncCheckPattern(long periodID){}
    public boolean verified(){return verified&&verifiedFacing==getFrontFacing();}
    public boolean commissioning(){return running&&verified()&&isFormed();}
    public long commissionTicks(){return ticks;}
    public String commissionStatus(){return status;}
    @Override public void onStructureInvalid(){
        super.onStructureInvalid();verified=false;running=false;ticks=0;inspected=0;plan=null;
        var old=check;check=null;if(old!=null)old.close();
        status="结构未成型，调试已停止";
        if(getLevel() instanceof ServerLevel level)MultiblockWorldSavedData.getOrCreate(level).removeMapping(getMultiblockState());
    }
    public void requestIntegrityCheck(){
        if(!(getLevel() instanceof ServerLevel)||Hk3UniversalTerminalBuilder.isBuilding(this))return;
        onStructureInvalid();check=new Hk3HyperionIntegrityTask(this);status="准备完整实体检查…";
    }
    @Override public void acceptVerifiedPlan(Hk3BuildPlan verifiedPlan){plan=verifiedPlan;}
    @Override public void integrityFailed(String reason){onStructureInvalid();status=reason;}
    @Override public void integrityPassed(Direction facing){
        var old=check;check=null;if(old!=null)old.close();verified=true;verifiedFacing=facing;
        if(!checkPatternWithLock()){integrityFailed("真实GT主控或通用接口未匹配");return;}
        onStructureFormed();var saved=MultiblockWorldSavedData.getOrCreate((ServerLevel)getLevel());
        saved.addMapping(getMultiblockState());saved.removeAsyncLogic(this);
        status="完整结构已成型 · 可启动创造调试";
        com.mojang.logging.LogUtils.getLogger().info("{}完整结构成型：{}，{}格",commissionTitle(),getPos(),plan.size());
    }
    public void toggleCommission(Player player){
        if(getLevel() instanceof ServerLevel&&player.isCreative()&&verified()&&isFormed()){
            running=!running;status=running?"实体巡检运行中 · 不产出、不计毕业":"实体巡检已暂停";
            com.mojang.logging.LogUtils.getLogger().info("{}创造调试：{}，运行{}，累计{}tick",commissionTitle(),getPos(),running,ticks);
        }
    }
    private void tickCommission(){
        try{
            if(check!=null){status=check.progress();check.tick();}
            if(verified&&!verified())onStructureInvalid();
            if(commissioning()){
                ticks++;var level=(ServerLevel)getLevel();
                var rotation=Hk3UniversalTerminalBuilder.rotation(plan.sourceFacing(),getFrontFacing());
                // 均匀抽查已加载实体；不强制常驻百万方块，也不替代首次完整核验。
                for(int step=0;step<64;step++){
                    int i=java.util.concurrent.ThreadLocalRandom.current().nextInt(plan.size());
                    var pos=new BlockPos(plan.x(i),plan.y(i),plan.z(i)).rotate(rotation).offset(getPos());
                    if(!level.hasChunkAt(pos)||pos.equals(getPos()))continue;
                    if(!Hk3BuildState.matches(level.getBlockState(pos),plan.state(i).rotate(rotation))
                            &&!(plan.isMachinePartSlot(plan.x(i),plan.y(i),plan.z(i))&&MetaMachine.getMachine(level,pos) instanceof IMultiPart)){
                        integrityFailed("巡检发现结构不符："+pos.toShortString());return;
                    }
                    inspected++;
                }
            }
        }catch(RuntimeException failure){
            com.mojang.logging.LogUtils.getLogger().error("奇观实体检查失败",failure);integrityFailed("检查失败，详见日志");
        }
    }
    public static void blockChanged(ServerLevel level,BlockPos pos){
        for(var machine:LOADED){
            if(machine.getLevel()!=level||(!machine.verified&&machine.check==null)||Hk3UniversalTerminalBuilder.isBuilding(machine))continue;
            var r=Hk3UniversalTerminalBuilder.rotation(machine.getFrontFacing(),machine.plan==null?Direction.NORTH:machine.plan.sourceFacing());
            var local=pos.subtract(machine.getPos()).rotate(r);
            // 检查中的变更由逐格读取发现；已通过的实体按精确坐标撤销证据，忽略空域积雪。
            if(machine.check!=null&&machine.check.containsWorldPosition(pos)
                    ||machine.plan!=null&&machine.plan.contains(local.getX(),local.getY(),local.getZ()))
                machine.integrityFailed("结构已改变，请重新检查："+pos.toShortString());
        }
    }
    @Override public ModularUI createUI(Player player){
        return new ModularUI(330,238,this,player).background(GuiTextures.BACKGROUND)
            .widget(new LabelWidget(8,8,commissionTitle()))
            .widget(new LabelWidget(8,27,"完整实体核验 · 空气自由 · 创造运行调试"))
            .widget(new LabelWidget(8,47,()->status))
            .widget(new LabelWidget(8,65,()->Hk3UniversalTerminalBuilder.progress(this)))
            .widget(new LabelWidget(8,83,()->"运行："+ticks+" tick · 实读："+inspected+"格"))
            .widget(button(8,102,102,"搭建／暂停",()->Hk3UniversalTerminalBuilder.use(player,getMultiblockState(),null)))
            .widget(button(114,102,102,"完整检查",this::requestIntegrityCheck))
            .widget(button(220,102,102,"取消搭建",()->Hk3UniversalTerminalBuilder.cancel(player,this)))
            .widget(button(8,127,314,"启动／暂停创造调试",()->toggleCommission(player)))
            .widget(UITemplate.bindPlayerInventory(player.getInventory(),GuiTextures.SLOT,77,157,true));
    }
    private ButtonWidget button(int x,int y,int width,String label,Runnable action){
        return new ButtonWidget(x,y,width,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture(label)),click->{if(!click.isRemote)action.run();});
    }
}
