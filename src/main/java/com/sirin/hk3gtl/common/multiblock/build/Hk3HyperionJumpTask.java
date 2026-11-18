package com.sirin.hk3gtl.common.multiblock.build;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionInterior;
import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionJumpData;
import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Rotation;
import java.math.BigInteger;
import java.util.BitSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/** 目的端完整落盘后才清除原舰；两段各自分帧，复制中重启从原舰重新复制。 */
public final class Hk3HyperionJumpTask implements AutoCloseable {
    private enum Stage {PREPARE,CHECK,COPY,CLEAR,ARRIVE}
    private static final TicketType<Long> CONTROL=TicketType.create("hk3gtl_hyperion_jump",Long::compare);
    private static final BigInteger COST=BigInteger.valueOf(4_915_200);
    private static final int FLAGS=Block.UPDATE_CLIENTS|Block.UPDATE_KNOWN_SHAPE|Block.UPDATE_MOVE_BY_PISTON;
    private final Hk3HyperionJumpData data;
    private final CompoundTag route;
    private final Map<UUID,CompoundTag> passengers=new LinkedHashMap<>();
    private final BlockPos origin,target;
    private final Direction facing;
    private final Rotation rotation;
    private ServerLevel source,destination;
    private Hk3BuildPlan plan;
    private Hk3BuildOrder order;
    private Hk3BuildChunkWindow sourceChunks,destinationChunks;
    private BitSet volume;
    private int[] cells;
    private Stage stage=Stage.PREPARE;
    private int cursor,planCursor,volumeCursor,cellCursor;
    private boolean planReady,writing,tickets;

    public Hk3HyperionJumpTask(Hk3HyperionJumpData data,Hk3HyperionMachine ship,ServerLevel destination,BlockPos target) {
        this.data=data;route=new CompoundTag();origin=ship.getPos();this.target=target.immutable();facing=ship.getFrontFacing();
        rotation=Hk3UniversalTerminalBuilder.rotation(Direction.EAST,facing);
        route.putString("Source",ship.getLevel().dimension().location().toString());
        route.putString("Destination",destination.dimension().location().toString());
        route.putLong("Origin",origin.asLong());route.putLong("Target",target.asLong());
        route.putString("Facing",facing.getName());route.putUUID("Owner",ship.getOwnerUUID());route.putUUID("Team",ship.getResearchTeamUUID());
    }
    public Hk3HyperionJumpTask(Hk3HyperionJumpData data,CompoundTag saved) {
        this.data=data;route=saved.getCompound("Route");origin=BlockPos.of(route.getLong("Origin"));target=BlockPos.of(route.getLong("Target"));
        facing=Direction.byName(route.getString("Facing"));rotation=Hk3UniversalTerminalBuilder.rotation(Direction.EAST,facing);
        stage=Stage.valueOf(saved.getString("Stage"));cursor=stage==Stage.COPY?0:saved.getInt("Cursor");
        if(saved.contains("Cells"))cells=saved.getIntArray("Cells");
        for(var raw:saved.getList("Passengers",10)) {var point=(CompoundTag)raw;passengers.put(point.getUUID("Player"),point);}
    }
    public CompoundTag save() {
        var tag=new CompoundTag();tag.put("Route",route);tag.putString("Stage",stage.name());tag.putInt("Cursor",cursor);
        if(cells!=null&&stage!=Stage.PREPARE)tag.putIntArray("Cells",cells);
        var rows=new ListTag();passengers.forEach((id,point)->{var row=point.copy();row.putUUID("Player",id);rows.add(row);});tag.put("Passengers",rows);return tag;
    }
    public boolean writing() {return writing;}
    public boolean isSource(Hk3HyperionMachine ship) {
        return ship.getPos().equals(origin)&&ship.getLevel().dimension().location().toString().equals(route.getString("Source"));
    }
    public boolean contains(ServerLevel level,BlockPos pos) {
        String dimension=level.dimension().location().toString();
        return dimension.equals(route.getString("Source"))&&Hk3HyperionMachine.hullBounds(origin,facing).contains(pos)
                ||dimension.equals(route.getString("Destination"))&&Hk3HyperionMachine.hullBounds(target,facing).contains(pos);
    }
    public String progress() {
        return switch(stage) {case PREPARE->"准备整舰跃迁范围";case CHECK->"检查目标净空";case COPY->"迁移真实舰体与仓储";case CLEAR->"清除原停泊舰体";case ARRIVE->"登舰成员到站";}
                +" · "+cursor+"/"+(cells==null?"准备中":cells.length);
    }
    private void open(MinecraftServer server) {
        source=server.getLevel(ResourceKey.create(Registries.DIMENSION,new ResourceLocation(route.getString("Source"))));
        destination=server.getLevel(ResourceKey.create(Registries.DIMENSION,new ResourceLocation(route.getString("Destination"))));
        sourceChunks=new Hk3BuildChunkWindow(source,origin.asLong());destinationChunks=new Hk3BuildChunkWindow(destination,target.asLong());
        source.getChunkSource().addRegionTicket(CONTROL,new ChunkPos(origin),1,origin.asLong());
        destination.getChunkSource().addRegionTicket(CONTROL,new ChunkPos(target),1,target.asLong());tickets=true;
    }
    public void tick(MinecraftServer server) {
        if(!tickets)open(server);
        holdPassengers();
        long deadline=System.nanoTime()+2_000_000;
        for(int steps=0;steps<8192&&System.nanoTime()<deadline;steps++) {
            if(stage==Stage.PREPARE) {prepare();continue;}
            if(order==null)createOrder();
            if(!order.step())continue;
            if(stage==Stage.ARRIVE) {arrive();return;}
            if(stage==Stage.CHECK&&cursor==cells.length) {depart();return;}
            if(stage==Stage.COPY&&cursor==cells.length) {
                // 复制完成的检查点先包含COPY状态；重启可从原舰重做，原舰不提前销毁。
                data.setDirty();server.saveEverything(false,true,true);stage=Stage.CLEAR;cursor=0;data.setDirty();continue;
            }
            if(stage==Stage.CLEAR&&cursor==cells.length) {clearController();stage=Stage.ARRIVE;data.setDirty();continue;}
            if(!ready())return;
            int cell=cells[order.index(cursor)];var from=position(cell,origin);var to=position(cell,target);
            if(stage==Stage.CHECK) {
                if(!destination.isEmptyBlock(to)) {data.finish("目标被占用："+to.toShortString()+" · 未扣HW");return;}
            } else if(stage==Stage.COPY)copy(from,to);
            else if(!from.equals(origin))clear(from);
            cursor++;data.setDirty();
        }
        holdPassengers();
    }
    private void prepare() {
        if(plan==null) {
            if(source.getChunkSource().getChunkNow(origin.getX()>>4,origin.getZ()>>4)==null)return;
            plan=Hk3BuildPlans.create((Hk3HyperionMachine)MetaMachine.getMachine(source,origin));volume=Hk3HyperionInterior.movementVolume();
            volume.set(linear(0,0,0));
        }
        if(!planReady) {planReady=plan.prepareStep();return;}
        if(planCursor<plan.size()) {
            volume.set(linear(plan.x(planCursor),plan.y(planCursor),plan.z(planCursor)));planCursor++;return;
        }
        if(cells==null)cells=new int[volume.cardinality()];
        if(cellCursor<cells.length) {
            int cell=volume.nextSetBit(volumeCursor);cells[cellCursor++]=cell;volumeCursor=cell+1;return;
        }
        volume=null;plan.close();plan=null;stage=Stage.CHECK;cursor=0;data.setDirty();
    }
    private void createOrder() {
        var bounds=Hk3HyperionMachine.hullBounds(origin,facing);int minX=bounds.min().getX()>>4,minZ=bounds.min().getZ()>>4;
        int width=(bounds.max().getX()>>4)-minX+1,count=width*((bounds.max().getZ()>>4)-minZ+1);
        order=new Hk3BuildOrder(cells.length,1,0,i->0,i->0,count,i->{var p=position(cells[i],origin);return ((p.getZ()>>4)-minZ)*width+(p.getX()>>4)-minX;});
    }
    private boolean ready() {
        boolean from=sourceChunks.ready(cursor,cells.length,i->{var p=position(cells[order.index(i)],origin);return ChunkPos.asLong(p.getX()>>4,p.getZ()>>4);},order::nextChunkIndex);
        boolean to=destinationChunks.ready(cursor,cells.length,i->{var p=position(cells[order.index(i)],target);return ChunkPos.asLong(p.getX()>>4,p.getZ()>>4);},order::nextChunkIndex);
        return from&&to;
    }
    private void depart() {
        var ship=(Hk3HyperionMachine)MetaMachine.getMachine(source,origin);
        if(!ship.hasVerifiedHull()||!ship.isFormed()) {data.finish("舰体检查已失效，请重新检查后跃迁");return;}
        if(!HonkaiWirelessNetwork.tryExtractExact(route.getUUID("Owner"),COST)) {data.finish("跃迁等待4,915,200 HW，原舰保留");return;}
        for(var player:Hk3ResearchTeams.online(source.getServer(),route.getUUID("Team"))) {
            if(player.level()!=source||!ship.containsInterior(player.blockPosition()))continue;
            var point=new CompoundTag();point.putDouble("X",player.getX());point.putDouble("Y",player.getY());point.putDouble("Z",player.getZ());
            point.putFloat("Yaw",player.getYRot());point.putFloat("Pitch",player.getXRot());point.putBoolean("NoGravity",player.isNoGravity());
            passengers.put(player.getUUID(),point);player.closeContainer();
        }
        ship.onStructureInvalid();stage=Stage.COPY;cursor=0;data.setDirty();
    }
    private void copy(BlockPos from,BlockPos to) {
        var state=source.getBlockState(from);if(state.isAir())return;
        var entity=source.getBlockEntity(from);var nbt=entity==null?null:entity.saveWithFullMetadata();
        writing=true;
        try {
            destination.removeBlockEntity(to);
            if(destination.getBlockState(to)==state)destination.setBlock(to,Blocks.AIR.defaultBlockState(),FLAGS);
            destination.setBlock(to,state,FLAGS);
            if(nbt!=null) {
                nbt.putInt("x",to.getX());nbt.putInt("y",to.getY());nbt.putInt("z",to.getZ());
                var moved=destination.getBlockEntity(to);moved.load(nbt);moved.setChanged();
            }
        } finally {writing=false;}
    }
    private void clear(BlockPos from) {
        writing=true;
        try {source.removeBlockEntity(from);source.setBlock(from,Blocks.AIR.defaultBlockState(),FLAGS);}
        finally {writing=false;}
    }
    private void clearController() {clear(origin);}
    private void holdPassengers() {
        if(stage!=Stage.COPY&&stage!=Stage.CLEAR)return;
        passengers.forEach((id,point)->{
            var player=source.getServer().getPlayerList().getPlayer(id);if(player==null)return;
            player.setNoGravity(true);player.fallDistance=0;
            player.teleportTo(source,point.getDouble("X"),point.getDouble("Y"),point.getDouble("Z"),point.getFloat("Yaw"),point.getFloat("Pitch"));
        });
    }
    private void arrive() {
        passengers.forEach((id,original)->{
            var point=original.copy();point.putString("Dimension",route.getString("Destination"));
            point.putDouble("X",original.getDouble("X")+target.getX()-origin.getX());
            point.putDouble("Y",original.getDouble("Y")+target.getY()-origin.getY());
            point.putDouble("Z",original.getDouble("Z")+target.getZ()-origin.getZ());data.arrival(id,point);
            var player=source.getServer().getPlayerList().getPlayer(id);if(player!=null)data.deliver(player);
        });
        var ship=(Hk3HyperionMachine)MetaMachine.getMachine(destination,target);
        com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(source.getServer()).produced(route.getUUID("Owner"),"receipt:49",1);
        data.finish("整舰跃迁搬移结束 · 正在重新检查完整舰体");ship.requestIntegrityCheck();source.getServer().saveEverything(false,true,true);
    }
    private static int linear(int x,int y,int z) {return ((y+82)*549+z+274)*1145+x+1061;}
    private BlockPos position(int cell,BlockPos anchor) {
        int x=cell%1145-1061,z=cell/1145%549-274,y=cell/(1145*549)-82;
        return new BlockPos(x,y,z).rotate(rotation).offset(anchor);
    }
    @Override public void close() {
        if(plan!=null)plan.close();
        if(tickets) {
            sourceChunks.close();destinationChunks.close();
            source.getChunkSource().removeRegionTicket(CONTROL,new ChunkPos(origin),1,origin.asLong());
            destination.getChunkSource().removeRegionTicket(CONTROL,new ChunkPos(target),1,target.asLong());tickets=false;
        }
    }
}
