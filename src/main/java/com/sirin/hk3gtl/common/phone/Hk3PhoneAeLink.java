package com.sirin.hk3gtl.common.phone;
import appeng.items.tools.powered.WirelessTerminalItem;
import appeng.helpers.WirelessTerminalMenuHost;
import appeng.menu.locator.MenuLocator;
import appeng.menu.locator.MenuLocators;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import java.lang.reflect.Method;
import java.util.*;
/**
 * 【变更记录 #1】2026-09-30 19:17:36（内测5修订115）
 * 删除：无；新增：背包实体终端选择与AE2WTLib可选原生接口适配。
 * 修改：不用普通终端菜单代替万能终端；用途：保留实际物品的合成/编码页、量子连接和原生权限。
 * 边界：反射只调用已核对的固定公开接口，依赖缺失时不加载；适配失败不降级开错误菜单。
 */
/** 【变更记录 #2】2026-10-01 04:43:52（修订128）：删除：旧固定上限或被替代的分支；新增/修改：原生无线终端返回打开成功后检测真实物品及合成菜单类型，不用普通终端替代；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3PhoneAeLink {
    private Hk3PhoneAeLink(){}
    private static final org.slf4j.Logger LOG=com.mojang.logging.LogUtils.getLogger();
    private static boolean warned;
    private static final class Universal {
        static final Class<?> TYPE;
        static final Method OPEN,HOST;
        static {
            Class<?> type=null;Method open=null,host=null;
            if(net.minecraftforge.fml.ModList.get().isLoaded("ae2wtlib"))try{
                type=Class.forName("de.mari_023.ae2wtlib.terminal.IUniversalWirelessTerminalItem");
                open=type.getMethod("tryOpen",Player.class,MenuLocator.class,ItemStack.class,boolean.class);
                host=type.getMethod("getMenuHost",Player.class,MenuLocator.class,ItemStack.class);
            }catch(ReflectiveOperationException|LinkageError e){warn(e);}
            TYPE=type;OPEN=open;HOST=host;
        }
        static boolean applies(ItemStack stack){return TYPE!=null&&TYPE.isInstance(stack.getItem());}
    }
    private static void warn(Throwable error){if(!warned){warned=true;LOG.warn("手机无法使用无线终端原生接口，已阻止普通菜单降级",error);}}
    private static boolean compatible(ItemStack stack){
        return stack.getItem() instanceof WirelessTerminalItem;
    }
    public static boolean available(ServerPlayer p,int slot){
        if(slot<0||slot>=p.getInventory().getContainerSize())return false;
        var stack=p.getInventory().getItem(slot);
        if(!(stack.getItem() instanceof WirelessTerminalItem terminal)||!terminal.hasPower(p,.5,stack))return false;
        if(net.minecraftforge.fml.ModList.get().isLoaded("ae2wtlib")&&Universal.TYPE==null)return false;
        try{
            var grid=terminal.getLinkedGrid(stack,p.level(),p);
            if(grid==null||!grid.getEnergyService().isNetworkPowered())return false;
            // 使用真实终端的宿主，保留万能终端的量子/无限范围升级判定。
            Object host=Universal.applies(stack)?
                (Universal.HOST==null?null:Universal.HOST.invoke(stack.getItem(),p,MenuLocators.forInventorySlot(slot),stack)):
                terminal.getMenuHost(p,slot,stack,null);
            return host instanceof WirelessTerminalMenuHost wireless&&wireless.rangeCheck();
        }catch(ReflectiveOperationException|RuntimeException|LinkageError e){warn(e);return false;}
    }
    public static boolean connected(ServerPlayer p){
        for(int slot=0;slot<p.getInventory().getContainerSize();slot++)if(available(p,slot))return true;return false;
    }
    public static int choose(ServerPlayer p){
        var slots=new ArrayList<Integer>();
        for(int slot=0;slot<p.getInventory().getContainerSize();slot++)if(compatible(p.getInventory().getItem(slot)))slots.add(slot);
        if(slots.size()==1)return open(p,slots.get(0));
        if(slots.isEmpty()){p.sendSystemMessage(Component.literal("背包中没有AE无线终端。请携带并绑定你要使用的终端。"));return 0;}
        var view=new CompoundTag();view.putString("Mode","ae_terminals");var rows=new ListTag();
        for(int slot:slots){var row=new CompoundTag();row.putInt("Slot",slot);row.putString("Title",p.getInventory().getItem(slot).getHoverName().getString());row.putBoolean("Available",available(p,slot));rows.add(row);}
        view.put("Rows",rows);Hk3PhoneService.send(p,view);return 1;
    }
    public static int open(ServerPlayer p,int slot){
        if(!available(p,slot)){p.sendSystemMessage(Component.literal("这部终端暂不可连接：请检查绑定、电量、网络供电与它自身支持的连接范围。"));return 0;}
        var stack=p.getInventory().getItem(slot);boolean opened;
        try{
            if(Universal.applies(stack)){
                if(Universal.OPEN==null)throw new IllegalStateException("万能终端接口不可用");
                opened=Boolean.TRUE.equals(Universal.OPEN.invoke(stack.getItem(),p,MenuLocators.forInventorySlot(slot),stack,false));
            }else opened=((WirelessTerminalItem)stack.getItem()).openFromInventory(p,slot);
        }catch(ReflectiveOperationException|RuntimeException|LinkageError e){
            warn(e);p.sendSystemMessage(Component.literal("这部终端的原生界面打开失败，未替换为普通终端。"));return 0;
        }
        if(opened){
            Hk3PhoneAppHints.opened(p,"ae");
            String id=net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
            if(id.equals("ae2:wireless_terminal"))com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,198);
            if(id.equals("ae2:wireless_crafting_terminal")&&p.containerMenu instanceof appeng.menu.me.items.CraftingTermMenu)com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,199);
        }
        return opened?1:0;
    }
}
