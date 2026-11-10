package com.sirin.hk3gtl.common.easter;

import com.sirin.hk3gtl.common.narrative.*;
import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import java.util.*;

/** 【变更记录 #1】2026-10-01 04:08:14（修订128）：删除无；新增经过服务端操作确认的彩蛋事实入口；用途：只投递个人收藏，隔离研究、外交、阶段授予；投递失败不提前写去重标记。 */
/** 【变更记录 #2】2026-10-01 05:50:31（修订128）：删除：无；新增/修改：信箱或收藏投递异常限频记录，不向已完成的真实交互回调传播；未投递不提前写去重；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggRuntime {
    public static final String ROOT="hk3gtl_egg_v2";
    private static final java.util.concurrent.atomic.AtomicLong LAST_FAILURE=new java.util.concurrent.atomic.AtomicLong();
    private Hk3EggRuntime(){}
    public static CompoundTag state(ServerPlayer p){
        var root=p.getPersistentData();if(!root.contains(ROOT,10))root.put(ROOT,new CompoundTag());return root.getCompound(ROOT);
    }
    public static void observe(ServerPlayer p,String event,Map<String,String> facts){
        if(!p.server.isSameThread())throw new IllegalStateException("彩蛋事实必须在服务端线程提交");
        for(var r:Hk3EggRules.forEvent(event)){
            if(Hk3NarrativeLog.isUnlocked(p,r.id()))continue;
            if(r.matches(event,facts))try{award(p,r.id());}catch(RuntimeException failure){
                long now=System.nanoTime(),previous=LAST_FAILURE.get();
                if((previous==0||now-previous>=60_000_000_000L)&&LAST_FAILURE.compareAndSet(previous,now))com.mojang.logging.LogUtils.getLogger().error("[HK3GTL] 可选彩蛋投递失败，不影响触发它的游戏操作。id={}",r.id(),failure);
            }
        }
    }
    private static void award(ServerPlayer p,String id){
        var node=Hk3NarrativeNodes.byId(id);
        if(node==null||!Hk3EggCatalog.contains(id))return;
        var receipt=Hk3CollectionRecords.record(p.getPersistentData(),Hk3PhoneData.get(p),p.getUUID(),node,
                System.currentTimeMillis(),key->Component.translatable(key).getString());
        if(receipt.delivered())com.sirin.hk3gtl.common.phone.Hk3PhoneService.toast(p,"narrative_"+id,receipt.title(),receipt.body(),"chatter",0);
    }
    public static Map<String,String> fields(String... pairs){
        if(pairs.length%2!=0)throw new IllegalArgumentException("彩蛋事实必须成对");
        var result=new LinkedHashMap<String,String>();
        for(int i=0;i<pairs.length;i+=2)result.put(pairs[i],pairs[i+1]);
        return Map.copyOf(result);
    }
}
