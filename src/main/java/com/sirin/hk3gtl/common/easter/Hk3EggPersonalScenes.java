package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.*;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 06:19:47（修订128）：删除无；新增真实操作及连续状态旁注；修改无；用途：只读已加载世界与本人回执，不改游戏结果、不授研究资格。 */
/** 【变更记录 #2】2026-10-01 06:35:47（修订128）：删除：无；新增/修改：展示盔甲按四个实际操作部位记录本人，拆下清除归属，不只判断最后一件操作者；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 16:30:04（修订134）：删除SCP5000只在保存瞬间且8格内检查的单向限制；新增穿齐盔甲后回查本人已存笔记、完成盔甲架定位回执；修改两种操作顺序都重检真实四件及归属；用途：不把他人盔甲或客户端文字当作本人条件。 */
public final class Hk3EggPersonalScenes {
    private Hk3EggPersonalScenes(){}
    public static void note(ServerPlayer p,String title,String body){
        var s=Hk3EggRuntime.state(p);
        if(!body.isBlank()&&s.getBoolean("namedWeaponAcquired")){Hk3EggVanilla.caseEvent(p,473);s.remove("namedWeaponAcquired");}
        if(Hk3EggScpFacts.whyNote(title,body)){
            if(s.hasUUID("scp5000Stand"))for(var level:p.server.getAllLevels()){
                var entity=level.getEntity(s.getUUID("scp5000Stand"));
                if(entity instanceof ArmorStand stand&&completeArmor(p,stand)){Hk3EggVanilla.caseEvent(p,411);return;}
            }
            for(var stand:p.level().getEntitiesOfClass(ArmorStand.class,p.getBoundingBox().inflate(8),a->a.isAlive())){
                if(completeArmor(p,stand)){Hk3EggVanilla.caseEvent(p,411);break;}
            }
        }
    }
    public static void openedNote(ServerPlayer p,String body){
        if(!body.contains("106"))return;var memory=Hk3EggBuildMemory.get(p.serverLevel());
        for(var at:memory.near(p,p.blockPosition(),8))if(p.level().getBlockState(at).is(Blocks.OXIDIZED_COPPER))for(var direction:net.minecraft.core.Direction.Plane.HORIZONTAL){
            var wall=at.relative(direction);if(!p.level().hasChunkAt(wall))continue;var b=p.level().getBlockState(wall);
            if(b.is(Blocks.DEEPSLATE)||b.is(Blocks.COBBLED_DEEPSLATE)||b.is(Blocks.DEEPSLATE_BRICKS)||b.is(Blocks.DEEPSLATE_TILES)){Hk3EggVanilla.caseEvent(p,396);return;}
        }
    }
    public static void acquired(ServerPlayer p,ItemStack stack){if(stack.hasCustomHoverName()&&(stack.getItem() instanceof SwordItem||stack.getItem() instanceof AxeItem||stack.getItem() instanceof BowItem||stack.getItem() instanceof CrossbowItem||stack.is(Items.TRIDENT)))Hk3EggRuntime.state(p).putBoolean("namedWeaponAcquired",true);}
    @SubscribeEvent public static void pickup(PlayerEvent.ItemPickupEvent e){if(e.getEntity() instanceof ServerPlayer p)acquired(p,e.getStack());}
    @SubscribeEvent public static void crafted(PlayerEvent.ItemCraftedEvent e){if(e.getEntity() instanceof ServerPlayer p)acquired(p,e.getCrafting());}
    private static boolean completeArmor(ServerPlayer p,ArmorStand stand){
        if(!stand.isAlive())return false;
        var slots=new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET};
        boolean[] present=new boolean[4];for(int i=0;i<4;i++)present[i]=stand.getItemBySlot(slots[i]).getItem() instanceof ArmorItem;
        return Hk3EggScpFacts.ownsArmor(stand.getPersistentData(),p.getUUID(),present);
    }
    public static void armored(ServerPlayer p,ArmorStand stand,EquipmentSlot slot){
        if(stand.getItemBySlot(slot).isEmpty())stand.getPersistentData().remove("hk3_egg_armorer_"+slot.getName());
        else stand.getPersistentData().putUUID("hk3_egg_armorer_"+slot.getName(),p.getUUID());
        if(completeArmor(p,stand)){
            Hk3EggRuntime.state(p).putUUID("scp5000Stand",stand.getUUID());
            if(Hk3EggScpFacts.hasWhyNote(com.sirin.hk3gtl.common.phone.Hk3PhoneNotes.get(p).list(p.getUUID())))Hk3EggVanilla.caseEvent(p,411);
        }
    }
    public static void farming(ServerPlayer p,String part){
        var s=Hk3EggRuntime.state(p);long day=Math.floorDiv(p.server.overworld().getDayTime(),24000);
        if(!s.contains("farmDay")||s.getLong("farmDay")!=day){s.putLong("farmDay",day);s.putInt("farmActions",0);}
        int bit=switch(part){case "water"->1;case "harvest"->2;case "feed"->4;default->0;};int done=s.getInt("farmActions")|bit;s.putInt("farmActions",done);if(done==7)Hk3EggVanilla.caseEvent(p,486);
    }
    @SubscribeEvent public static void death(LivingDeathEvent e){if(e.getEntity() instanceof ServerPlayer p)reset(p);}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p)reset(p);}
    private static void reset(ServerPlayer p){var s=Hk3EggRuntime.state(p);for(var k:new String[]{"teleportWalk","teleportWalkDim","personalTick"})s.remove(k);}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();
        var previous=new net.minecraft.world.phys.Vec3(s.getDouble("personalX"),s.getDouble("personalY"),s.getDouble("personalZ"));var delta=p.position().subtract(previous);
        if(s.contains("teleportWalk")){
            if(s.getLong("personalTick")!=now-1||!s.getString("teleportWalkDim").equals(p.level().dimension().location().toString())||delta.lengthSqr()>2.25||p.getAbilities().flying||p.isPassenger())s.remove("teleportWalk");
            else if(p.onGround()){double distance=s.getDouble("teleportWalk")+Math.sqrt(delta.x*delta.x+delta.z*delta.z);if(distance>15)s.remove("teleportWalk");else s.putDouble("teleportWalk",distance);}
        }
        s.putDouble("personalX",p.getX());s.putDouble("personalY",p.getY());s.putDouble("personalZ",p.getZ());s.putLong("personalTick",now);
    }
    public static void teleported(ServerPlayer p){var s=Hk3EggRuntime.state(p);s.putDouble("teleportWalk",0);s.putString("teleportWalkDim",p.level().dimension().location().toString());s.putDouble("personalX",p.getX());s.putDouble("personalY",p.getY());s.putDouble("personalZ",p.getZ());s.putLong("personalTick",p.server.overworld().getGameTime());}
    public static void civilization(ServerPlayer p){var s=Hk3EggRuntime.state(p);if(s.contains("teleportWalk")&&s.getDouble("teleportWalk")>=14&&s.getDouble("teleportWalk")<=15)Hk3EggVanilla.caseEvent(p,294);}
}
