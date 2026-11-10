package com.sirin.hk3gtl.common.machine.w03;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IDisplayUIMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.gui.UITemplate;
import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.sirin.hk3gtl.common.multiblock.build.*;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.network.PacketDistributor;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/** C9真实GT主机；完整实体复核后开放创造场调试，尚不授予生产或毕业资格。 */
public final class Hk3W03Machine extends MultiblockControllerMachine implements IDisplayUIMachine,Hk3IntegrityHost {
    private static final Set<Hk3W03Machine> LOADED=ConcurrentHashMap.newKeySet();
    private static final TicketType<Long> FIELD=TicketType.create("hk3gtl_w03_field",Long::compare);
    private Hk3HyperionIntegrityTask check;
    private Hk3BuildPlan verifiedPlan;
    private Direction verifiedFacing;
    private boolean verified,running,ticket;
    private long elapsed,epoch;
    private String status="尚未检查C9完整结构";
    public Hk3W03Machine(IMachineBlockEntity holder){super(holder);}
    @Override public MultiblockControllerMachine integrityController(){return this;}
    @Override public boolean captureFarView(){return false;}
    @Override public void onLoad(){
        super.onLoad();if(getLevel() instanceof ServerLevel){
            // GT保存的成型位不等于本次世界实体已经核验，重新加载必须撤销旧凭据。
            boolean previouslyFormed=isFormed();onStructureInvalid();LOADED.add(this);subscribeServerTick(this::tickField);
            if(previouslyFormed)requestIntegrityCheck();
        }
    }
    @Override public void onUnload(){LOADED.remove(this);onStructureInvalid();super.onUnload();}
    @Override public void onPartUnload(){onStructureInvalid();super.onPartUnload();}
    @Override public void asyncCheckPattern(long periodID){}
    public boolean verified(){return verified&&verifiedFacing==getFrontFacing();}
    public String commissionStatus(){return status+"；运行="+running+"；tick="+(elapsed+(running?getLevel().getGameTime()-epoch:0));}
    private void closeCheck(){var old=check;check=null;if(old!=null)old.close();}
    @Override public void onStructureInvalid(){
        super.onStructureInvalid();verified=false;verifiedPlan=null;running=false;elapsed=0;closeCheck();
        status="结构未成型，场调试已停止";
        if(getLevel() instanceof ServerLevel level){
            if(ticket){ticket=false;level.getChunkSource().removeRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());}
            MultiblockWorldSavedData.getOrCreate(level).removeMapping(getMultiblockState());sync();
        }
    }
    public void requestIntegrityCheck(){
        if(!(getLevel() instanceof ServerLevel)||Hk3UniversalTerminalBuilder.isBuilding(this))return;
        onStructureInvalid();check=new Hk3HyperionIntegrityTask(this);status="准备C9完整实体检查…";
    }
    @Override public void acceptVerifiedPlan(Hk3BuildPlan plan){verifiedPlan=plan;}
    @Override public void integrityFailed(String reason){onStructureInvalid();status=reason;com.mojang.logging.LogUtils.getLogger().info("W03 C9检查未通过：{}",reason);}
    @Override public void integrityPassed(Direction facing){
        closeCheck();verified=true;verifiedFacing=facing;
        if(!checkPatternWithLock()){integrityFailed("通用接口未通过GT匹配");return;}
        onStructureFormed();var saved=MultiblockWorldSavedData.getOrCreate((ServerLevel)getLevel());
        saved.addMapping(getMultiblockState());saved.removeAsyncLogic(this);
        status="C9完整结构已成型 · 可启动场调试";updateTicket((ServerLevel)getLevel());sync();
        com.mojang.logging.LogUtils.getLogger().info("W03 C9完整结构成型：{}，6642464格",getPos());
    }
    public void toggleField(Player player){
        if(!(getLevel() instanceof ServerLevel level)||!player.isCreative()||!verified()||!isFormed())return;
        if(running){elapsed+=level.getGameTime()-epoch;running=false;}
        else{epoch=level.getGameTime();running=true;}
        updateTicket(level);
        status=running?"场调试运行中 · 不产出物品、不计毕业":"场调试已暂停";sync();
        com.mojang.logging.LogUtils.getLogger().info("W03 C9场调试：{}，运行{}，累计{}tick",getPos(),running,elapsed);
    }
    private void tickField(){
        try{if(check!=null){status=check.progress();check.tick();}
            if(verified&&!verified())onStructureInvalid();
            if(verified&&getLevel().getGameTime()%40==0){updateTicket((ServerLevel)getLevel());sync();}
        }catch(RuntimeException failure){com.mojang.logging.LogUtils.getLogger().error("W03 C9完整检查失败",failure);integrityFailed("检查失败，详见日志");}
    }
    private void updateTicket(ServerLevel level){
        // 暂停后仍有附近观察者时保留主控小窗口，防止卸载撤销成型并使整机远景消失。
        boolean needed=verified&&(running||level.players().stream().anyMatch(player->
                player.distanceToSqr(getPos().getX(),getPos().getY(),getPos().getZ())<2500d*2500));
        if(needed==ticket)return;
        ticket=needed;
        if(needed)level.getChunkSource().addRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());
        else level.getChunkSource().removeRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());
    }
    private void sync(){
        if(!(getLevel() instanceof ServerLevel level))return;
        var packet=new Hk3W03FieldPacket(level.dimension().location(),getPos(),getFrontFacing(),verified,running,elapsed,epoch);
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
    public static void blockChanged(ServerLevel level,BlockPos pos){
        for(var m:LOADED)if(m.getLevel()==level&&(m.verified||m.check!=null)&&!Hk3UniversalTerminalBuilder.isBuilding(m)&&m.bounds().contains(pos)){
            var r=Hk3UniversalTerminalBuilder.rotation(m.getFrontFacing(),Direction.NORTH);
            var local=pos.subtract(m.getPos()).rotate(r);
            if(m.verifiedPlan==null||m.verifiedPlan.contains(local.getX(),local.getY(),local.getZ()))m.integrityFailed("结构已改变，请重新检查："+pos.toShortString());
        }
    }
    @Override public ModularUI createUI(Player player){
        return new ModularUI(330,238,this,player).background(GuiTextures.BACKGROUND)
            .widget(new LabelWidget(8,8,"hk3gtl.w03.title"))
            .widget(new LabelWidget(8,25,"hk3gtl.w03.size"))
            .widget(new LabelWidget(8,41,"hk3gtl.w03.commission"))
            .widget(new LabelWidget(8,58,()->status))
            .widget(new LabelWidget(8,74,()->Hk3UniversalTerminalBuilder.progress(this)))
            .widget(button(8,101,102,"hk3gtl.w03.build",()->Hk3UniversalTerminalBuilder.use(player,getMultiblockState(),null)))
            .widget(button(114,101,102,"hk3gtl.w03.check",this::requestIntegrityCheck))
            .widget(button(220,101,102,"hk3gtl.w03.cancel",()->Hk3UniversalTerminalBuilder.cancel(player,this)))
            .widget(button(8,126,314,"hk3gtl.w03.toggle",()->toggleField(player)))
            .widget(UITemplate.bindPlayerInventory(player.getInventory(),GuiTextures.SLOT,77,157,true));
    }
    private ButtonWidget button(int x,int y,int width,String label,Runnable action){
        return new ButtonWidget(x,y,width,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture(label)),click->{if(!click.isRemote)action.run();});
    }
}
