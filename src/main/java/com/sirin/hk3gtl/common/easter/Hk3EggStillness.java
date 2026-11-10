package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 05:59:33（修订128）：删除无；新增虚数维度连续30秒固定锚点距离验证；修改无；用途：原条件的有界只读检测，不授研究资格。 */
public final class Hk3EggStillness {
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();
        boolean allowed=p.level().dimension().equals(com.sirin.hk3gtl.common.dimension.Hk3Dimensions.IMAGINARY)&&p.onGround()&&!p.isPassenger();
        var anchor=new Vec3(s.getDouble("stillX"),s.getDouble("stillY"),s.getDouble("stillZ"));
        if(!allowed||s.getLong("stillLast")!=now-1||p.position().distanceToSqr(anchor)>=1){s.putDouble("stillX",p.getX());s.putDouble("stillY",p.getY());s.putDouble("stillZ",p.getZ());s.putInt("stillTicks",0);}
        else{int ticks=Math.min(600,s.getInt("stillTicks")+1);s.putInt("stillTicks",ticks);if(ticks==600)Hk3EggVanilla.caseEvent(p,21);}
        s.putLong("stillLast",now);
    }
}
