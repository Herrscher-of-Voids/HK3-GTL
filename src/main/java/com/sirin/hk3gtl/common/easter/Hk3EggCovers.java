package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.cover.CoverBehavior;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import net.minecraft.server.level.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.item.ItemStack;
import java.util.*;
public final class Hk3EggCovers {
    private Hk3EggCovers(){}
    private static String key(CoverBehavior c){return "hk3_egg_cover_"+c.attachedSide.getName();}
    private static BlockEntity holder(CoverBehavior c){var h=c.coverHolder;if(h.getLevel()==null||h.getLevel().isClientSide)return null;return h.getLevel().getBlockEntity(h.getPos());}
    public static void attached(CoverBehavior c,ServerPlayer p){var be=holder(c);if(be==null)return;be.getPersistentData().putUUID(key(c),p.getUUID());be.getPersistentData().remove(key(c)+"_full");be.setChanged();}
    public static void target(CoverBehavior c,ServerPlayer p,net.minecraft.world.item.ItemStack item){
        var be=holder(c);var tag=item.getTag();if(be==null||tag==null||!net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(item.getItem()).toString().equals("gtmthings:advanced_wireless_item_transfer_cover"))return;
        String dim=tag.getString("dimensionid"),face=tag.getString("facing");if(net.minecraft.resources.ResourceLocation.tryParse(dim)==null||net.minecraft.core.Direction.byName(face)==null)return;
        String target=dim+":"+tag.getInt("x")+":"+tag.getInt("y")+":"+tag.getInt("z")+":"+face,field=key(c)+"_target";var n=be.getPersistentData();
        boolean sameOwner=n.hasUUID(field+"_by")&&n.getUUID(field+"_by").equals(p.getUUID());n.putBoolean(field+"_changed",sameOwner&&n.contains(field)&&!target.equals(n.getString(field)));n.putString(field,target);n.putUUID(field+"_by",p.getUUID());be.setChanged();
    }
    public static void targetDelivered(CoverBehavior c){var be=holder(c);if(be!=null&&be.getPersistentData().getBoolean(key(c)+"_target_changed")){delivered(c,279);be.getPersistentData().remove(key(c)+"_target_changed");be.setChanged();}}
    public static void delivered(CoverBehavior c,int id){
        var be=holder(c);if(be==null||!(be.getLevel() instanceof ServerLevel level)||!be.getPersistentData().hasUUID(key(c)))return;
        Hk3EggProductionData.get(level.getServer()).produced(be.getPersistentData().getUUID(key(c)),"receipt:"+id,1);
    }
    public static void whitelistRejected(CoverBehavior cover){
        var block=holder(cover);
        if(block==null||!(block.getLevel() instanceof ServerLevel level)||!block.getPersistentData().hasUUID(key(cover)))return;
        var owner=block.getPersistentData().getUUID(key(cover));var data=Hk3EggProductionData.get(level.getServer());
        if(data.count(owner,"receipt:277")==0)data.produced(owner,"receipt:277",1);
    }
    public static void fluidResult(CoverBehavior c,long actual,boolean full){
        var be=holder(c);if(be==null)return;String field=key(c)+"_full";
        if(actual==0&&full){be.getPersistentData().putBoolean(field,true);be.setChanged();}
        else if(actual>0&&be.getPersistentData().getBoolean(field)){delivered(c,278);be.getPersistentData().remove(field);be.setChanged();}
    }
    public static long itemCount(com.lowdragmc.lowdraglib.side.item.IItemTransfer inv){if(inv.getSlots()>4096)return -1;long n=0;for(int i=0;i<inv.getSlots();i++)n+=inv.getStackInSlot(i).getCount();return n;}
}
