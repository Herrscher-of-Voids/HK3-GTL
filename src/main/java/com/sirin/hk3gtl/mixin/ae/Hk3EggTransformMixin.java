package com.sirin.hk3gtl.mixin.ae;
import appeng.recipes.transform.*;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.level.Level;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.registries.BuiltInRegistries;
import java.util.*;
import java.util.function.Predicate;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import com.sirin.hk3gtl.mixin.Hk3EggItemThrowerAccessor;
import com.sirin.hk3gtl.common.easter.Hk3EggProductionData;
import com.sirin.hk3gtl.common.easter.Hk3EggCraftingReceipts.TransformInput;
@Mixin(value=TransformLogic.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:27:59（修订128）：删除无；新增AE实际提交、完成与转化回执；修改无；用途：失败、取消、模拟及创造拿取不当生产，归属写入CPU存档。 */
/** 【变更记录 #2】2026-10-01 06:35:47（修订128）：删除：无；新增/修改：消除Mixin私有嵌套快照引用，改用公共独立记录类型；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggTransformMixin {
    @Unique private static final ThreadLocal<List<TransformInput>> hk3gtl$before=new ThreadLocal<>();
    @Inject(method="tryTransform",at=@At("HEAD"))private static void hk3gtl$before(ItemEntity item,Predicate<TransformCircumstance> circumstance,CallbackInfoReturnable<Boolean> ci){
        hk3gtl$before.remove();if(!(item.level() instanceof ServerLevel))return;
        var region=new net.minecraft.world.phys.AABB(item.getX()-1,item.getY()-1,item.getZ()-1,item.getX()+1,item.getY()+1,item.getZ()+1);
        var list=new ArrayList<TransformInput>();for(var e:item.level().getEntitiesOfClass(ItemEntity.class,region)){var owner=((Hk3EggItemThrowerAccessor)e).hk3gtl$thrower();if(owner!=null)list.add(new TransformInput(e,e.getItem().getCount(),owner));}hk3gtl$before.set(list);
    }
    @Redirect(method="tryTransform",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/Level;addFreshEntity(Lnet/minecraft/world/entity/Entity;)Z",remap=true))
    private static boolean hk3gtl$output(Level level,Entity entity){boolean success=level.addFreshEntity(entity);var before=hk3gtl$before.get();
        if(success&&level instanceof ServerLevel server&&entity instanceof ItemEntity result&&BuiltInRegistries.ITEM.getKey(result.getItem().getItem()).toString().equals("ae2:fluix_crystal")&&before!=null){var owners=new HashSet<UUID>();for(var input:before)if(input.entity().getItem().getCount()<input.count())owners.add(input.owner());for(var owner:owners)Hk3EggProductionData.get(server.getServer()).produced(owner,"receipt:182",1);}
        return success;
    }
    @Inject(method="tryTransform",at=@At("RETURN"))private static void hk3gtl$clear(ItemEntity item,Predicate<TransformCircumstance> circumstance,CallbackInfoReturnable<Boolean> ci){hk3gtl$before.remove();}
}
