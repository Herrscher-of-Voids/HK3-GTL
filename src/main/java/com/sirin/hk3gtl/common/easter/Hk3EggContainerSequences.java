package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.*;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.core.*;
import net.minecraftforge.event.entity.player.PlayerContainerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** 【变更记录 #1】2026-10-01 05:36:00（修订128）：删除无；新增本人箱子访问时间与同次实际存取后序列；修改无；用途：服务端保存放置归属，未有历史时不猜30天，库存改变不当生产证明。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #2】2026-10-01 05:53:29（修订128）：删除：无；新增/修改：30日自有箱子支持双箱；两半须都有本人归属与足够未访问时间，不能用新拼接半箱冒充历史；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggContainerSequences {
    private static final String OWNER="hk3gtl_egg_chest_owner",VISIT="hk3gtl_egg_chest_visit",STALE="hk3gtl_egg_chest_stale";
    private Hk3EggContainerSequences(){}
    public static void placed(ServerPlayer p,BlockPos pos){
        if(p.level().getBlockEntity(pos) instanceof ChestBlockEntity chest){var n=chest.getPersistentData();n.putUUID(OWNER,p.getUUID());n.putLong(VISIT,p.server.overworld().getGameTime());n.remove(STALE);chest.setChanged();}
    }
    @SubscribeEvent public static void opened(PlayerContainerEvent.Open e){
        if(!(e.getEntity() instanceof ServerPlayer p)||!(e.getContainer() instanceof ChestMenu menu))return;
        var parts=Hk3EggChests.parts(p,menu.getContainer());if(parts.isEmpty())return;long now=p.server.overworld().getGameTime();
        boolean own=parts.stream().allMatch(c->c.getPersistentData().hasUUID(OWNER)&&p.getUUID().equals(c.getPersistentData().getUUID(OWNER)));
        boolean stale=own&&parts.stream().allMatch(c->{var n=c.getPersistentData();return n.contains(VISIT)&&now>=n.getLong(VISIT)&&now-n.getLong(VISIT)>=30L*24000L;});
        for(var chest:parts){var n=chest.getPersistentData();if(stale)n.putUUID(STALE,p.getUUID());else n.remove(STALE);if(own)n.putLong(VISIT,now);chest.setChanged();}
    }
    public static void changed(ServerPlayer p,AbstractContainerMenu menu,List<Hk3EggStorageFacts.Stack> before,List<Hk3EggStorageFacts.Stack> after){
        var produced=Hk3EggProductionData.get(p.server);var receipts=produced.counts(p.getUUID());
        if(Hk3EggStorageFacts.increased(before,after,"gtceu:advanced_smd_capacitor")&&receipts.getOrDefault("gtceu:advanced_smd_capacitor",0L)>0&&before.stream().anyMatch(v->!v.empty())&&before.stream().filter(v->!v.empty()).allMatch(v->v.id().endsWith("capacitor")))Hk3EggVanilla.caseEvent(p,217);
        if(Hk3EggStorageFacts.count(after,"gtceu:resin_printed_circuit_board")<Hk3EggStorageFacts.count(before,"gtceu:resin_printed_circuit_board"))produced.produced(p.getUUID(),"context:240",1);
        if(!(menu instanceof ChestMenu chestMenu))return;
        var parts=Hk3EggChests.parts(p,chestMenu.getContainer());if(parts.isEmpty())return;
        for(var chest:parts){var n=chest.getPersistentData();var pos=chest.getBlockPos();
        if(n.hasUUID(STALE)&&p.getUUID().equals(n.getUUID(STALE))&&before.stream().filter(v->!v.empty()).anyMatch(v->Hk3EggStorageFacts.count(after,v.id())<Hk3EggStorageFacts.count(before,v.id()))){Hk3EggVanilla.caseEvent(p,465);n.remove(STALE);chest.setChanged();}
        long old=before.stream().filter(v->v.id().equals("minecraft:paper")&&v.name().equals("079")).mapToLong(Hk3EggStorageFacts.Stack::count).sum();
        long current=after.stream().filter(v->v.id().equals("minecraft:paper")&&v.name().equals("079")).mapToLong(Hk3EggStorageFacts.Stack::count).sum();
        if(current>old)for(var dir:Direction.Plane.HORIZONTAL){var at=pos.relative(dir);if(p.level().hasChunkAt(at)&&p.level().getBlockState(at).is(Blocks.CRAFTING_TABLE)){Hk3EggRuntime.state(p).putBoolean("079StoredAtWorkbench",true);break;}}
        }
    }
}
