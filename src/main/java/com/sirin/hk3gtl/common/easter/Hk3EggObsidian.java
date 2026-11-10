package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.*;
import net.minecraft.core.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.tags.FluidTags;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 13:29:18（修订128）：删除：无；新增/修改：观察源熔岩实际变黑曜石，tick末确认邻接本人放水来源后记录，混合归属不猜，未加载不扫描；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggObsidian {
    private record Candidate(ServerLevel level,BlockPos pos){}
    private static final Map<net.minecraft.server.MinecraftServer,ArrayDeque<Candidate>> PENDING=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggObsidian(){}
    public static void changed(ServerLevel level,BlockPos pos,BlockState before,BlockState after){if(!after.is(Blocks.OBSIDIAN)||!before.getFluidState().is(FluidTags.LAVA)||!before.getFluidState().isSource())return;var queue=PENDING.computeIfAbsent(level.getServer(),k->new ArrayDeque<>());if(queue.size()<4096)queue.add(new Candidate(level,pos.immutable()));}
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;var queue=PENDING.remove(e.getServer());if(queue==null)return;
        for(var candidate:queue){var level=candidate.level;var at=candidate.pos;if(!level.hasChunkAt(at)||!level.getBlockState(at).is(Blocks.OBSIDIAN))continue;var memory=Hk3EggBuildMemory.get(level);var owners=new HashSet<UUID>();
            for(var d:Direction.values()){var water=at.relative(d);if(!level.hasChunkAt(water)||!level.getFluidState(water).is(FluidTags.WATER))continue;var owner=memory.recordedOwner(water,"minecraft:water");if(owner!=null)owners.add(owner);}
            if(owners.size()!=1)continue;var p=e.getServer().getPlayerList().getPlayer(owners.iterator().next());if(p!=null&&p.serverLevel()==level)memory.madeObsidian(p,at,true);
        }
    }
    @SubscribeEvent public static void stop(ServerStoppedEvent e){PENDING.remove(e.getServer());}
}
