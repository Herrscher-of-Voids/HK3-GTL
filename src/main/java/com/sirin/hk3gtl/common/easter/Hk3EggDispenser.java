package com.sirin.hk3gtl.common.easter;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.*;
import java.util.*;
/** 【变更记录 #1】2026-10-01 13:34:51（修订128）：删除：无；新增/修改：本人装水瓶、实际按相邻按钮、默认发射行为成功生成水瓶实体三步配对；投掷器和瓶子变泥行为不算发射；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggDispenser {
    private static final ThreadLocal<ArrayDeque<BlockSource>> ACTIVE=ThreadLocal.withInitial(ArrayDeque::new);
    private Hk3EggDispenser(){}
    public static void stored(ServerPlayer p,AbstractContainerMenu menu,List<Hk3EggStorageFacts.Stack> before,List<Hk3EggStorageFacts.Stack> after){
        if(!(menu instanceof DispenserMenu)||!menu.stillValid(p))return;
        long old=before.stream().filter(s->s.id().equals("minecraft:potion")&&s.potion().isEmpty()).mapToLong(Hk3EggStorageFacts.Stack::count).sum(),now=after.stream().filter(s->s.id().equals("minecraft:potion")&&s.potion().isEmpty()).mapToLong(Hk3EggStorageFacts.Stack::count).sum();if(now<=old)return;
        for(var slot:menu.slots)if(slot.container instanceof DispenserBlockEntity dispenser&&!(dispenser instanceof DropperBlockEntity)&&slot.getItem().is(Items.POTION)&&PotionUtils.getPotion(slot.getItem())==Potions.WATER){dispenser.getPersistentData().putUUID("hk3EggWaterLoader",p.getUUID());dispenser.setChanged();return;}
    }
    public static void button(ServerPlayer p,BlockPos at){
        for(var direction:Direction.values()){var pos=at.relative(direction);if(!p.level().hasChunkAt(pos))continue;
            if(p.level().getBlockEntity(pos) instanceof DispenserBlockEntity dispenser&&!(dispenser instanceof DropperBlockEntity)&&p.level().hasNeighborSignal(pos)){var n=dispenser.getPersistentData();if(n.hasUUID("hk3EggWaterLoader")&&n.getUUID("hk3EggWaterLoader").equals(p.getUUID())){n.putLong("hk3EggWaterButton",p.server.overworld().getGameTime());dispenser.setChanged();}}
        }
    }
    public static void spawn(BlockSource source,Level level,ItemStack stack,int speed,Direction facing,Position position){var q=ACTIVE.get();q.push(source);try{net.minecraft.core.dispenser.DefaultDispenseItemBehavior.spawnItem(level,stack,speed,facing,position);}finally{q.pop();if(q.isEmpty())ACTIVE.remove();}}
    public static void ejected(net.minecraft.world.entity.Entity entity){
        var q=ACTIVE.get();if(q.isEmpty()){ACTIVE.remove();return;}if(!(entity instanceof net.minecraft.world.entity.item.ItemEntity item)||!item.getItem().is(Items.POTION)||PotionUtils.getPotion(item.getItem())!=Potions.WATER)return;
        var source=q.peek();if(!(source.getEntity() instanceof DispenserBlockEntity dispenser)||dispenser instanceof DropperBlockEntity)return;var n=dispenser.getPersistentData();long now=source.getLevel().getServer().overworld().getGameTime();if(!n.hasUUID("hk3EggWaterLoader")||!n.contains("hk3EggWaterButton")||now-n.getLong("hk3EggWaterButton")<0||now-n.getLong("hk3EggWaterButton")>6)return;
        var p=source.getLevel().getServer().getPlayerList().getPlayer(n.getUUID("hk3EggWaterLoader"));if(p!=null)Hk3EggVanilla.caseEvent(p,403);n.remove("hk3EggWaterButton");n.remove("hk3EggWaterLoader");dispenser.setChanged();
    }
}
