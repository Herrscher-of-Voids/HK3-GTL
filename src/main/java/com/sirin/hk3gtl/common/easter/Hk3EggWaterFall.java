package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 12:32:24（修订128）：删除：无；新增/修改：成功放水建立源水归属，本人挖脚下后的实际无伤落水才触发；死亡、飞行、换维度或超时撤销；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggWaterFall {
    private Hk3EggWaterFall(){}
    public static void placed(ServerPlayer p,BlockPos pos){
        var state=p.level().getBlockState(pos);
        if(!state.getFluidState().is(FluidTags.WATER)||!state.getFluidState().isSource())return;
        Hk3EggBuildMemory.get(p.serverLevel()).placed(p,pos);
    }
    public static void broken(ServerPlayer p,BlockPos pos){
        if(!p.onGround()||p.isCreative()||p.isSpectator()||p.isPassenger()||!pos.equals(p.blockPosition().below()))return;
        var s=Hk3EggRuntime.state(p);s.putLong("ownWaterFallStart",p.server.overworld().getGameTime());s.putDouble("ownWaterFallY",p.getY());s.putString("ownWaterFallDim",p.level().dimension().location().toString());s.putFloat("ownWaterFallHealth",p.getHealth());
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        var s=Hk3EggRuntime.state(p);if(!s.contains("ownWaterFallStart"))return;
        long now=p.server.overworld().getGameTime(),elapsed=now-s.getLong("ownWaterFallStart");
        if(elapsed<0||elapsed>200||!s.getString("ownWaterFallDim").equals(p.level().dimension().location().toString())||p.isPassenger()||p.isFallFlying()||p.getAbilities().flying||p.getHealth()<s.getFloat("ownWaterFallHealth")){s.remove("ownWaterFallStart");return;}
        var feet=p.blockPosition();
        if(p.isInWater()&&p.getY()<s.getDouble("ownWaterFallY")-1&&Hk3EggBuildMemory.get(p.serverLevel()).owns(p,feet)&&p.level().getFluidState(feet).isSource()&&p.level().getFluidState(feet).is(FluidTags.WATER)&&p.isAlive()){
            Hk3EggVanilla.caseEvent(p,488);s.remove("ownWaterFallStart");
        }else if(elapsed>2&&p.onGround())s.remove("ownWaterFallStart");
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p)Hk3EggRuntime.state(p).remove("ownWaterFallStart");}
    @SubscribeEvent public static void died(LivingDeathEvent e){if(e.getEntity() instanceof ServerPlayer p)Hk3EggRuntime.state(p).remove("ownWaterFallStart");}
}
