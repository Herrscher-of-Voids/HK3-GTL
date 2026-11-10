package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import net.minecraft.server.level.*;
import net.minecraft.core.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 06:23:20（修订128）：删除无；新增服务端真实事件旁注；修改无；用途：原条件、原世界结果不变，只授个人可选收藏。 */
/** 【变更记录 #2】2026-10-01 06:35:47（修订128）：删除：无；新增/修改：已取得I01顶层收藏即停止结构缓存扫描；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggStructureScenes {
    private Hk3EggStructureScenes(){}
    public static void formed(MultiblockControllerMachine m){
        if(!(m.getLevel() instanceof ServerLevel level)||!m.isFormed()||m.getMultiblockState().hasError()||!(m.getHolder() instanceof BlockEntity be))return;
        var owner=m instanceof com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine h?h.getOwnerUUID():be.getPersistentData().hasUUID(Hk3EggProduction.OWNER)?be.getPersistentData().getUUID(Hk3EggProduction.OWNER):null;
        if(owner==null)return;var p=level.getServer().getPlayerList().getPlayer(owner);if(p==null)return;
        var s=Hk3EggRuntime.state(p);var seen=s.getCompound("formedLocations");
        String key=Hk3EggNotes.digest("industrial:"+level.dimension().location()+":"+m.getPos().asLong()+":"+m.getDefinition().getId());
        if(seen.size()<100)seen.putBoolean(key,true);s.put("formedLocations",seen);if(seen.size()>=100)Hk3EggVanilla.caseEvent(p,67);
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0||!p.onGround()||p.getAbilities().flying||com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-071"))return;
        var feet=p.blockPosition().below();
        for(var s:MultiblockWorldSavedData.getOrCreate(p.serverLevel()).getControllerInChunk(new net.minecraft.world.level.ChunkPos(feet))){
            if(!s.isPosInCache(feet)||s.hasError()||s.cache==null||!p.level().hasChunkAt(s.controllerPos))continue;
            var m=MetaMachine.getMachine(p.level(),s.controllerPos);
            if(!(m instanceof MultiblockControllerMachine controller)||!controller.isFormed()||!m.getDefinition().getId().toString().equals("hk3gtl:i01_honkai_collection_tower"))continue;
            int top=Integer.MIN_VALUE;
            for(long packed:s.cache){var at=BlockPos.of(packed);if(!p.level().hasChunkAt(at)){top=Integer.MAX_VALUE;break;}
                if(p.level().getBlockState(at).isFaceSturdy(p.level(),at,Direction.UP)&&p.level().getBlockState(at.above()).getCollisionShape(p.level(),at.above()).isEmpty()&&p.level().getBlockState(at.above(2)).getCollisionShape(p.level(),at.above(2)).isEmpty())top=Math.max(top,at.getY());}
            if(feet.getY()==top)Hk3EggVanilla.caseEvent(p,71);
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
