package com.sirin.hk3gtl.test.circuit;

import com.sirin.hk3gtl.common.research.*;
import net.minecraft.resources.ResourceLocation;
import java.util.*;
import java.util.concurrent.*;

/** 【变更记录 #1】2026-10-01 21:12:01（修订150）：删除无；新增真实门槛表的覆盖回归、并发合并及外部修改隔离测试；修改无；用途：防止多前置悄然丢失，不使用游戏存档。 */
public final class RecipeGateMergeTest {
    private static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
    public static void run() throws Exception {
        String type="test_gate_merge",name="overlap";
        var key=new ResourceLocation("hk3gtl",type+"/"+name);
        Hk3RecipeResearchGate.bindAll(type,name,List.of("RN-CQS","RN-WCP"));
        Hk3RecipeResearchGate.bind(type,name,"RN-CQS");
        check(Hk3RecipeResearchGate.getAllRequiredResearch(key).equals(List.of("RN-CQS","RN-WCP")),"单项绑定不能丢失另一前置");
        var snapshot=Hk3RecipeResearchGate.getAllRequiredResearch(key);
        Hk3RecipeResearchGate.bindAll(type,name,List.of("RN-WCP","RN-IAA"));
        check(snapshot.equals(List.of("RN-CQS","RN-WCP")),"旧查询快照稳定");
        check(Hk3RecipeResearchGate.getAllRequiredResearch(key).equals(List.of("RN-CQS","RN-WCP","RN-IAA")),"多项重叠追加去重");
        Hk3RecipeResearchGate.bindAll(type,name,List.of());
        check(Hk3RecipeResearchGate.getAllRequiredResearch(key).size()==3,"空绑定不抹除条件");
        boolean immutable=false;try{snapshot.clear();}catch(UnsupportedOperationException expected){immutable=true;}
        check(immutable,"调用者不能修改门槛列表");
        var row=Hk3RecipeResearchGate.snapshot().entrySet().stream().filter(e->e.getKey().equals(key)).findFirst().orElseThrow();
        immutable=false;try{row.setValue(List.of("RN-HED"));}catch(UnsupportedOperationException expected){immutable=true;}
        check(immutable&&Hk3RecipeResearchGate.getAllRequiredResearch(key).equals(List.of("RN-CQS","RN-WCP","RN-IAA")),"完整条目导出不可写回注册表");
        for(String namespace:List.of("hk3gtl","gtceu"))check(Hk3RecipeResearchGate.getAllRequiredResearch(new ResourceLocation(namespace,type+"/"+name)).size()==3,"双命名空间一致");
        try{Hk3RecipeResearchGate.bindAll(type,name,List.of("RN-HED"," "));throw new AssertionError("空研究应拒绝");}
        catch(IllegalArgumentException expected){check(Hk3RecipeResearchGate.getAllRequiredResearch(key).size()==3,"非法输入不部分写入");}
        var nodes=List.copyOf(Hk3ResearchPlans.all().keySet());
        var pool=Executors.newFixedThreadPool(8);
        try {
            var work=new ArrayList<Callable<Void>>();
            for(String id:nodes)work.add(()->{for(int i=0;i<10;i++)Hk3RecipeResearchGate.bind(type,"concurrent",id);return null;});
            for(var future:pool.invokeAll(work))future.get();
        } finally {pool.shutdownNow();}
        for(String namespace:List.of("hk3gtl","gtceu")) {
            var concurrent=new ResourceLocation(namespace,type+"/concurrent");
            check(new HashSet<>(Hk3RecipeResearchGate.getAllRequiredResearch(concurrent)).equals(new HashSet<>(nodes)),"1000次并发注册不丢前置");
            check(Hk3RecipeResearchGate.requiresResearch(concurrent)&&Hk3RecipeResearchGate.allGatedRecipeIds().contains(concurrent),"索引与执行来源一致");
        }
        System.out.println("RecipeGateMergeTest passed: overwrite regression, immutable snapshots, invalid-input atomicity and 1000 concurrent registrations");
    }
}
