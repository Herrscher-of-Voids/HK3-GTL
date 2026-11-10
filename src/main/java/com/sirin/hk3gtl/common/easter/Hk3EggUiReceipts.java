package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.ItemTags;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 12:13:33（修订128）：删除：无；新增/修改：客户端只回报实际显示页，服务端核对已注册物品、真实生产/生存取得与标签成员，不接受任意彩蛋编号；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #2】2026-10-01 12:14:23（修订128）：删除：无；新增/修改：修复标签分隔转义，限流改为每tick16次避免同屏多配方丢回执，删除无用读取；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 12:14:48（修订128）：删除：无；新增/修改：标签分隔使用字符类避免Java字符串与正则双层转义歧义；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 13:26:03（修订128）：删除：无；新增/修改：坐标阅读需本人由维度传送器成功传送后的维度一致凭据；预览回执只交AE现有菜单核验；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggUiReceipts {
    private Hk3EggUiReceipts(){}
    public static void acquired(ServerPlayer p,net.minecraft.world.item.ItemStack item){
        if(p.isCreative()||p.isSpectator()||item.isEmpty())return;String id=BuiltInRegistries.ITEM.getKey(item.getItem()).toString();
        if(id.equals("gtladditions:barnarda_data")||id.equals("gtladditions:create_data"))Hk3EggRuntime.state(p).putBoolean("acquired_"+id,true);
    }
    @SubscribeEvent public static void picked(PlayerEvent.ItemPickupEvent e){if(e.getEntity() instanceof ServerPlayer p)acquired(p,e.getStack());}
    @SubscribeEvent public static void crafted(PlayerEvent.ItemCraftedEvent e){if(e.getEntity() instanceof ServerPlayer p)acquired(p,e.getCrafting());}
    public static void input(ServerPlayer p,String action,String value){
        var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();if(s.getLong("uiReceiptTick")!=now){s.putLong("uiReceiptTick",now);s.putInt("uiReceiptCount",0);}int count=s.getInt("uiReceiptCount");if(count>=16)return;s.putInt("uiReceiptCount",count+1);
        if(action.equals("egg_ae_preview")){Hk3EggAeMenus.preview(p);
        }else if(action.equals("egg_coordinates")){if(s.contains("dimensionalTeleported")&&s.getString("dimensionalTeleportedDim").equals(p.level().dimension().location().toString())&&now>=s.getLong("dimensionalTeleported")){Hk3EggVanilla.caseEvent(p,263);s.remove("dimensionalTeleported");}
        }else if(action.equals("egg_tooltip")){
            if(!Set.of("gtladditions:barnarda_data","gtladditions:create_data").contains(value)||!s.getBoolean("acquired_"+value)||Hk3EggVanilla.count(p,value)<1||p.isCreative())return;
            Hk3EggVanilla.caseEvent(p,value.endsWith("barnarda_data")?251:254);
        }else if(action.equals("egg_guide")){
            if(value.startsWith("gtladditions:")&&(BuiltInRegistries.ITEM.getKey(p.getMainHandItem().getItem()).toString().equals("gtladditions:guide")||BuiltInRegistries.ITEM.getKey(p.getOffhandItem().getItem()).toString().equals("gtladditions:guide")))Hk3EggVanilla.caseEvent(p,257);
        }else if(action.equals("egg_recipe")){
            var id=ResourceLocation.tryParse(value);if(id==null||!net.minecraftforge.fml.ModList.get().isLoaded(id.getNamespace()))return;
            var mods=s.getCompound("jeiRecipeMods");if(mods.size()<5)mods.putBoolean(id.getNamespace(),true);s.put("jeiRecipeMods",mods);if(mods.size()>=5)Hk3EggVanilla.caseEvent(p,470);
        }else if(action.equals("egg_transistor")){
            if(value.equals("gtceu:advanced_smd_transistor")&&Hk3EggProductionData.get(p.server).counts(p.getUUID()).getOrDefault(value,0L)>0)Hk3EggVanilla.caseEvent(p,218);
        }else if(action.equals("egg_tag")){
            String[] parts=value.split("[|]",-1);if(parts.length!=2)return;var tag=ResourceLocation.tryParse(parts[0]);var id=ResourceLocation.tryParse(parts[1]);if(tag==null||id==null||!BuiltInRegistries.ITEM.containsKey(id))return;
            var item=BuiltInRegistries.ITEM.get(id);if(!item.getDefaultInstance().is(ItemTags.create(tag)))return;
            if(!s.getString("jeiTagPage").equals(parts[0])){s.putString("jeiTagPage",parts[0]);s.remove("jeiTagMods");}
            var mods=s.getCompound("jeiTagMods");if(mods.size()<3)mods.putBoolean(id.getNamespace(),true);s.put("jeiTagMods",mods);if(mods.size()>=3)Hk3EggVanilla.caseEvent(p,469);
        }else if(action.equals("egg_tag_clear")){s.remove("jeiTagPage");s.remove("jeiTagMods");}
    }
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e){if(e.getEntity() instanceof ServerPlayer p){var s=Hk3EggRuntime.state(p);s.remove("jeiRecipeMods");s.remove("jeiTagPage");s.remove("jeiTagMods");}}
}
