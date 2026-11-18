package com.sirin.hk3gtl.common.machine.wonder;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.network.PacketDistributor;

public class Hk3AnimatedWonderMachine extends Hk3WonderMachine {
    private static final TicketType<Long> FIELD=TicketType.create("hk3gtl_wonder_field",Long::compare);
    private boolean visualFormed,working,ticket;
    private long epoch,age;
    private double idle,work,seed;
    private int[] ports=new int[0];
    public Hk3AnimatedWonderMachine(IMachineBlockEntity holder,String role){super(holder,role);}
    @Override public void onLoad(){super.onLoad();if(getLevel() instanceof ServerLevel)subscribeServerTick(this::tickField);}
    @Override public void onStructureFormed(){
        super.onStructureFormed();
        var positions=getParts().stream().map(part->part.self().getPos()).toList();
        if(researchRole().equals("W07")||researchRole().equals("W11")||researchRole().equals("W13")||researchRole().equals("W14")||researchRole().equals("W15")){
            int[] center;
            if(!researchRole().equals("W11")){
                try(var source=com.sirin.hk3gtl.common.multiblock.pattern.Hk3WonderPatternSource.open(researchRole())){
                    var header=source.header();center=new int[]{header.cx(),header.cy(),header.cz()};
                }
            }else{
                var header=com.sirin.hk3gtl.common.multiblock.build.Hk3W11BuildPlan.header();
                center=new int[]{header.cx(),header.cy(),header.cz()};
            }
            ports=positions.stream().sorted().flatMapToInt(pos->{
                int dx=pos.getX()-getPos().getX(),dz=pos.getZ()-getPos().getZ(),x=dx,z=dz;
                switch(getFrontFacing()){
                    case NORTH->{x=-dx;z=-dz;}case EAST->{x=-dz;z=dx;}case WEST->{x=dz;z=-dx;}default->{}
                }
                return java.util.stream.IntStream.of(x+center[0],pos.getY()-getPos().getY()+center[1],z+center[2]);
            }).toArray();
            return;
        }
        int[] center=researchRole().equals("W05")?new int[]{277,12,5}:new int[]{408,85,719};
        int width=researchRole().equals("W05")?555:817,depth=researchRole().equals("W05")?701:761;
        ports=positions.stream().mapToInt(pos->{
            int dx=pos.getX()-getPos().getX(),dz=pos.getZ()-getPos().getZ(),x=dx,z=dz;
            switch(getFrontFacing()){
                case EAST->{x=dz;z=-dx;}case SOUTH->{x=-dx;z=-dz;}case WEST->{x=-dz;z=dx;}default->{}
            }
            return ((pos.getY()-getPos().getY()+center[1])*depth+z+center[2])*width+x+center[0];
        }).sorted().toArray();
    }
    @Override public void onStructureInvalid(){
        super.onStructureInvalid();ports=new int[0];
        if(getLevel() instanceof ServerLevel level){
            if(visualFormed){visualFormed=false;sync(level);}
            if(ticket){ticket=false;level.getChunkSource().removeRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());}
        }
    }
    protected boolean fieldRunning(){return commissioning()||getRecipeLogic().isActive();}
    private void tickField(){
        var level=(ServerLevel)getLevel();long now=level.getGameTime();
        if(!verified()||!isFormed())return;
        boolean active=fieldRunning(),changed=active!=working;
        if(!visualFormed){visualFormed=true;idle=work=0;age=0;epoch=now;seed=level.random.nextDouble()*10000;changed=true;}
        double elapsed=(now-epoch)/20.;
        if(working)work+=elapsed;else idle+=elapsed;
        age+=now-epoch;epoch=now;working=active;
        boolean needed=level.players().stream().anyMatch(p->p.distanceToSqr(getPos().getX(),getPos().getY(),getPos().getZ())<2500d*2500);
        if(needed!=ticket){
            ticket=needed;
            if(needed)level.getChunkSource().addRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());
            else level.getChunkSource().removeRegionTicket(FIELD,new ChunkPos(getPos()),1,getPos().asLong());
        }
        if(changed||now%40==0)sync(level);
    }
    private void sync(ServerLevel level){
        var packet=new Hk3WonderFxPacket(researchRole(),level.dimension().location(),getPos(),getFrontFacing(),visualFormed,working,idle,work,epoch,age,seed,ports);
        for(var player:level.players())if(player.distanceToSqr(getPos().getX(),getPos().getY(),getPos().getZ())<2500d*2500)
            Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),packet);
    }
}
