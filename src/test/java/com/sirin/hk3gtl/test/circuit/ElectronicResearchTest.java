package com.sirin.hk3gtl.test.circuit;

import com.sirin.hk3gtl.common.research.*;
import net.minecraft.resources.ResourceLocation;
import java.util.*;

/** 【变更记录 #1】2026-10-01 20:59:23（修订149）：删除无；新增实际门槛注册表与研究前置检查；修改无；用途：验证多前置不丢失、两命名空间一致与种子前级知识无研究循环，不代替实际设备可达性验收。 */
public final class ElectronicResearchTest {
    public static void run() {
        for(int p=0;p<4;p++) {
            var expected=Hk3ElectronicResearch.requirements(p);
            Hk3RecipeResearchGate.bindAll("test_electronic", "platform_"+p,expected);
            for(String namespace:List.of("gtceu","hk3gtl")) {
                var actual=Hk3RecipeResearchGate.getAllRequiredResearch(new ResourceLocation(namespace,"test_electronic/platform_"+p));
                check(actual.equals(expected),"注册表完整保留多前置");
                for(String missing:expected)check(!actual.stream().allMatch(id->!id.equals(missing)),"任一研究未完成仍锁定");
            }
            int predecessor=14+p*4;
            for(String id:expected) {
                check(id.startsWith("RN-"),"不能依赖旧节点");
                var contract=Hk3ResearchExecutionContracts.get(id);check(contract!=null,"实际研究目录存在");
                check(contract.energyTier()<=predecessor,"门槛实验不要求平台首枚的后级电压");
                parents(id,new HashSet<>(),predecessor);
            }
            if(p>0)for(String prior:Hk3ElectronicResearch.requirements(p-1))
                check(expected.stream().anyMatch(id->ancestors(id).contains(prior)),"高平台知识不能越过前平台");
        }
        check(Hk3ElectronicResearch.requirements(1).equals(List.of("RN-MCE")),"MCE种子不能反锁于CPT或S02");
        boolean invalid=false;try{Hk3ElectronicResearch.requirements(4);}catch(IllegalArgumentException expected){invalid=true;}
        check(invalid,"未知平台拒绝回退");
        System.out.println("ElectronicResearchTest passed: four platform gates, namespace parity, every missing prerequisite, research ancestry and predecessor experiment energy");
    }
    private static Set<String> ancestors(String id) {var result=new HashSet<String>();collect(id,result);return result;}
    private static void collect(String id,Set<String> result) {if(result.add(id))for(String parent:Hk3ResearchExecutionContracts.get(id).prerequisites())collect(parent,result);}
    private static void parents(String id,Set<String> visited,int tier) {
        if(!visited.add(id))return;var c=Hk3ResearchExecutionContracts.get(id);
        check(c.energyTier()<=tier,"全部研究祖先仍在前级电压以内："+id);
        for(String parent:c.prerequisites())parents(parent,visited,tier);
    }
    private static void check(boolean value,String message) {if(!value)throw new AssertionError(message);}
}
