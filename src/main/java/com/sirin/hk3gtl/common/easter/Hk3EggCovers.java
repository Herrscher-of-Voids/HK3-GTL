package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.cover.CoverBehavior;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import net.minecraft.server.level.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.item.ItemStack;
import java.util.*;
/** 【变更记录 #1】2026-10-01 06:15:25（修订128）：删除无；新增本人安装无线覆盖板与真实插入/填充结果旁注；修改无；用途：归属按面持久化，旧未归属覆盖板不猜作者，模拟不记录。 */
/** 【变更记录 #2】2026-10-01 06:17:41（修订128）：删除：无；新增/修改：按当前GTCEu公开字段读取覆盖板面与承载方，修复不存在getter导致的编译失败；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 12:33:29（修订128）：删除：无；新增/修改：普通无线流体覆盖板记录接收端确实满容量导致的零传输，恢复实际传输后授278，重装清除旧暂停证据；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 13:24:37（修订128）：删除：无；新增/修改：本人在同一面重绑不同目标后只在真实物品接收成功时授279；未改目标或无接收不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
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
    public static void fluidResult(CoverBehavior c,long actual,boolean full){
        var be=holder(c);if(be==null)return;String field=key(c)+"_full";
        if(actual==0&&full){be.getPersistentData().putBoolean(field,true);be.setChanged();}
        else if(actual>0&&be.getPersistentData().getBoolean(field)){delivered(c,278);be.getPersistentData().remove(field);be.setChanged();}
    }
    public static long itemCount(com.lowdragmc.lowdraglib.side.item.IItemTransfer inv){if(inv.getSlots()>4096)return -1;long n=0;for(int i=0;i<inv.getSlots();i++)n+=inv.getStackInSlot(i).getCount();return n;}
}
