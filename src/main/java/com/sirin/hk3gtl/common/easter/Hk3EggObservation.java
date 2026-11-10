package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.item.*;
import net.minecraft.world.entity.monster.Slime;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
/** 【变更记录 #1】2026-10-01 04:53:17（修订128）：删除无；新增服务器视线与连续观察tick；用途：仅已加载区块、本人视向及真实使用望远镜，离开条件即时重置，不用物品持有冒充观察。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #2】2026-10-01 12:18:50（修订128）：删除：无；新增/修改：按原版天空旋转推导月亮方向并逐段遮挡检查；红玻璃月视与月升连续十秒回屋，不用抬头冒充月视；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 16:30:04（修订134）：删除破晓之时额外的30度限制与首块玻璃顶部见天判据；新增逐层穿玻璃后实际天空检查；修改保留主世界23000至23999及100连续刻；用途：修复正常日出视向与高窗漏触发，不改变其他彩蛋。 */
public final class Hk3EggObservation {
    private Hk3EggObservation(){}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();
        if(s.getLong("lookLastTick")!=now-1){s.remove("skyEyeTicks");s.remove("redGlassTicks");s.remove("dawnGlassTicks");s.remove("moonRiseStart");s.remove("moonWatched");}
        s.putLong("lookLastTick",now);
        boolean sky=p.getXRot()<-45&&p.level().canSeeSky(p.blockPosition().above());
        boolean night=p.level().isNight();
        double angle=p.level().getTimeOfDay(0)*Math.PI*2;var moon=new Vec3(Math.sin(angle),-Math.cos(angle),0);
        boolean aiming=p.level().dimension()==Level.OVERWORLD&&night&&!p.level().isRaining()&&moon.y>0&&p.getLookAngle().dot(moon)>.985;
        boolean glass=false,visible=aiming;
        if(aiming){var origin=p.getEyePosition();for(int i=1;i<=192;i++){var pos=BlockPos.containing(origin.add(moon.scale(i*.5)));if(pos.getY()>=p.level().getMaxBuildHeight())break;if(!p.level().hasChunkAt(pos)){visible=false;break;}var block=p.level().getBlockState(pos);if(block.is(Blocks.RED_STAINED_GLASS)){glass=true;continue;}if(!block.getCollisionShape(p.level(),pos).isEmpty()){visible=false;break;}}}
        if(visible&&glass)Hk3EggVanilla.caseEvent(p,425);
        long moonDay=Math.floorMod(p.level().getDayTime(),24000);
        if(visible){if(!s.contains("moonRiseStart")&&moonDay>=12000&&moonDay<=14000)s.putLong("moonRiseStart",now);if(s.contains("moonRiseStart")&&now-s.getLong("moonRiseStart")>=200)s.putBoolean("moonWatched",true);}else s.remove("moonRiseStart");
        if(s.getBoolean("moonWatched")&&now%20==0&&Hk3EggRooms.room(p)!=null){Hk3EggVanilla.caseEvent(p,452);s.remove("moonWatched");}
        if(!night){s.remove("moonRiseStart");s.remove("moonWatched");}
        advance(p,"skyEyeTicks",night&&sky&&(p.getMainHandItem().is(Items.ENDER_EYE)||p.getOffhandItem().is(Items.ENDER_EYE)),60,424);
        boolean spy=p.isUsingItem()&&p.getUseItem().is(Items.SPYGLASS);
        var hit=(spy||p.getXRot()<-30)?sight(p,64):null;
        boolean red=hit!=null&&p.level().getBlockState(hit.getBlockPos()).is(Blocks.RED_STAINED_GLASS);
        advance(p,"redGlassTicks",spy&&red,60,394);
        if(!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-401")) {
            boolean valid=Hk3EggScpFacts.dawn(p.level().dimension()==Level.OVERWORLD,p.level().getDayTime(),p.getLookAngle().y)&&Hk3EggDawnSight.visible(p);
            int ticks=Hk3EggScpFacts.nextObservation(s.getInt("dawnGlassTicks"),true,valid);
            s.putInt("dawnGlassTicks",ticks);if(ticks==100)Hk3EggVanilla.caseEvent(p,401);
        }
        if(spy&&hit!=null&&hit.getLocation().distanceTo(p.getEyePosition())>=16&&p.level().getBiome(p.blockPosition()).is(BiomeTags.IS_MOUNTAIN))s.putBoolean("mountainSpied",true);
        if(spy&&hit!=null&&p.level().getBiome(p.blockPosition()).is(BiomeTags.IS_JUNGLE)&&p.level().getBlockState(hit.getBlockPos()).is(BlockTags.LEAVES))Hk3EggVanilla.caseEvent(p,429);
        if(now%20==0&&p.level().isDay()&&!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-421"))
            for(var slime:p.level().getEntitiesOfClass(Slime.class,p.getBoundingBox().inflate(32),a->a.isAlive()&&a.getType()==net.minecraft.world.entity.EntityType.SLIME)){
                var to=slime.getEyePosition().subtract(p.getEyePosition());if(to.lengthSqr()>0&&p.getLookAngle().dot(to.normalize())>.8&&p.hasLineOfSight(slime)){Hk3EggVanilla.caseEvent(p,421);break;}
            }
    }
    private static BlockHitResult sight(ServerPlayer p,int distance){
        var from=p.getEyePosition();var to=from.add(p.getLookAngle().scale(distance));
        for(int n=0;n<=distance;n+=4)if(!p.level().hasChunkAt(BlockPos.containing(from.add(p.getLookAngle().scale(n)))))return null;
        var hit=p.level().clip(new ClipContext(from,to,ClipContext.Block.OUTLINE,ClipContext.Fluid.NONE,p));return hit.getType()==HitResult.Type.BLOCK?hit:null;
    }
    private static void advance(ServerPlayer p,String key,boolean condition,int target,int id){
        var s=Hk3EggRuntime.state(p);int ticks=condition?Math.min(target,Math.max(0,s.getInt(key))+1):0;s.putInt(key,ticks);if(ticks==target)Hk3EggVanilla.caseEvent(p,id);
    }
}
