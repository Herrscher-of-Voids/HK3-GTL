package com.sirin.hk3gtl.common.easter;
import appeng.api.crafting.PatternDetailsHelper;
import appeng.api.stacks.*;
import appeng.crafting.pattern.AEProcessingPattern;
import appeng.blockentity.misc.InscriberBlockEntity;
import appeng.menu.implementations.InscriberMenu;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraftforge.event.entity.player.PlayerContainerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:45:29（修订128）：删除无；新增AE真实样板保存及压印输入消耗后回执；用途：拒绝模拟产出和空样板，离线产量持久记录，不授研究资格。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggAe {
    private Hk3EggAe(){}
    public static void encoded(ServerPlayer p,ItemStack before,ItemStack after){
        if(after.isEmpty()||ItemStack.matches(before,after))return;
        String id=BuiltInRegistries.ITEM.getKey(after.getItem()).toString();
        if(id.equals("ae2:crafting_pattern"))Hk3EggVanilla.caseEvent(p,192);
        if(!id.equals("ae2:processing_pattern"))return;
        var details=PatternDetailsHelper.decodePattern(after,p.level());
        if(!(details instanceof AEProcessingPattern current)||current.getInputs().length==0||current.getOutputs().length==0)return;
        Hk3EggVanilla.caseEvent(p,193);
        if(singleItem(current.getSparseInputs())&&singleItem(current.getSparseOutputs()))Hk3EggVanilla.caseEvent(p,281);
        var old=PatternDetailsHelper.decodePattern(before,p.level());
        if(old instanceof AEProcessingPattern previous){
            var a=previous.getSparseOutputs();var b=current.getSparseOutputs();
            if(a.length==b.length){
                for(int i=0;i<a.length;i++)if(a[i]!=null&&b[i]!=null&&a[i].what().equals(b[i].what())&&a[i].amount()!=b[i].amount()){Hk3EggVanilla.caseEvent(p,194);break;}
            }
        }
    }
    private static boolean singleItem(GenericStack[] values){
        long total=0;for(var v:values)if(v!=null){if(!(v.what() instanceof AEItemKey)||v.amount()!=1)return false;total++;}return total==1;
    }
    public static void inscribed(InscriberBlockEntity machine,ItemStack input,ItemStack result){
        var level=machine.getLevel();var n=machine.getPersistentData();
        if(level==null||level.isClientSide||level.getServer()==null||!n.hasUUID(Hk3EggProduction.OWNER)||result.isEmpty())return;
        var owner=n.getUUID(Hk3EggProduction.OWNER);var ledger=Hk3EggProductionData.get(level.getServer());
        String out=BuiltInRegistries.ITEM.getKey(result.getItem()).toString(),in=BuiltInRegistries.ITEM.getKey(input.getItem()).toString();
        ledger.produced(owner,out,result.getCount());
        if(out.equals("ae2:printed_silicon"))ledger.produced(owner,"receipt:187",1);
        for(var e:Map.of("logic",188,"calculation",189,"engineering",190).entrySet())
            if(in.equals("ae2:printed_"+e.getKey()+"_processor")&&out.equals("ae2:"+e.getKey()+"_processor"))ledger.produced(owner,"receipt:"+e.getValue(),1);
    }
    @SubscribeEvent public static void opened(PlayerContainerEvent.Open e){
        if(e.getEntity() instanceof ServerPlayer p&&e.getContainer() instanceof InscriberMenu&&Hk3EggVanilla.count(p,"ae2:logic_processor_press")>0&&Hk3EggVanilla.count(p,"ae2:calculation_processor_press")>0&&Hk3EggVanilla.count(p,"ae2:engineering_processor_press")>0)Hk3EggVanilla.caseEvent(p,186);
    }
}
