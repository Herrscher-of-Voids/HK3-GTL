package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.inventory.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 05:28:18（修订128）：删除无；新增修复工具经验回执、设置床重生点、实际挡箭离战及原版箱子开启顺序；修改无；用途：只读真实事件，保留取消结果，不授正式资格。 */
/** 【变更记录 #2】2026-10-01 05:59:33（修订128）：删除：无；新增/修改：扩展剪刀等工具实际修复；命名工具真实铁砧修复后在成品保存身份与次数；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 06:25:16（修订128）：删除：无；新增/修改：雪地自然战利品首次展开后必须成功打开对应单双箱菜单，未打开不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggLifeEvents {
    private static final Map<UUID,PlayerSetSpawnEvent> SPAWN=new java.util.concurrent.ConcurrentHashMap<>();
    private static final Map<UUID,ShieldBlockEvent> SHIELD=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggLifeEvents(){}
    @SubscribeEvent public static void spawn(PlayerSetSpawnEvent e){if(e.getEntity() instanceof ServerPlayer&&!e.isForced()&&e.getNewSpawn()!=null)SPAWN.put(e.getEntity().getUUID(),e);}
    @SubscribeEvent public static void shield(ShieldBlockEvent e){if(e.getEntity() instanceof ServerPlayer)SHIELD.put(e.getEntity().getUUID(),e);}
    @SubscribeEvent public static void repair(AnvilRepairEvent e){
        if(!(e.getEntity() instanceof ServerPlayer p)||!(p.containerMenu instanceof AnvilMenu menu))return;
        var before=e.getLeft();var after=e.getOutput();
        if((before.getItem() instanceof TieredItem||before.is(Items.SHEARS)||before.is(Items.FLINT_AND_STEEL)||before.is(Items.FISHING_ROD)||before.is(Items.BOW)||before.is(Items.CROSSBOW))&&before.isDamaged()&&after.is(before.getItem())&&after.getDamageValue()<before.getDamageValue()){
            if(before.hasCustomHoverName()){
                var tag=after.getOrCreateTag();var old=before.getTag();
                if(old!=null&&old.hasUUID("Hk3EggToolIdentity"))tag.putUUID("Hk3EggToolIdentity",old.getUUID("Hk3EggToolIdentity"));else tag.putUUID("Hk3EggToolIdentity",UUID.randomUUID());
                int repairs=Math.min(3,Math.max(0,old==null?0:old.getInt("Hk3EggRepairs"))+1);tag.putInt("Hk3EggRepairs",repairs);
                if(repairs>=3)Hk3EggVanilla.caseEvent(p,468);
            }
            var state=Hk3EggRuntime.state(p);state.putInt("repairExperience",p.isCreative()?0:menu.getCost());state.putLong("repairAt",p.server.overworld().getGameTime());
        }
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();
        var spawn=SPAWN.remove(p.getUUID());
        if(spawn!=null&&!spawn.isCanceled()&&spawn.getSpawnLevel().equals(p.getRespawnDimension())&&spawn.getNewSpawn().equals(p.getRespawnPosition())){
            var level=p.server.getLevel(spawn.getSpawnLevel());var at=spawn.getNewSpawn();
            if(level!=null&&level.hasChunkAt(at)&&level.getBlockState(at).getBlock() instanceof BedBlock)s.putLong("bedSpawnSetAt",now);
        }
        var block=SHIELD.remove(p.getUUID());
        if(block!=null&&!block.isCanceled()&&block.getBlockedDamage()>0){
            s.putLong("shieldBlockedAt",now);
            if(block.getDamageSource().getDirectEntity() instanceof net.minecraft.world.entity.projectile.AbstractArrow&&block.getDamageSource().getEntity() instanceof net.minecraft.world.entity.monster.AbstractSkeleton enemy){
                s.putUUID("blockedSkeleton",enemy.getUUID());s.putString("blockedSkeletonDimension",p.level().dimension().location().toString());
                s.putDouble("blockedSkeletonX",enemy.getX());s.putDouble("blockedSkeletonZ",enemy.getZ());
            }
        }
        if(now%20==0&&s.hasUUID("blockedSkeleton")&&p.isAlive()&&p.level().dimension().location().toString().equals(s.getString("blockedSkeletonDimension"))){
            var enemy=p.serverLevel().getEntity(s.getUUID("blockedSkeleton"));
            double x=enemy==null?s.getDouble("blockedSkeletonX"):enemy.getX(),z=enemy==null?s.getDouble("blockedSkeletonZ"):enemy.getZ();
            boolean clear=p.level().getEntitiesOfClass(net.minecraft.world.entity.Mob.class,p.getBoundingBox().inflate(32),m->m.isAlive()&&m.getTarget()==p).isEmpty();
            if(p.distanceToSqr(x,p.getY(),z)>32*32&&clear){Hk3EggVanilla.caseEvent(p,478);s.remove("blockedSkeleton");}
        }
    }
    public static void note(ServerPlayer p,String title,String body){
        var s=Hk3EggRuntime.state(p);
        if(s.contains("bedSpawnSetAt")&&(title.equals("歇会儿")||body.strip().equals("歇会儿")))Hk3EggVanilla.caseEvent(p,477);
        if(s.contains("repairAt")&&java.util.regex.Pattern.compile("(?:经验|等级|花费|消耗)[：:＝= ]*"+s.getInt("repairExperience")+"(?![0-9])|(?<![0-9])"+s.getInt("repairExperience")+"\\s*(?:级|经验)").matcher(body).find())Hk3EggVanilla.caseEvent(p,455);
    }
    @SubscribeEvent public static void opened(PlayerContainerEvent.Open e){
        if(e.getEntity() instanceof ServerPlayer p&&e.getContainer() instanceof ChestMenu menu){
            var state=Hk3EggRuntime.state(p);
            if(state.contains("snowLootChest")&&state.getLong("snowLootTick")==p.server.overworld().getGameTime()&&state.getString("snowLootDim").equals(p.level().dimension().location().toString())){
                for(var part:Hk3EggChests.parts(p,menu.getContainer()))if(part.getBlockPos().asLong()==state.getLong("snowLootChest"))Hk3EggVanilla.caseEvent(p,431);
                state.remove("snowLootChest");
            }
        }
        if(e.getEntity() instanceof ServerPlayer p&&e.getContainer() instanceof ChestMenu menu&&menu.getContainer() instanceof net.minecraft.world.level.block.entity.ChestBlockEntity){
            var s=Hk3EggRuntime.state(p);if(s.contains("shieldBlockedAt")&&p.server.overworld().getGameTime()-s.getLong("shieldBlockedAt")<=200)Hk3EggVanilla.caseEvent(p,481);
        }
    }
    public static void lamp(ServerPlayer p,BlockPos pos,net.minecraft.world.level.block.state.BlockState block){
        var s=Hk3EggRuntime.state(p);
        if(s.contains("golemRepairedAt")&&p.server.overworld().getGameTime()-s.getLong("golemRepairedAt")<=1200&&p.level().isNight()&&block.getLightEmission(p.level(),pos)>0)Hk3EggVanilla.caseEvent(p,448);
    }
    @SubscribeEvent public static void respawn(PlayerEvent.PlayerRespawnEvent e){if(e.getEntity() instanceof ServerPlayer p)Hk3EggRuntime.state(p).remove("blockedSkeleton");}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){SPAWN.remove(e.getEntity().getUUID());SHIELD.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){SPAWN.clear();SHIELD.clear();}
}
