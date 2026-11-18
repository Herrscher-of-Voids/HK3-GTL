package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.LecternMenu;
import net.minecraft.world.item.Items;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
@Mod.EventBusSubscriber(modid="hk3gtl")

public final class Hk3EggLectern {
    private static final class View {LecternMenu menu;String book;BitSet read=new BitSet();int page=-1,ticks;long last;}
    private static final Map<UUID,View> VIEWS=new java.util.concurrent.ConcurrentHashMap<>();
    private record Placement(net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock event,
                             ServerPlayer player,net.minecraft.core.BlockPos pos,net.minecraft.world.item.ItemStack book){}
    private static final List<Placement> PLACEMENTS=new ArrayList<>();
    private Hk3EggLectern(){}
    @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
    public static void placed(net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock e){
        if(e.isCanceled()||!(e.getEntity() instanceof ServerPlayer p)||!e.getItemStack().is(Items.WRITTEN_BOOK))return;
        var state=p.level().getBlockState(e.getPos());
        if(state.is(net.minecraft.world.level.block.Blocks.LECTERN)&&!state.getValue(net.minecraft.world.level.block.LecternBlock.HAS_BOOK))
            PLACEMENTS.add(new Placement(e,p,e.getPos().immutable(),e.getItemStack().copy()));
    }
    @SubscribeEvent public static void placements(TickEvent.ServerTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;
        var it=PLACEMENTS.iterator();
        while(it.hasNext()){
            var placed=it.next();var p=placed.player();if(p.server!=e.getServer())continue;it.remove();
            if(!placed.event().isCanceled()&&p.level()==placed.event().getLevel()&&p.level().hasChunkAt(placed.pos())
                    &&p.level().getBlockEntity(placed.pos()) instanceof net.minecraft.world.level.block.entity.LecternBlockEntity lectern
                    &&net.minecraft.world.item.ItemStack.isSameItemSameTags(lectern.getBook(),placed.book()))
                Hk3EggFacilityScenes.book(p,placed.pos());
        }
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        if(!(p.containerMenu instanceof LecternMenu menu)||!menu.stillValid(p)||!menu.getBook().is(Items.WRITTEN_BOOK)){VIEWS.remove(p.getUUID());return;}
        var book=menu.getBook();var tag=book.getTag();if(tag==null)return;int pages=tag.getList("pages",8).size();if(pages<1||pages>100)return;
        String hash=Hk3EggNotes.digest(tag.toString());var view=VIEWS.computeIfAbsent(p.getUUID(),key->new View());long now=p.server.overworld().getGameTime();
        if(view.menu!=menu||!hash.equals(view.book)||view.last!=now-1){view.menu=menu;view.book=hash;view.read.clear();view.ticks=0;view.page=-1;}
        int page=menu.getPage();if(view.page!=page){view.page=page;view.ticks=0;}view.last=now;
        if(page>=0&&page<pages&&++view.ticks>=10)view.read.set(page);
        if(view.read.cardinality()==pages){var date=Hk3EggCalendar.now();if(date.getMonthValue()==4&&date.getDayOfMonth()==23)Hk3EggVanilla.caseEvent(p,350);}
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){VIEWS.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){VIEWS.clear();PLACEMENTS.removeIf(v->v.player().server==e.getServer());}
}
