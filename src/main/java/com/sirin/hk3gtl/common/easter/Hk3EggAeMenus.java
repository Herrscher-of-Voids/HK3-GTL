package com.sirin.hk3gtl.common.easter;
import appeng.menu.*;
import appeng.menu.implementations.*;
import appeng.menu.me.items.CraftingTermMenu;
import appeng.menu.me.items.PatternEncodingTermMenu;
import appeng.helpers.WirelessTerminalMenuHost;
import appeng.parts.reporting.CraftingTerminalPart;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
@Mod.EventBusSubscriber(modid="hk3gtl")
 
 
 
 
 
 
public final class Hk3EggAeMenus {
    private record CellView(AbstractContainerMenu menu,net.minecraft.nbt.CompoundTag snapshot){}
    private static final Map<UUID,CellView> CELLS=new java.util.concurrent.ConcurrentHashMap<>();
    private final static Map<UUID,AbstractContainerMenu> PREVIEW=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggAeMenus(){}
    public static void preview(ServerPlayer p){
        if(!(p.containerMenu instanceof PatternEncodingTermMenu menu)||!menu.stillValid(p)||!(menu.getTarget() instanceof appeng.parts.encoding.PatternEncodingTerminalPart))return;
        boolean visible=java.util.stream.Stream.concat(menu.getSlots(SlotSemantics.CRAFTING_RESULT).stream(),menu.getSlots(SlotSemantics.PROCESSING_OUTPUTS).stream()).anyMatch(slot->slot.isActive()&&!slot.getItem().isEmpty());
        if(visible)PREVIEW.put(p.getUUID(),menu);
    }
    public static void encoding(ServerPlayer p){PREVIEW.remove(p.getUUID());}
    public static void cancelled(ServerPlayer p,AbstractContainerMenu menu){if(PREVIEW.remove(p.getUUID())==menu)Hk3EggVanilla.caseEvent(p,201);}

    public static int blanks(AbstractContainerMenu menu){
        if(!(menu instanceof PatternEncodingTermMenu ae))return -1;
        int count=0;for(var slot:ae.getSlots(SlotSemantics.BLANK_PATTERN)){var stack=slot.getItem();if(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString().equals("ae2:blank_pattern"))count+=stack.getCount();}return count;
    }
    public static void clicked(ServerPlayer p,AbstractContainerMenu menu,int before){if(before>=0&&menu.stillValid(p)&&blanks(menu)>before)Hk3EggVanilla.caseEvent(p,191);}
    public static void crafted(ServerPlayer p){if(p.containerMenu instanceof CraftingTermMenu ae&&ae.getTarget() instanceof CraftingTerminalPart)Hk3EggVanilla.caseEvent(p,197);}
    public static long patterns(ServerPlayer p){long count=0;for(var s:p.getInventory().items)if(!s.isEmpty()&&appeng.api.crafting.PatternDetailsHelper.isEncodedPattern(s))count+=s.getCount();var carried=p.containerMenu.getCarried();if(!carried.isEmpty()&&appeng.api.crafting.PatternDetailsHelper.isEncodedPattern(carried))count+=carried.getCount();return count;}
    @SubscribeEvent public static void opened(PlayerContainerEvent.Open e){
        if(!(e.getEntity() instanceof ServerPlayer p))return;CELLS.remove(p.getUUID());PREVIEW.remove(p.getUUID());
        if(e.getContainer() instanceof AEBaseMenu ae&&ae.getTarget() instanceof WirelessTerminalMenuHost wireless&&ae.stillValid(p)&&wireless.rangeCheck()){
            String item=BuiltInRegistries.ITEM.getKey(wireless.getItemStack().getItem()).toString();
            if(item.equals("ae2:wireless_terminal"))Hk3EggVanilla.caseEvent(p,198);
        }
        if(e.getContainer() instanceof CellWorkbenchMenu cell&&cell.getBlockEntity()!=null){
            for(var slot:cell.getSlots(SlotSemantics.STORAGE_CELL)){
                var inventory=appeng.api.storage.StorageCells.getCellInventory(slot.getItem(),null);
                if(inventory!=null&&!inventory.getAvailableStacks().isEmpty()){CELLS.put(p.getUUID(),new CellView(cell,cell.getBlockEntity().saveWithoutMetadata()));break;}
            }
        }
    }
    public static void changed(ServerPlayer p,AbstractContainerMenu menu){
        var view=CELLS.get(p.getUUID());
        if(view!=null&&view.menu()==menu&&menu instanceof CellWorkbenchMenu cell&&cell.getBlockEntity()!=null&&!view.snapshot().equals(cell.getBlockEntity().saveWithoutMetadata()))CELLS.remove(p.getUUID());
    }
    @SubscribeEvent public static void tick(net.minecraftforge.event.TickEvent.PlayerTickEvent e){if(e.phase==net.minecraftforge.event.TickEvent.Phase.END&&e.player instanceof ServerPlayer p)changed(p,p.containerMenu);}
    @SubscribeEvent public static void closed(PlayerContainerEvent.Close e){
        if(!(e.getEntity() instanceof ServerPlayer p))return;cancelled(p,e.getContainer());var state=CELLS.remove(p.getUUID());
        if(state!=null&&state.menu()==e.getContainer()&&e.getContainer() instanceof CellWorkbenchMenu cell&&cell.getBlockEntity()!=null&&state.snapshot().equals(cell.getBlockEntity().saveWithoutMetadata()))Hk3EggVanilla.caseEvent(p,208);
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){CELLS.remove(e.getEntity().getUUID());PREVIEW.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){CELLS.clear();PREVIEW.clear();}
}
