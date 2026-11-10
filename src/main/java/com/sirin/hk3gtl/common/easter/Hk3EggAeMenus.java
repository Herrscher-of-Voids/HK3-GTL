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
/** 【变更记录 #1】2026-10-01 05:24:14（修订128）：删除无；新增有内容单元查看前后存储快照、空白样板真实存入、无线终端原生打开；修改无；用途：原条件的只读观察，不改物品与权限。 */
/** 【变更记录 #2】2026-10-01 05:24:46（修订128）：删除：旧固定上限或被替代的分支；新增/修改：按AE当前源码导入样板编码终端菜单；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 05:25:27（修订128）：删除：旧固定上限或被替代的分支；新增/修改：无线终端必须核对审核指定物品ID和有效网络范围，不把任何无线菜单当普通终端；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 05:33:55（修订128）：删除：旧固定上限或被替代的分支；新增/修改：199明确只允许手机入口，不从普通无线菜单触发；262继续核对实际超级终端菜单提供方；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #5】2026-10-01 06:19:47（修订128）：删除：无；新增/修改：单元工作台每次点击和服务端tick检查过程状态，曾修改后恢复仍不算只读；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 13:26:03（修订128）：删除：无；新增/修改：实际渲染的AE样板终端输出预览与本人清空或关闭串联；点击编码即清除取消证据；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
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
