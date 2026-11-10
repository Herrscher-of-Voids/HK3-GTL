package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.core.registries.BuiltInRegistries;
import appeng.menu.AEBaseMenu;
import appeng.blockentity.storage.DriveBlockEntity;
import java.util.*;
/** 【变更记录 #1】2026-10-01 06:03:54（修订128）：删除无；新增ME驱动器真实单元装入、容量卡扩槽、记忆卡保存恢复的配置摘要；修改无；用途：服务器本人有效菜单与成功通知，只读单元识别，不以持有替代安装。 */
/** 【变更记录 #2】2026-10-01 06:31:11（修订128）：删除：无；新增/修改：本人升级卡装入前后数量建立归属；1M流体单元安装身份随实体单元保存，持有不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggAeDevices {
    public record View(List<ItemStack> cells,int slots,List<Integer> cards){}
    private Hk3EggAeDevices(){}
    public static View before(AbstractContainerMenu menu){
        if(menu instanceof AEBaseMenu ae&&ae.getTarget() instanceof DriveBlockEntity drive){var inv=drive.getInternalInventory();var items=new ArrayList<ItemStack>();for(int i=0;i<inv.size();i++)items.add(inv.getStackInSlot(i).copy());return new View(items,-1,List.of());}
        return new View(List.of(),enabled(menu),Hk3EggAeUpgrades.snapshot(menu));
    }
    private static int enabled(AbstractContainerMenu menu){if(!(menu instanceof appeng.menu.implementations.UpgradeableMenu<?> ae))return -1;int count=0;for(int i=0;i<63;i++)if(ae.isSlotEnabled(i))count++;return count;}
    public static void after(ServerPlayer p,AbstractContainerMenu menu,View before){
        if(before==null||!menu.stillValid(p)||p.containerMenu!=menu)return;
        Hk3EggAeUpgrades.installed(p,menu,before.cards);
        if(menu instanceof AEBaseMenu ae&&ae.getTarget() instanceof DriveBlockEntity drive){
            var inv=drive.getInternalInventory();if(inv.size()!=before.cells.size())return;
            for(int i=0;i<inv.size();i++){
                var stack=inv.getStackInSlot(i);if(stack.isEmpty()||ItemStack.matches(stack,before.cells.get(i))||drive.getOriginalCellInventory(i)==null)continue;
                String id=BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
                if(BuiltInRegistries.BLOCK.getKey(drive.getBlockState().getBlock()).toString().equals("ae2:drive"))Hk3EggVanilla.caseEvent(p,196);
                if(id.equals("gtlcore:fluid_storage_cell_1m")){stack.getOrCreateTag().putUUID("hk3EggCellInstaller",p.getUUID());drive.setChanged();}
                if(id.equals("gtlcore:item_storage_cell_1m"))Hk3EggVanilla.caseEvent(p,247);
            }
        }
        if(before.slots>=0&&enabled(menu)>before.slots&&menu instanceof appeng.menu.implementations.UpgradeableMenu<?> ae&&ae.getHost().getUpgrades().getInstalledUpgrades(appeng.core.definitions.AEItems.CAPACITY_CARD)>0)Hk3EggVanilla.caseEvent(p,203);
    }
    public static void memory(ServerPlayer p,appeng.api.implementations.items.MemoryCardMessages message){
        for(var hand:net.minecraft.world.InteractionHand.values()){
            var card=p.getItemInHand(hand);if(!(card.getItem() instanceof appeng.items.tools.MemoryCardItem item))continue;
            String hash=Hk3EggNotes.digest(item.getSettingsName(card)+item.getData(card).toString());var s=Hk3EggRuntime.state(p);
            if(message==appeng.api.implementations.items.MemoryCardMessages.SETTINGS_SAVED)s.putString("aeSavedSettings",hash);
            if(message==appeng.api.implementations.items.MemoryCardMessages.SETTINGS_LOADED&&hash.equals(s.getString("aeSavedSettings")))Hk3EggVanilla.caseEvent(p,202);
        }
    }
}
