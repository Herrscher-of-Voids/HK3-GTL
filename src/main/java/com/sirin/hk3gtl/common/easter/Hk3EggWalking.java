package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.*;
import net.minecraft.world.item.BlockItem;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
/** 【变更记录 #1】2026-10-01 05:02:11（修订128）：删除无；新增雪地步行、雨中树叶遮蔽及沙漠穿行状态；用途：服务端逐tick位移，换维度/断线/飞行/乘骑不计，不累计瞬移距离。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggWalking {
    private Hk3EggWalking(){}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();String dim=p.level().dimension().location().toString();
        var previous=new Vec3(s.getDouble("walkX"),s.getDouble("walkY"),s.getDouble("walkZ"));var delta=p.position().subtract(previous);
        boolean continuous=s.getLong("walkTick")==now-1&&s.getString("walkDimension").equals(dim)&&delta.lengthSqr()<2.25;
        boolean ground=p.onGround()&&!p.getAbilities().flying&&!p.isPassenger()&&!p.isSwimming()&&!p.isFallFlying();
        double step=continuous&&ground?Math.sqrt(delta.x*delta.x+delta.z*delta.z):0;
        var feet=p.level().getBlockState(p.blockPosition());var under=p.level().getBlockState(p.blockPosition().below());
        boolean snow=feet.is(Blocks.SNOW)||under.is(Blocks.SNOW_BLOCK)||under.is(Blocks.POWDER_SNOW);
        double snowWalk=continuous&&ground&&snow?s.getDouble("snowWalk")+step:0;s.putDouble("snowWalk",Math.min(28,snowWalk));if(snowWalk>=28)Hk3EggVanilla.caseEvent(p,308);
        boolean leaves=p.getMainHandItem().getItem() instanceof BlockItem item&&item.getBlock().defaultBlockState().is(BlockTags.LEAVES);
        if(!continuous||!ground||!p.level().isRaining())s.remove("rainLeafWalk");
        else if(p.level().isRainingAt(p.blockPosition())&&leaves)s.putDouble("rainLeafWalk",Math.min(10,s.getDouble("rainLeafWalk")+step));
        else if(s.getDouble("rainLeafWalk")>=10&&!p.level().canSeeSky(p.blockPosition().above())){Hk3EggVanilla.caseEvent(p,426);s.remove("rainLeafWalk");}
        else if(!leaves)s.remove("rainLeafWalk");
        String biome=p.level().getBiome(p.blockPosition()).unwrapKey().map(k->k.location().toString()).orElse("");
        long day=Math.floorDiv(p.level().getDayTime(),24000);boolean daylight=p.level().isDay();
        if(!continuous||!ground||!daylight||s.getLong("desertDay")!=day)s.remove("desertWalk");
        if(daylight&&ground&&biome.equals("minecraft:desert")){s.putLong("desertDay",day);s.putDouble("desertWalk",s.getDouble("desertWalk")+step);}
        else if(continuous&&ground&&daylight&&s.getDouble("desertWalk")>0&&!biome.isEmpty()){Hk3EggVanilla.caseEvent(p,430);s.remove("desertWalk");}
        s.putDouble("walkX",p.getX());s.putDouble("walkY",p.getY());s.putDouble("walkZ",p.getZ());s.putLong("walkTick",now);s.putString("walkDimension",dim);
    }
}
