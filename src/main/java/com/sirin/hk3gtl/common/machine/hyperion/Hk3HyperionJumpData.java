package com.sirin.hk3gtl.common.machine.hyperion;

import com.sirin.hk3gtl.common.multiblock.build.Hk3HyperionJumpTask;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3HyperionJumpData extends SavedData {
    private static final Map<MinecraftServer,Hk3HyperionJumpData> ACTIVE=new ConcurrentHashMap<>();
    private final Map<UUID,CompoundTag> arrivals=new LinkedHashMap<>();
    private Hk3HyperionJumpTask task;
    private String status="单次跃迁 4,915,200 HW · 保持舰体朝向";

    public static Hk3HyperionJumpData get(MinecraftServer server) {
        return ACTIVE.computeIfAbsent(server,s->com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(s,
                "hk3gtl_hyperion_jump",Hk3HyperionJumpData::load,Hk3HyperionJumpData::new));
    }
    public String status() {return task==null?status:task.progress();}
    public static boolean locked(ServerLevel level,BlockPos pos) {
        var data=ACTIVE.get(level.getServer());
        return data!=null&&data.task!=null&&data.task.contains(level,pos);
    }
    public static boolean blocksWrite(ServerLevel level,BlockPos pos) {
        var data=ACTIVE.get(level.getServer());
        return data!=null&&data.task!=null&&!data.task.writing()&&data.task.contains(level,pos);
    }
    public static boolean moving(Hk3HyperionMachine ship) {
        var data=ACTIVE.get(ship.getLevel().getServer());
        return data!=null&&data.task!=null&&data.task.isSource(ship);
    }
    public void start(Hk3HyperionMachine ship,ServerPlayer actor,String dimension,BlockPos target) {
        if(task!=null) {actor.sendSystemMessage(net.minecraft.network.chat.Component.literal("服务器已有整舰跃迁任务"));return;}
        var server=actor.server;var team=ship.getResearchTeamUUID();var research=Hk3ResearchData.get(server);
        if(!Hk3ResearchTeams.canManage(server,team,actor.getUUID())||!actor.getAbilities().mayBuild) {
            message(actor,"只有舰体所属团队的管理成员可导航");return;
        }
        if(!ship.hasVerifiedHull()||!ship.isFormed()||Hk3UniversalTerminalBuilder.isBuilding(ship)
                ||ship.getRecipeLogic().getProgress()>0) {message(actor,"请先完成舰载工艺并通过完整舰体检查");return;}
        if(!Hk3ResearchExecutionContracts.permitsMachine(research,team,"H01",research.hasReviewPermission(team,2))) {
            message(actor,"尚未取得H01正式运行研究许可");return;
        }
        var id=ResourceLocation.tryParse(dimension);
        var dest=id==null?null:server.getLevel(ResourceKey.create(Registries.DIMENSION,id));
        if(dest==null) {message(actor,"目标维度不存在");return;}
        var source=(ServerLevel)ship.getLevel();
        if(source.dimension()==com.sirin.hk3gtl.common.dimension.Hk3Dimensions.IMAGINARY
                ||dest.dimension()==com.sirin.hk3gtl.common.dimension.Hk3Dimensions.IMAGINARY
                ||source.dimension()==com.sirin.hk3gtl.common.review.Hk3ReviewScene.COCOON
                ||dest.dimension()==com.sirin.hk3gtl.common.review.Hk3ReviewScene.COCOON) {
            message(actor,"终审场景沿原准入，舰体不能跃入或跃出");return;
        }
        var bounds=Hk3HyperionMachine.hullBounds(target,ship.getFrontFacing());
        if(bounds.min().getY()<dest.getMinBuildHeight()||bounds.max().getY()>=dest.getMaxBuildHeight()
                ||!dest.getWorldBorder().isWithinBounds(bounds.min())||!dest.getWorldBorder().isWithinBounds(bounds.max())) {
            message(actor,"目标高度或世界边界不能容纳整舰");return;
        }
        var old=ship.hullBounds();
        if(source==dest&&old.min().getX()<=bounds.max().getX()&&old.max().getX()>=bounds.min().getX()
                &&old.min().getY()<=bounds.max().getY()&&old.max().getY()>=bounds.min().getY()
                &&old.min().getZ()<=bounds.max().getZ()&&old.max().getZ()>=bounds.min().getZ()) {
            message(actor,"同维跃迁的原舰与目的范围不能重叠");return;
        }
        ship.getRecipeLogic().setWorkingEnabled(false);
        var occupied=new net.minecraft.world.phys.AABB(old.min(),old.max().offset(1,1,1)).inflate(8);
        for(var player:source.players())if(occupied.contains(player.position()))player.closeContainer();
        task=new Hk3HyperionJumpTask(this,ship,dest,target);setDirty();
    }
    private void message(ServerPlayer player,String text) {status=text;setDirty();player.sendSystemMessage(net.minecraft.network.chat.Component.literal(text));}
    public void finish(String text) {task.close();task=null;status=text;setDirty();}
    public void arrival(UUID player,CompoundTag point) {arrivals.put(player,point);setDirty();}
    public void deliver(ServerPlayer player) {
        var point=arrivals.remove(player.getUUID());if(point==null)return;
        var dest=player.server.getLevel(ResourceKey.create(Registries.DIMENSION,new ResourceLocation(point.getString("Dimension"))));
        player.teleportTo(dest,point.getDouble("X"),point.getDouble("Y"),point.getDouble("Z"),point.getFloat("Yaw"),point.getFloat("Pitch"));
        player.setNoGravity(point.getBoolean("NoGravity"));player.fallDistance=0;setDirty();
    }
    @Override public CompoundTag save(CompoundTag tag) {
        tag.putString("Status",status);if(task!=null)tag.put("Task",task.save());
        var rows=new ListTag();arrivals.forEach((id,point)->{var row=point.copy();row.putUUID("Player",id);rows.add(row);});tag.put("Arrivals",rows);return tag;
    }
    public static Hk3HyperionJumpData load(CompoundTag tag) {
        var data=new Hk3HyperionJumpData();data.status=tag.getString("Status");
        if(tag.contains("Task"))data.task=new Hk3HyperionJumpTask(data,tag.getCompound("Task"));
        for(var raw:tag.getList("Arrivals",10)) {var point=(CompoundTag)raw;data.arrivals.put(point.getUUID("Player"),point);}
        return data;
    }
    @SubscribeEvent public static void started(ServerStartedEvent event) {get(event.getServer());}
    @SubscribeEvent public static void stopped(ServerStoppedEvent event) {
        var data=ACTIVE.remove(event.getServer());if(data!=null&&data.task!=null)data.task.close();
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        var data=get(event.getServer());if(data.task!=null)data.task.tick(event.getServer());
    }
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent event) {
        if(event.getEntity() instanceof ServerPlayer player)get(player.server).deliver(player);
    }
    @SubscribeEvent public static void interact(PlayerInteractEvent.RightClickBlock event) {
        if(event.getLevel() instanceof ServerLevel level&&locked(level,event.getPos()))event.setCanceled(true);
    }
    @SubscribeEvent public static void breakBlock(BlockEvent.BreakEvent event) {
        if(event.getLevel() instanceof ServerLevel level&&locked(level,event.getPos()))event.setCanceled(true);
    }
}
