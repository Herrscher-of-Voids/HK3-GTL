package com.sirin.hk3gtl.common.multiblock.build;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Rotation;

/** 在服务器主线程分批实读完整稀疏舰体；从不把建造完成计数当作成型证明。 */
public final class Hk3HyperionIntegrityTask implements AutoCloseable {
    private static final TicketType<Long> CONTROL_TICKET=TicketType.create("hk3gtl_hull_check",Long::compare);
    private final com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine machine;
    private final Hk3IntegrityHost host;
    private final ServerLevel level;
    private final Hk3BuildPlan plan;
    private final Direction facing;
    private final Rotation rotation;
    private final Hk3BuildChunkWindow chunks;
    private final BlockPos.MutableBlockPos pos=new BlockPos.MutableBlockPos();
    private final BlockPos.MutableBlockPos ahead=new BlockPos.MutableBlockPos();
    private Hk3BuildOrder order;
    private int cursor;
    private boolean prepared;
    private boolean controlTicket;
    public Hk3HyperionIntegrityTask(Hk3IntegrityHost host) {
        this.host=host;this.machine=host.integrityController();level=(ServerLevel)machine.getLevel();
        plan=Hk3BuildPlans.create(machine);facing=machine.getFrontFacing();
        rotation=Hk3UniversalTerminalBuilder.rotation(plan.sourceFacing(),facing);
        chunks=new Hk3BuildChunkWindow(level,machine.getPos().asLong());
        level.getChunkSource().addRegionTicket(CONTROL_TICKET,new ChunkPos(machine.getPos()),1,machine.getPos().asLong());
        controlTicket=true;
    }
    public String progress() { return !prepared?"准备舰体检查…":order==null?"建立检查索引…":"检查舰体 "+cursor+"/"+plan.size(); }
    public boolean containsWorldPosition(BlockPos changed) {
        var local=changed.subtract(machine.getPos()).rotate(Hk3UniversalTerminalBuilder.rotation(facing,plan.sourceFacing()));
        var min=plan.minOffset();var max=plan.maxOffset();
        return local.getX()>=min.getX()&&local.getX()<=max.getX()&&local.getY()>=min.getY()&&local.getY()<=max.getY()
            &&local.getZ()>=min.getZ()&&local.getZ()<=max.getZ();
    }
    public void tick() {
        if(machine.isInValid()||facing!=machine.getFrontFacing()||Hk3UniversalTerminalBuilder.isBuilding(machine)) {
            host.integrityFailed("检查中断：朝向、控制器或建造状态已变化");return;
        }
        long deadline=System.nanoTime()+2_000_000L;
        for(int step=0;step<16384&&System.nanoTime()<deadline;step++) {
            if(!prepared) {prepared=plan.prepareStep();continue;}
            if(order==null) {
                var a=position(plan.minOffset().getX(),plan.minOffset().getY(),plan.minOffset().getZ(),new BlockPos.MutableBlockPos()).immutable();
                var b=position(plan.maxOffset().getX(),plan.maxOffset().getY(),plan.maxOffset().getZ(),new BlockPos.MutableBlockPos()).immutable();
                int minX=Math.min(a.getX(),b.getX())>>4,minZ=Math.min(a.getZ(),b.getZ())>>4;
                int width=(Math.max(a.getX(),b.getX())>>4)-minX+1;
                int count=width*((Math.max(a.getZ(),b.getZ())>>4)-minZ+1);
                // 分桶及二分预取会反复调用坐标函数，不能改写当前正在核验的pos。
                order=new Hk3BuildOrder(plan,count,i->{position(i,ahead);return ((ahead.getZ()>>4)-minZ)*width+(ahead.getX()>>4)-minX;});
            }
            if(!order.step())continue;
            if(cursor==plan.size()) {host.acceptVerifiedPlan(plan);host.integrityPassed(facing);return;}
            int i=order.index(cursor);position(i,pos);
            if(!chunks.ready(cursor,plan.size(),at->{position(order.index(at),ahead);return ChunkPos.asLong(ahead.getX()>>4,ahead.getZ()>>4);},order::nextChunkIndex))return;
            if(!pos.equals(machine.getPos()) && !Hk3BuildState.matches(level.getBlockState(pos),plan.state(i).rotate(rotation))
                    && !(plan.isMachinePartSlot(plan.x(i),plan.y(i),plan.z(i)) && MetaMachine.getMachine(level,pos) instanceof IMultiPart)) {
                host.integrityFailed("结构不符："+pos.toShortString());return;
            }
            if(host.captureFarView())com.sirin.hk3gtl.common.farview.Hk3FarViewData.observe(level,pos,level.getBlockState(pos));
            cursor++;
        }
    }
    private void position(int i,BlockPos.MutableBlockPos out) {position(plan.x(i),plan.y(i),plan.z(i),out);}
    private BlockPos.MutableBlockPos position(int x,int y,int z,BlockPos.MutableBlockPos out) {
        int rx=switch(rotation){case CLOCKWISE_90->-z;case CLOCKWISE_180->-x;case COUNTERCLOCKWISE_90->z;default->x;};
        int rz=switch(rotation){case CLOCKWISE_90->x;case CLOCKWISE_180->-z;case COUNTERCLOCKWISE_90->-x;default->z;};
        return out.set(machine.getPos().getX()+rx,machine.getPos().getY()+y,machine.getPos().getZ()+rz);
    }
    @Override public void close() {
        try {chunks.close();plan.close();}
        finally {if(controlTicket){controlTicket=false;level.getChunkSource().removeRegionTicket(CONTROL_TICKET,new ChunkPos(machine.getPos()),1,machine.getPos().asLong());}}
    }
}
