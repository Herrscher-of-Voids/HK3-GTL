package com.sirin.hk3gtl.test.review;

import com.sirin.hk3gtl.common.review.*;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.nbt.*;
import java.util.*;

/** 【变更记录 #1】2026-10-01 01:30:10（修订125）：删除无；新增审查准入、缺项、来源快照及研究防自锁回归；修改使用生产判定器和账本；用途：仅隔离测试回执，不冒充实际工业或多人游戏验收。 */
public final class ReviewQualificationTest {
    private static int checks;
    private static void check(boolean value,String message){if(!value)throw new AssertionError(message);checks++;}
    private static CompoundTag receipt(UUID team){
        var n=new CompoundTag();n.putUUID("Batch",UUID.randomUUID());n.putUUID("Team",team);
        n.putString("Facility","isolated_review_fixture");n.putString("Recipe","hk3gtl:test_only");n.putLong("Tick",1);
        var input=new CompoundTag();input.putLong("Amount",1);n.put("Inputs",input.copy());n.put("Outputs",input.copy());return n;
    }
    private static void acyclic(String id,boolean first,Set<String> visited){
        if(!visited.add(id))return;var c=Hk3ResearchExecutionContracts.get(id);check(c!=null,"准入课题必须属于正式100题");
        if(first)check(!c.facts().contains("cocoon_authorization"),"一审不反锁自身许可");
        check(c.facts().stream().noneMatch(f->f.startsWith("wonder_")||f.equals("all_fourteen_wonders")),"准入不反锁二审后的奇观");
        for(String parent:c.prerequisites())acyclic(parent,first,visited);
    }
    public static void main(String[] args){
        UUID team=UUID.randomUUID();
        for(var kind:Hk3ReviewLedger.Kind.values()){
            var rules=Hk3ReviewRequirements.rules(kind);var known=new HashSet<String>();var facts=new HashMap<String,CompoundTag>();
            for(var r:rules.research()){known.add(r.key());acyclic(r.key(),kind==Hk3ReviewLedger.Kind.FIRST,new HashSet<>());}
            for(var f:rules.facts()){
                check(Hk3ResearchExecutionContracts.factNames().contains(f.key()),"工况名称必须存在："+f.key());facts.put(f.key(),receipt(team));
            }
            UUID permit=kind==Hk3ReviewLedger.Kind.SECOND?UUID.randomUUID():null;
            var ready=Hk3ReviewRequirements.evaluate(team,kind,known::contains,facts::get,permit);
            check(ready.ready(),"完整真实格式回执可达标");
            check(ready.sources().getUUID("Team").equals(team),"来源固定本队");
            for(String missing:new ArrayList<>(known)){
                known.remove(missing);var result=Hk3ReviewRequirements.evaluate(team,kind,known::contains,facts::get,permit);
                check(!result.ready()&&result.sources().isEmpty()&&result.missing().size()==1,"缺任一课题不生成部分资格");known.add(missing);
            }
            for(String key:facts.keySet()){
                var original=facts.get(key);facts.put(key,new CompoundTag());
                check(!Hk3ReviewRequirements.evaluate(team,kind,known::contains,facts::get,permit).ready(),"空/静态工况不算实际生产");
                var invalid=original.copy();invalid.putUUID("Team",UUID.randomUUID());facts.put(key,invalid);
                check(!Hk3ReviewRequirements.evaluate(team,kind,known::contains,facts::get,permit).ready(),"拒绝串队回执");
                invalid=original.copy();invalid.remove("Outputs");facts.put(key,invalid);
                check(!Hk3ReviewRequirements.evaluate(team,kind,known::contains,facts::get,permit).ready(),"未输出不能取得准入");facts.put(key,original);
            }
            var retained=ready.sources();ready.sources().getCompound("Facts").getAllKeys().stream().findFirst().ifPresent(k->ready.sources().getCompound("Facts").remove(k));
            check(retained.equals(ready.sources()),"读取返回副本");
            var firstFact=facts.values().iterator().next();firstFact.putString("Recipe","changed_after_snapshot");
            check(retained.equals(ready.sources()),"原工况后续变化不修改既有资格来源");
            if(kind==Hk3ReviewLedger.Kind.SECOND){
                check(!Hk3ReviewRequirements.evaluate(team,kind,known::contains,facts::get,null).ready(),"二审必须有本队一审会面许可");
                check(ready.sources().getUUID("FirstReview").equals(permit),"二审资格引用具体一审会面");
            }else{
                var ledger=new Hk3ReviewLedger();check(ledger.qualify(team,kind,retained),"生产核验结果写入账本");
                var saved=Hk3ReviewLedger.load(ledger.save());check(saved.qualified(team,kind)&&!saved.settled(team,kind),"资格持久化不自动通过审查");
                check(saved.sources(team,kind).equals(retained),"来源完整存盘");
                check(!saved.qualify(team,kind,ready.sources()),"轮询不覆盖首次来源");
                check(!saved.qualified(UUID.randomUUID(),kind),"新队不继承旧队资格");
            }
        }
        var research=new Hk3ResearchData();
        check(!Hk3ReviewRequirements.evaluate(team,Hk3ReviewLedger.Kind.FIRST,id->research.completed(team,id),id->research.processFactReceipt(team,id),null).ready(),"实际新账户没有免费资格");
        System.out.println("Review qualification: "+checks+" checks passed; source-based gates only, live scenes pending");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
