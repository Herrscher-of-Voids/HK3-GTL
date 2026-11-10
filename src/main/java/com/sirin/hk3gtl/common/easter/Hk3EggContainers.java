package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.Container;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:12:10（修订128）：删除无；新增原生箱/漏斗/投掷器/潜影盒点击完成观察；修改无；用途：服务器菜单权限成立后只读快照，无跨区块扫描，无自动化增量冒充本人操作。 */
/** 【变更记录 #2】2026-10-01 04:30:25（修订128）：删除：旧固定上限或被替代的分支；新增/修改：携带实际操作槽位凭据，纯读/无关存取不解锁他人布局；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 04:41:04（修订128）：删除：旧固定上限或被替代的分支；新增/修改：关闭时重新读取实际容器内容，自动化或其他人已改变最后快照时不发关闭彩蛋；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 04:51:18（修订128）：删除：旧固定上限或被替代的分支；新增/修改：实际存入后记录隔离箱、床边蘑菇煲与命名药箱；仅同一权限容器；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #5】2026-10-01 05:36:00（修订128）：删除：旧固定上限或被替代的分支；新增/修改：把真实容器存取回执转交工业前置与自有箱子30天状态，不从仓库库存当生产；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 05:59:33（修订128）：删除：无；新增/修改：现有成功交互串联本人装饰、存取与自然场景检测；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 06:39:10（修订128）：删除：无；新增/修改：343桌椅蛋糕场景只接本人命名纸实际存入现有权限箱子的成功回执；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 13:33:12（修订128）：删除：无；新增/修改：高级终端有效操作后存回容器使用本人真实点击前后数量及物品凭据，不接受纯打开；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #9】2026-10-01 13:34:51（修订128）：删除：无；新增/修改：本人菜单真正增加水瓶后记录发射器装载归属；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggContainers {
    private Hk3EggContainers(){}
    public static List<Hk3EggStorageFacts.Stack> snapshot(AbstractContainerMenu menu,ServerPlayer p){
        if(!(menu instanceof ChestMenu||menu instanceof HopperMenu||menu instanceof DispenserMenu||menu instanceof ShulkerBoxMenu)||!menu.stillValid(p))return List.of();
        var slots=new ArrayList<Hk3EggStorageFacts.Stack>();
        for(var slot:menu.slots)if(slot.container!=p.getInventory()){
            var s=slot.getItem();String potion=s.getItem() instanceof PotionItem?BuiltInRegistries.POTION.getKey(PotionUtils.getPotion(s)).toString():"";
            if(potion.endsWith(":empty")||potion.endsWith(":water"))potion="";
            slots.add(new Hk3EggStorageFacts.Stack(BuiltInRegistries.ITEM.getKey(s.getItem()).toString(),s.getCount(),s.getDamageValue(),s.isEdible(),s.hasCustomHoverName()?s.getHoverName().getString():"",potion));
            if(slots.size()>54)return List.of();
        }return List.copyOf(slots);
    }
    public static void changed(ServerPlayer p,AbstractContainerMenu menu,List<Hk3EggStorageFacts.Stack> before,List<Hk3EggStorageFacts.Stack> after,java.util.BitSet authored){
        if(before.isEmpty()||before.size()!=after.size())return;
        Hk3EggExtraScenes.stored(p,menu,before,after);
        Hk3EggScenePaths.stored(p,menu,before,after);
        Hk3EggTools.stored(p,menu,before,after);
        Hk3EggDispenser.stored(p,menu,before,after);
        Hk3EggDecor.container(p,menu,before,after);
        Hk3EggContainerSequences.changed(p,menu,before,after);
        for(int id:Hk3EggStorageFacts.evaluate(before,after,menu instanceof ChestMenu,authored))Hk3EggRuntime.observe(p,"container",Map.of("case",Integer.toString(id)));
    }
    public static void closed(ServerPlayer p,AbstractContainerMenu menu,List<Hk3EggStorageFacts.Stack> original,List<Hk3EggStorageFacts.Stack> last,boolean changed){
        if(!changed||last.isEmpty()||!last.equals(snapshot(menu,p)))return;
        var f=new LinkedHashMap<String,String>();
        f.put("empty",Long.toString(last.stream().filter(Hk3EggStorageFacts.Stack::empty).count()));
        f.put("chest",Boolean.toString(menu instanceof ChestMenu));
        f.put("wheat",Long.toString(Hk3EggStorageFacts.count(last,"minecraft:wheat")));
        f.put("carrot",Long.toString(Hk3EggStorageFacts.count(last,"minecraft:carrot")));
        f.put("potato",Long.toString(Hk3EggStorageFacts.count(last,"minecraft:potato")));
        Hk3EggRuntime.observe(p,"container_close",f);
        if(original.stream().allMatch(Hk3EggStorageFacts.Stack::empty)&&Hk3EggStorageFacts.count(last,"minecraft:wheat")==99)Hk3EggRuntime.observe(p,"container",Map.of("case","320"));
    }
}
