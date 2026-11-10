package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerContainerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 12:16:23（修订128）：删除：无；新增/修改：已有护具工作设备交互、本人电池实际充电、复制工具成功复制再粘贴回执；失败消息不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #2】2026-10-01 13:24:37（修订128）：删除：无；新增/修改：只在本人有效电路GUI成功改配置后记录参数，配方生成和后台设置不算玩家修改；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 13:33:12（修订128）：删除：无；新增/修改：高级终端本人有效GUI真实更改设置后标记该物品，随后存入有权限的现有收纳容器才授280，关闭不改值不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggTools {
    private record Terminal(net.minecraft.world.inventory.AbstractContainerMenu menu,ItemStack stack,net.minecraft.nbt.CompoundTag before){}
    private static final java.util.Map<java.util.UUID,Terminal> TERMINALS=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggTools(){}
    @SubscribeEvent public static void closed(PlayerContainerEvent.Close e){if(!(e.getEntity() instanceof ServerPlayer p))return;var view=TERMINALS.remove(p.getUUID());if(view==null||view.menu!=e.getContainer()||view.stack.isEmpty())return;var tag=view.stack.getOrCreateTag();for(String key:java.util.List.of("CoilTier","RepeatCount","NoHatchMode"))if(tag.getInt(key)!=view.before.getInt(key)){tag.putUUID("Hk3EggTerminalOperatedBy",p.getUUID());break;}}
    @SubscribeEvent public static void logout(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent e){TERMINALS.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){TERMINALS.clear();}
    public static void stored(ServerPlayer p,net.minecraft.world.inventory.AbstractContainerMenu menu,java.util.List<Hk3EggStorageFacts.Stack> before,java.util.List<Hk3EggStorageFacts.Stack> after){
        if(!menu.stillValid(p)||!Hk3EggStorageFacts.increased(before,after,"gtmthings:advanced_terminal"))return;
        for(var slot:menu.slots)if(slot.container!=p.getInventory()){var item=slot.getItem();var tag=item.getTag();if(BuiltInRegistries.ITEM.getKey(item.getItem()).toString().equals("gtmthings:advanced_terminal")&&tag!=null&&tag.hasUUID("Hk3EggTerminalOperatedBy")&&tag.getUUID("Hk3EggTerminalOperatedBy").equals(p.getUUID())){Hk3EggVanilla.caseEvent(p,280);return;}}
    }

    public static void circuitChanged(com.lowdragmc.lowdraglib.gui.factory.HeldItemUIFactory.HeldItemHolder holder,int before,int after){
        if(before==after)return;var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(server==null||!server.isSameThread())return;
        for(var p:server.getPlayerList().getPlayers())if(p.containerMenu instanceof com.lowdragmc.lowdraglib.gui.modular.ModularUIContainer ui&&ui.getModularUI().holder==holder&&ui.stillValid(p)&&com.gregtechceu.gtceu.common.item.IntCircuitBehaviour.isIntegratedCircuit(holder.getHeld())){
            Hk3EggProductionData.get(server).produced(p.getUUID(),"context:circuit_"+after,1);return;
        }
    }
    public static void batteryOwner(ServerPlayer p,ItemStack stack){if(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString().equals("gtlcore:extremely_max_battery")&&!p.isCreative()){var n=stack.getOrCreateTag();if(!n.hasUUID("Hk3EggBatteryOwner")||!n.getUUID("Hk3EggBatteryOwner").equals(p.getUUID()))n.putUUID("Hk3EggBatteryOwner",p.getUUID());}}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0)return;for(var stack:p.getInventory().items)batteryOwner(p,stack);batteryOwner(p,p.getOffhandItem());}
    public static void charged(ItemStack stack,long actual,boolean simulate){
        if(simulate||actual<=0||!BuiltInRegistries.ITEM.getKey(stack.getItem()).toString().equals("gtlcore:extremely_max_battery"))return;var n=stack.getTag();if(n==null||!n.hasUUID("Hk3EggBatteryOwner"))return;
        var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(server!=null&&server.isSameThread())Hk3EggProductionData.get(server).produced(n.getUUID("Hk3EggBatteryOwner"),"receipt:249",1);
    }
    @SubscribeEvent public static void menu(PlayerContainerEvent.Open e){
        if(!(e.getEntity() instanceof ServerPlayer p)||!e.getContainer().stillValid(p))return;
        TERMINALS.remove(p.getUUID());
        if(e.getContainer() instanceof com.lowdragmc.lowdraglib.gui.modular.ModularUIContainer settings&&settings.getModularUI().holder instanceof com.lowdragmc.lowdraglib.gui.factory.HeldItemUIFactory.HeldItemHolder held&&BuiltInRegistries.ITEM.getKey(held.getHeld().getItem()).toString().equals("gtmthings:advanced_terminal"))TERMINALS.put(p.getUUID(),new Terminal(e.getContainer(),held.getHeld(),held.getHeld().getOrCreateTag().copy()));
        if(e.getContainer() instanceof com.lowdragmc.lowdraglib.gui.modular.ModularUIContainer ui&&ui.getModularUI().holder instanceof com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine machine&&machine.getRecipeLogic().isWorking()){
            for(var stack:p.getArmorSlots())if(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString().equals("gtceu:rubber_gloves")){Hk3EggVanilla.caseEvent(p,236);break;}
        }
    }
    public static void copyMessage(net.minecraft.world.entity.player.Player actor,net.minecraft.network.chat.Component message,net.minecraft.world.item.context.UseOnContext context){
        if(!(actor instanceof ServerPlayer p)||!(message.getContents() instanceof net.minecraft.network.chat.contents.TranslatableContents contents)||context==null)return;
        String key=contents.getKey();var n=context.getItemInHand().getOrCreateTag();String pos=Hk3EggVanilla.key(p,context.getClickedPos());
        if(key.equals("message.gtlcore.machine_data_copied")){n.putUUID("Hk3EggCopyOwner",p.getUUID());n.putString("Hk3EggCopySource",pos);}
        if(key.equals("message.gtlcore.machine_data_pasted")&&n.hasUUID("Hk3EggCopyOwner")&&n.getUUID("Hk3EggCopyOwner").equals(p.getUUID())&&!n.getString("Hk3EggCopySource").isEmpty()&&!n.getString("Hk3EggCopySource").equals(pos))Hk3EggVanilla.caseEvent(p,242);
    }
}
