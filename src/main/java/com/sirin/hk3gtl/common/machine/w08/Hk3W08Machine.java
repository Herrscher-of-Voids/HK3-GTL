package com.sirin.hk3gtl.common.machine.w08;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderMachine;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.network.PacketDistributor;

public final class Hk3W08Machine extends Hk3WonderMachine {
    private static final TicketType<Long> FIELD=TicketType.create("hk3gtl_w08_field",Long::compare);
    private boolean visualFormed,working,ticket;
    private long epoch,age;
    private double phase,flow,seed;
    private int[] ports=new int[0];
    public Hk3W08Machine(IMachineBlockEntity holder){super(holder,"W08");}
    @Override public void onLoad(){super.onLoad();if(getLevel() instanceof ServerLevel)subscribeServerTick(this::tickField);}
    @Override public void onStructureFormed(){
        super.onStructureFormed();
        ports=getParts().stream().map(part->part.self().getPos()).mapToInt(pos->{
            int dx=pos.getX()-getPos().getX(),dz=pos.getZ()-getPos().getZ(),x=dx,z=dz;
            switch(getFrontFacing()){
                case EAST->{x=dz;z=-dx;}case SOUTH->{x=-dx;z=-dz;}case WEST->{x=-dz;z=dx;}default->{}
            }
            return ((pos.getY()-getPos().getY()+238)*512+z+165)*512+x+256;
        }).sorted().toArray();
    }
    @Override public void onStructureInvalid(){
        super.onStructureInvalid();ports=new int[0];
        if(getLevel() instanceof ServerLevel level){
            if(visualFormed){visualFormed=false;sync(level);}
            if(ticket){ticket=false;level.getChunkSource().removeRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());}
        }
    }
    private void tickField(){
        var level=(ServerLevel)getLevel();long now=level.getGameTime();
        if(!verified()||!isFormed())return;
        boolean active=commissioning()||getRecipeLogic().isActive(),changed=active!=working;
        if(!visualFormed){visualFormed=true;phase=flow=0;age=0;epoch=now;seed=level.random.nextDouble()*10000;changed=true;}
        phase+=(now-epoch)/20.*(working?.07:.025);flow+=(now-epoch)/20.*(working?.085:.035);age+=now-epoch;epoch=now;working=active;
        boolean needed=level.players().stream().anyMatch(p->p.distanceToSqr(getPos().getX(),getPos().getY(),getPos().getZ())<2500d*2500);
        if(needed!=ticket){
            ticket=needed;
            if(needed)level.getChunkSource().addRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());
            else level.getChunkSource().removeRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());
        }
        if(changed||now%40==0)sync(level);
    }
    private void sync(ServerLevel level){
        var packet=new Hk3W08FieldPacket(level.dimension().location(),getPos(),getFrontFacing(),visualFormed,working,phase,flow,epoch,age,seed,ports);
        for(var player:level.players())if(player.distanceToSqr(getPos().getX(),getPos().getY(),getPos().getZ())<2500d*2500)
            Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),packet);
    }
}
