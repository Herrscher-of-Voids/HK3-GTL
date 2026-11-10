package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.decoration.Painting;
import net.minecraft.world.entity.animal.Cat;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 06:23:20（修订128）：删除无；新增服务端真实事件旁注；修改无；用途：原条件、原世界结果不变，只授个人可选收藏。 */
public final class Hk3EggPaintingScenes {
    private Hk3EggPaintingScenes(){}
    public static void placed(ServerPlayer p,Painting painting){
        var s=Hk3EggRuntime.state(p);s.putUUID("eggPainting",painting.getUUID());s.putString("eggPaintingDim",p.level().dimension().location().toString());s.putLong("eggPaintingAt",p.server.overworld().getGameTime());s.putDouble("eggPaintingWalk",0);s.putBoolean("eggPaintingTurned",false);
        s.putDouble("eggPaintX",p.getX());s.putDouble("eggPaintY",p.getY());s.putDouble("eggPaintZ",p.getZ());
        if(!p.level().getEntitiesOfClass(Cat.class,painting.getBoundingBox().inflate(4),c->c.isAlive()&&c.isTame()).isEmpty())s.putUUID("catPainting",painting.getUUID());
    }
    public static void note(ServerPlayer p,String title){var s=Hk3EggRuntime.state(p);if(title.equals("半张照片")&&s.hasUUID("catPainting")){Hk3EggVanilla.caseEvent(p,409);s.remove("catPainting");}}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;var s=Hk3EggRuntime.state(p);if(!s.hasUUID("eggPainting"))return;
        long now=p.server.overworld().getGameTime();var entity=p.serverLevel().getEntity(s.getUUID("eggPainting"));
        var last=new net.minecraft.world.phys.Vec3(s.getDouble("eggPaintX"),s.getDouble("eggPaintY"),s.getDouble("eggPaintZ"));var delta=p.position().subtract(last);
        if(entity==null||entity.isRemoved()||!s.getString("eggPaintingDim").equals(p.level().dimension().location().toString())||now-s.getLong("eggPaintingAt")>1200||delta.lengthSqr()>2.25||p.getAbilities().flying||p.isPassenger()||!p.isAlive()){s.remove("eggPainting");return;}
        var away=p.position().subtract(entity.position()).normalize();
        if(now-s.getLong("eggPaintingAt")<=60&&p.getLookAngle().dot(away)>.7)s.putBoolean("eggPaintingTurned",true);
        if(s.getBoolean("eggPaintingTurned")&&p.onGround()&&delta.dot(away)>0)s.putDouble("eggPaintingWalk",s.getDouble("eggPaintingWalk")+Math.sqrt(delta.x*delta.x+delta.z*delta.z));
        if(s.getDouble("eggPaintingWalk")>=8){Hk3EggVanilla.caseEvent(p,395);s.remove("eggPainting");}
        s.putDouble("eggPaintX",p.getX());s.putDouble("eggPaintY",p.getY());s.putDouble("eggPaintZ",p.getZ());
    }
}
