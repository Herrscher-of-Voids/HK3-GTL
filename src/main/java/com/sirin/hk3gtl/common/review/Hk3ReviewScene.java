package com.sirin.hk3gtl.common.review;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** 【变更记录 #1】2026-10-01 18:42:57（修订140）：删除无；新增隔离召入、原点安全返程和二审粒子投影；修改借用原版不可见交互体，不冒充琪亚娜模型；用途：场景不改玩家建筑，返程失败保留账本，攻击投影只暂停本人会面。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #2】2026-10-01 18:51:55（修订140）：删除重载旧投影的可能；新增只读陪同及投射物中止；修改传送须确认实际落点、飞行返程允许空中安全位置；用途：返回失败不清票据，陪同不增加审查次数。 */
/** 【变更记录 #3】2026-10-01 19:03:37（修订141）：删除：无；新增／修改：不可见盔甲架替换为有皮肤和配件的琪亚娜，会面归属及中断清理保持原入口；用途：琪亚娜二审形象和终审统一称谓，保留其他会话行为。 */
/** 【变更记录 #4】2026-10-01 19:08:10（修订141）：删除：无；新增／修改：二审投影上浮0.95格，静态剑尖离地约0.106格，保留原归属和清理事件；用途：完整呈现二审人物及配件。 */
/** 【变更记录 #5】2026-10-01 19:10:52（修订142）：删除：二审武器展示；新增：无；修改：撤下武器后取消0.95格避让悬浮，琪亚娜恢复平静站立会面；用途：遵循负责人只保留琪亚娜和翅膀的最新决定。 */
/** 【变更记录 #6】2026-10-01 20:04:51（修订146）：删除：无；新增：一审入场面向200格球体的仰视角；修改：首次召入与陪同共用朝向计算，保留进入前姿态用于返程；用途：让菱形核心位于入场视野，不改变三问及结算。 */
/** 【变更记录 #7】2026-10-01 20:19:52（修订147）：删除：一审64格自由移动边界；新增：每玩家每tick固定观礼位置并面向茧；修改：入场角度抽取共用计算，约束仅在一审活动会话生效，异常时暂停并尝试返程；用途：防止绕到背面，退出保持既有原位返程。 */
/** 【变更记录 #8】2026-11-04 18:48:13（修订199）：删除：一审丢失锚点或维度时静默等待；新增：选择及轮询共用场景有效性校验、退出释放临时场景；修改：二审投影失效立即拒绝选择，一审失效暂停并尝试返程；用途：关闭跨场景结算窗口及离线锚点泄漏，不删除持久返程记录。 */
public final class Hk3ReviewScene {
    public static final ResourceKey<Level> COCOON=ResourceKey.create(Registries.DIMENSION,new ResourceLocation("hk3gtl","cocoon_review"));
    private static final String OWNER="hk3_review_projection_owner";
    private static final Set<UUID> MOVING=new HashSet<>();
    private static final Map<UUID,Vec3> ANCHORS=new HashMap<>();
    private static final Map<UUID,ArmorStand> ACTORS=new HashMap<>();
    private Hk3ReviewScene(){}
    public static boolean moving(UUID id){return MOVING.contains(id);}
    public static boolean available(ServerPlayer p){return p.server.getLevel(COCOON)!=null;}
    public static void enter(ServerPlayer p,UUID meeting,long room,int index){
        var dest=p.server.getLevel(COCOON);if(dest==null)throw new IllegalStateException("召入维度未加载");
        var at=new Vec3((room%1000)*512+0.5+(index%8)*2,1,(room/1000)*512+0.5+(index/8)*2);
        Hk3ReviewReturnData.get(p.server).remember(p,meeting);
        p.stopRiding();moveIntoCocoon(p,dest,at);ANCHORS.put(p.getUUID(),at);
    }
    public static void accompany(ServerPlayer p,Hk3ReviewLedger.Snapshot meeting){
        var at=meeting.participants().stream().map(ANCHORS::get).filter(Objects::nonNull).findFirst().orElseThrow(()->new IllegalStateException("暂无在场成员"));
        var dest=p.server.getLevel(COCOON);if(dest==null)throw new IllegalStateException("召入维度未加载");
        Hk3ReviewReturnData.get(p.server).remember(p,meeting.id());p.stopRiding();at=at.add(0,0,-3);moveIntoCocoon(p,dest,at);ANCHORS.put(p.getUUID(),at);
    }
    /** 召入和位置校正共用同一观礼朝向；不覆盖返程票据。 */
    private static void moveIntoCocoon(ServerPlayer p,ServerLevel world,Vec3 at){
        move(p,world,at,Hk3CocoonView.yaw(at.x,at.z),Hk3CocoonView.pitch(at.x,at.y+p.getEyeHeight(),at.z));
    }
    /** 服务端每tick约束活动会面及陪同；客户端镜头锁之外仍维护真实站位。 */
    @SubscribeEvent public static void holdFirstReview(net.minecraftforge.event.TickEvent.PlayerTickEvent event){
        if(event.phase!=net.minecraftforge.event.TickEvent.Phase.END||!(event.player instanceof ServerPlayer p)
                ||!p.isAlive()||p.level().dimension()!=COCOON||!Hk3ReviewSessions.active(p.getUUID()))return;
        var at=ANCHORS.get(p.getUUID());if(at==null)return;
        p.stopRiding();p.setDeltaMovement(Vec3.ZERO);p.fallDistance=0;p.setSprinting(false);
        try{
            if(p.position().distanceToSqr(at)>0.000001)moveIntoCocoon(p,p.serverLevel(),at);
            else{
                float yaw=Hk3CocoonView.yaw(at.x,at.z);
                p.setYRot(yaw);p.setYHeadRot(yaw);p.setYBodyRot(yaw);
                p.setXRot(Hk3CocoonView.pitch(at.x,at.y+p.getEyeHeight(),at.z));
            }
        }catch(RuntimeException failure){
            com.mojang.logging.LogUtils.getLogger().warn("[HK3GTL] 一审观礼位置校正失败，暂停并保留返程票据",failure);
            Hk3ReviewSessions.pause(p,false,false);
        }
    }
    private static void move(ServerPlayer p,ServerLevel world,Vec3 at,float yaw,float pitch){
        MOVING.add(p.getUUID());try{
            p.teleportTo(world,at.x,at.y,at.z,yaw,pitch);
            if(p.level()!=world||p.position().distanceToSqr(at)>1)throw new IllegalStateException("传送被拒绝，保留返程记录");
            p.fallDistance=0;p.setDeltaMovement(Vec3.ZERO);
        }finally{MOVING.remove(p.getUUID());}
    }
    /** 原位置受阻时仅寻找附近安全地面；没有安全位置则保留返程票据，绝不覆盖建筑或默认为出生点。 */
    public static boolean returnHome(ServerPlayer p){
        var data=Hk3ReviewReturnData.get(p.server);var r=data.point(p.getUUID());if(r==null)return true;if(!p.isAlive())return false;
        var dest=p.server.getLevel(ResourceKey.create(Registries.DIMENSION,new ResourceLocation(r.dimension())));
        Vec3 at=null;if(dest!=null){
            var original=new Vec3(r.x(),r.y(),r.z());if(safe(p,dest,original))at=original;
            else outer:for(int radius=0;radius<=8;radius++)for(int dy=0;dy<=8;dy++)for(int sign:new int[]{1,-1})for(int dx=-radius;dx<=radius;dx++)for(int dz=-radius;dz<=radius;dz++){
                if(Math.max(Math.abs(dx),Math.abs(dz))!=radius)continue;
                var candidate=new Vec3(Math.floor(r.x())+dx+0.5,Math.floor(r.y())+dy*sign,Math.floor(r.z())+dz+0.5);
                if(safe(p,dest,candidate)){at=candidate;break outer;}
            }
        }
        if(at==null){p.sendSystemMessage(Component.translatable("hk3gtl.review.return_blocked"));return false;}
        try{move(p,dest,at,r.yaw(),r.pitch());}
        catch(RuntimeException failure){com.mojang.logging.LogUtils.getLogger().warn("[HK3GTL] 审查返程暂时失败，保留票据",failure);p.sendSystemMessage(Component.translatable("hk3gtl.review.return_blocked"));return false;}
        data.returned(p.getUUID());ANCHORS.remove(p.getUUID());return true;
    }
    private static boolean safe(ServerPlayer p,ServerLevel level,Vec3 at){
        var feet=BlockPos.containing(at);if(at.y<level.getMinBuildHeight()+1||at.y+2>=level.getMaxBuildHeight()||!level.getWorldBorder().isWithinBounds(feet))return false;
        var floor=level.getBlockState(feet.below());
        if((!p.getAbilities().flying&&!floor.isFaceSturdy(level,feet.below(),Direction.UP))||!level.getFluidState(feet).isEmpty())return false;
        if(floor.is(net.minecraft.world.level.block.Blocks.MAGMA_BLOCK)||floor.is(net.minecraft.world.level.block.Blocks.CAMPFIRE)||floor.is(net.minecraft.world.level.block.Blocks.SOUL_CAMPFIRE)||floor.is(net.minecraft.world.level.block.Blocks.CACTUS))return false;
        return level.getBlockState(feet).isAir()&&level.getBlockState(feet.above()).isAir()&&level.noCollision(p,p.getBoundingBox().move(at.subtract(p.position())));
    }
    public static void projection(ServerPlayer p){
        removeProjection(p.getUUID());var at=p.position().add(p.getLookAngle().multiply(2,0,2));
        var actor=com.sirin.hk3gtl.common.entity.Hk3Entities.KIANA_REVIEW.get().create(p.serverLevel());
        if(actor==null)throw new IllegalStateException("琪亚娜实体创建失败");
        float yaw=(float)Math.toDegrees(Math.atan2(p.getZ()-at.z,p.getX()-at.x))-90;
        actor.moveTo(at.x,at.y,at.z,yaw,0);actor.setYBodyRot(yaw);actor.setYHeadRot(yaw);
        actor.setCustomName(Component.translatable("hk3gtl.review.kiana_projection"));actor.setCustomNameVisible(true);actor.getPersistentData().putUUID(OWNER,p.getUUID());
        ACTORS.put(p.getUUID(),actor);
        if(!p.serverLevel().addFreshEntity(actor)){removeProjection(p.getUUID());throw new IllegalStateException("二审投影生成失败");}
    }
    /** 选择包与轮询共享检查，避免投影移除至下一次轮询之间仍能结算。 */
    public static boolean valid(ServerPlayer p,Hk3ReviewLedger.Kind kind){
        if(!p.isAlive())return false;
        if(kind==Hk3ReviewLedger.Kind.FIRST)return ANCHORS.containsKey(p.getUUID())&&p.level().dimension()==COCOON;
        var actor=ACTORS.get(p.getUUID());
        return actor!=null&&!actor.isRemoved()&&actor.level()==p.level()&&actor.distanceToSqr(p)<=4096;
    }
    public static void tick(ServerPlayer p,Hk3ReviewLedger.Kind kind){
        if(!valid(p,kind)){Hk3ReviewSessions.pause(p,false,false);return;}
        if(kind==Hk3ReviewLedger.Kind.FIRST){
            var anchor=ANCHORS.get(p.getUUID());
            if(p.server.getTickCount()%20==0)p.serverLevel().sendParticles(p,ParticleTypes.END_ROD,true,anchor.x,anchor.y+3,anchor.z+3,6,0.4,1,0.4,0.01);
        }else{
            var a=ACTORS.get(p.getUUID());
            if(p.server.getTickCount()%10==0){
                p.serverLevel().sendParticles(p,ParticleTypes.REVERSE_PORTAL,true,a.getX(),a.getY()+1,a.getZ(),12,0.15,0.8,0.15,0.01);
                p.serverLevel().sendParticles(p,ParticleTypes.END_ROD,true,a.getX(),a.getY()+1.7,a.getZ(),4,0.25,0.2,0.25,0.01);
            }
        }
    }
    public static void release(UUID id){removeProjection(id);ANCHORS.remove(id);}
    public static void removeProjection(UUID id){var actor=ACTORS.remove(id);if(actor!=null)actor.discard();}
    public static void clear(){for(var actor:ACTORS.values())actor.discard();ACTORS.clear();ANCHORS.clear();MOVING.clear();}
    @SubscribeEvent public static void attack(AttackEntityEvent e){
        var n=e.getTarget().getPersistentData();if(!n.hasUUID(OWNER))return;e.setCanceled(true);
        if(e.getEntity() instanceof ServerPlayer p&&p.getUUID().equals(n.getUUID(OWNER)))Hk3ReviewSessions.pause(p,false,true);
    }
    @SubscribeEvent public static void interact(PlayerInteractEvent.EntityInteract e){if(e.getTarget().getPersistentData().hasUUID(OWNER))e.setCanceled(true);}
    @SubscribeEvent public static void projectile(net.minecraftforge.event.entity.ProjectileImpactEvent e){
        if(e.getRayTraceResult() instanceof net.minecraft.world.phys.EntityHitResult hit&&hit.getEntity().getPersistentData().hasUUID(OWNER)){
            e.setCanceled(true);var owner=e.getProjectile().getOwner();
            if(owner instanceof ServerPlayer p&&p.getUUID().equals(hit.getEntity().getPersistentData().getUUID(OWNER)))Hk3ReviewSessions.pause(p,false,true);
        }
    }
    @SubscribeEvent public static void damage(LivingAttackEvent e){
        if(e.getEntity().getPersistentData().hasUUID(OWNER)||e.getEntity() instanceof ServerPlayer p&&p.level().dimension()==COCOON)e.setCanceled(true);
    }
    @SubscribeEvent public static void loaded(EntityJoinLevelEvent e){
        if(!e.getLevel().isClientSide()&&e.getEntity().getPersistentData().hasUUID(OWNER)&&ACTORS.get(e.getEntity().getPersistentData().getUUID(OWNER))!=e.getEntity())e.setCanceled(true);
    }
    @SubscribeEvent public static void breakBlock(BlockEvent.BreakEvent e){if(e.getPlayer().level().dimension()==COCOON)e.setCanceled(true);}
    @SubscribeEvent public static void placeBlock(BlockEvent.EntityPlaceEvent e){if(e.getEntity()!=null&&e.getEntity().level().dimension()==COCOON)e.setCanceled(true);}
}
