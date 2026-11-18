package com.sirin.hk3gtl.common.easter;

import com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.Map;

 





 
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggFestivalActions {
    private static final String MOVEMENT = "festivalMovement";
    private Hk3EggFestivalActions() {}
    public static boolean lantern(BlockState state) { return state.is(Blocks.LANTERN) || state.is(Blocks.SOUL_LANTERN); }

    public static void placed(ServerPlayer p,BlockPos pos,BlockState state) {
        if (!lantern(state) || unlocked(p,374)) return;
        var facts=Hk3EggCalendar.facts(Hk3EggCalendar.now(),p.server.overworld().getDayTime());
        if (!"qixi".equals(facts.get("lunar_festival"))) return;
        var memory=Hk3EggBuildMemory.get(p.serverLevel());
        if (!memory.owns(p,pos)) return;
        for (var direction:Direction.values()) {
            var side=pos.relative(direction);
            if (p.level().hasChunkAt(side) && lantern(p.level().getBlockState(side)) && memory.owns(p,side)) {
                Hk3EggRuntime.observe(p,"festival_adjacent_lanterns",facts);
                return;
            }
        }
    }

    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent event) {
        if (event.phase!=TickEvent.Phase.END || !(event.player instanceof ServerPlayer p)) return;
        if (unlocked(p,371) && unlocked(p,373) && unlocked(p,376)) return;
        if (!p.isAlive() || p.isSpectator()) { reset(p); return; }
        var date=Hk3EggCalendar.now().toLocalDate();
        var facts=Hk3LunarCalendar.facts(date,Hk3EggCalendar.zone());
        var festival=facts.getOrDefault("lunar_festival","");
        if (festival.equals("lantern_festival") && !unlocked(p,371) && p.level().dimensionType().hasSkyLight()
                && p.level().isNight() && p.getXRot()<-45 && p.level().canSeeSky(p.blockPosition().above()))
            Hk3EggRuntime.observe(p,"festival_night_sky",facts);
        if (!festival.equals("dragon_boat") && !festival.equals("double_ninth")) { reset(p); return; }
        var root=Hk3EggRuntime.state(p);
        var previous=root.getCompound(MOVEMENT);
        long tick=p.server.overworld().getGameTime();
        if(previous.contains("Tick",4)&&previous.getLong("Tick")==tick)return;
        String dimension=p.level().dimension().location().toString();
        var delta=p.position().subtract(new Vec3(previous.getDouble("X"),previous.getDouble("Y"),previous.getDouble("Z")));
        boolean continuous=previous.contains("Tick",4) && previous.getLong("Tick")==tick-1
                && previous.getString("Date").equals(date.toString()) && previous.getString("Dimension").equals(dimension)
                && delta.lengthSqr()<=2.25;
        boolean safe=!p.getAbilities().flying && !p.isFallFlying() && !p.isSwimming()
                && !p.isInLava() && !p.isOnFire() && p.fallDistance<=0.01f;
        boolean walking=safe && p.onGround() && !p.isPassenger();
        double horizontal=delta.horizontalDistance();
        if (festival.equals("double_ninth") && !unlocked(p,376) && continuous && walking
                && previous.getBoolean("Walking") && horizontal>0.0001 && p.getY()>p.level().getSeaLevel()+64
                && p.level().hasChunkAt(p.blockPosition().below())
                && p.level().getBlockState(p.blockPosition().below()).isFaceSturdy(p.level(),p.blockPosition().below(),Direction.UP))
            Hk3EggRuntime.observe(p,"festival_safe_walk",facts);
        double distance=0;
        if (festival.equals("dragon_boat") && safe && p.getVehicle() instanceof Boat boat
                && boat.getControllingPassenger()==p && boat.isInWater()) {
            if (continuous && previous.hasUUID("Boat") && previous.getUUID("Boat").equals(boat.getUUID())) {
                distance=previous.getDouble("BoatDistance");
                if (boat.getPaddleState(0) || boat.getPaddleState(1)) distance=Math.min(20,distance+horizontal);
            }
            previous.putUUID("Boat",boat.getUUID());
            if (distance>=20 && !unlocked(p,373)) Hk3EggRuntime.observe(p,"festival_rowed",facts);
        } else previous.remove("Boat");
        previous.putDouble("BoatDistance",distance);
        previous.putDouble("X",p.getX()); previous.putDouble("Y",p.getY()); previous.putDouble("Z",p.getZ());
        previous.putLong("Tick",tick); previous.putString("Date",date.toString()); previous.putString("Dimension",dimension);
        previous.putBoolean("Walking",walking); root.put(MOVEMENT,previous);
    }

    private static boolean unlocked(ServerPlayer p,int id) { return Hk3NarrativeLog.isUnlocked(p,"E-EG-"+id); }
    private static void reset(ServerPlayer p) { Hk3EggRuntime.state(p).remove(MOVEMENT); }
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e) { if(e.getEntity() instanceof ServerPlayer p) reset(p); }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e) { if(e.getEntity() instanceof ServerPlayer p) reset(p); }
    @SubscribeEvent public static void death(LivingDeathEvent e) { if(e.getEntity() instanceof ServerPlayer p) reset(p); }
}
