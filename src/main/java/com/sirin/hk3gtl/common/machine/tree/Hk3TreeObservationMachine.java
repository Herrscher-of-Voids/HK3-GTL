package com.sirin.hk3gtl.common.machine.tree;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.machine.research.Hk3LateIndustrialMachine;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraftforge.network.PacketDistributor;
import java.util.List;

/** I34树影只读取真实GT成型与工况；创造场调试不改变配方、研究或产出。 */
public final class Hk3TreeObservationMachine extends Hk3LateIndustrialMachine {
    private boolean checkedThisLoad,paused;
    private int testMode;
    private long elapsed,epoch;
    public Hk3TreeObservationMachine(IMachineBlockEntity holder){super(holder,"I34");}
    @Override public void onLoad(){super.onLoad();if(getLevel() instanceof ServerLevel){checkedThisLoad=false;epoch=getLevel().getGameTime();subscribeServerTick(this::tickProjection);}}
    @Override public void onUnload(){checkedThisLoad=false;syncProjection();super.onUnload();}
    @Override public void onPartUnload(){checkedThisLoad=false;syncProjection();super.onPartUnload();}
    @Override public void onStructureFormed(){super.onStructureFormed();checkedThisLoad=true;syncProjection();}
    @Override public void onStructureInvalid(){super.onStructureInvalid();checkedThisLoad=false;testMode=0;paused=false;elapsed=0;if(getLevel()!=null)epoch=getLevel().getGameTime();syncProjection();}
    public boolean projectionFormed(){return checkedThisLoad&&isFormed();}
    public int projectionMode(){return !projectionFormed()?0:testMode==0?(getRecipeLogic().isActive()?2:1):testMode;}
    public void setProjectionMode(int mode){testMode=mode;syncProjection();}
    public void pauseProjection(boolean value){
        if(getLevel()==null||paused==value)return;
        if(value)elapsed+=getLevel().getGameTime()-epoch;else epoch=getLevel().getGameTime();paused=value;syncProjection();
    }
    private void tickProjection(){if(getLevel().getGameTime()%20==0)syncProjection();}
    private void syncProjection(){
        if(!(getLevel() instanceof ServerLevel level))return;
        long clock=elapsed+(paused?0:level.getGameTime()-epoch);
        var packet=new Hk3TreeProjectionPacket(level.dimension().location(),getPos(),getFrontFacing(),projectionMode(),paused,clock);
        for(var player:level.players())if(player.distanceToSqr(getPos().getX(),getPos().getY(),getPos().getZ())<2048d*2048)
            Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),packet);
    }
    @Override public void addDisplayText(List<Component> lines){super.addDisplayText(lines);lines.add(Component.translatable("hk3gtl.i34.projection."+projectionMode()));}
}
