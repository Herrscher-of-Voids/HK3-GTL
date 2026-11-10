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
/** 【变更记录 #1】2026-10-01 06:25:16（修订128）：删除无；新增真实阅读与操作记录；修改无；用途：服务器核对原始条件，失败或模拟不授予。 */
public final class Hk3EggLectern {
    private static final class View {LecternMenu menu;String book;BitSet read=new BitSet();int page=-1,ticks;long last;}
    private static final Map<UUID,View> VIEWS=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggLectern(){}
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
    @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){VIEWS.clear();}
}
