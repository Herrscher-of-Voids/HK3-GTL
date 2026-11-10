package com.sirin.hk3gtl.common.review;

import com.sirin.hk3gtl.common.research.Hk3ResearchBatchProofs;
import net.minecraft.nbt.*;
import java.util.*;
import java.util.function.*;

/**
 * 【变更记录 #1】2026-10-01 01:28:10（修订125）
 * 删除：无；新增：一二审真实研究及实际工况的固定准入清单和缺项说明。
 * 修改：资格只读取内测5研究账户，不接库存、旧研究ID、文明等级或客户端标记。
 * 用途：按主线阶段实现未给出代码映射的核验；资格快照不发许可，不代替召入场景。
 */
public final class Hk3ReviewRequirements {
    public record Requirement(String key,String label) {}
    public record Rules(List<Requirement> research,List<Requirement> facts) {
        public Rules { research=List.copyOf(research);facts=List.copyOf(facts); }
    }
    public record Evaluation(List<String> missing,CompoundTag sources) {
        public Evaluation { missing=List.copyOf(missing);sources=sources.copy(); }
        @Override public CompoundTag sources(){return sources.copy();}
        public boolean ready(){return missing.isEmpty()&&!sources.isEmpty();}
    }
    private static Requirement r(String id,String label){return new Requirement(id,label);}
    private static final Rules FIRST=new Rules(List.of(
            r("RN-SPM","魂钢精密加工研究"),r("RN-CCE","仿制核心结晶研究"),
            r("RN-GSC","气态崩坏能采集研究"),r("RN-CJK","仿制千界一乘研究")),List.of(
            r("soulium_processing","魂钢加工实际产出"),r("crystal_growth","基础核心结晶实际产出"),
            r("gas_collection","气态采集实际产出"),r("divine_key_assembly","神之键部件实际装配")));
    private static final Rules SECOND=new Rules(List.of(
            r("RN-WCP","世界泡坐标解析研究"),r("RN-UED","无人世界泡采掘研究"),
            r("RN-IAA","虚数空间锚定研究"),r("RN-WME","世界维系试验研究"),
            r("RN-SWR","模拟世界泡回收研究")),List.of(
            r("drone_return","真实世界泡无人采掘结算"),r("real_termination","真实世界泡终止回收"),
            r("simulation_full_chain","同批模拟构筑、稳定及回收"),r("world_maintenance","世界维系原型真实运行")));
    private Hk3ReviewRequirements() {}
    public static Rules rules(Hk3ReviewLedger.Kind kind){return Objects.requireNonNull(kind)==Hk3ReviewLedger.Kind.FIRST?FIRST:SECOND;}
    /** 完整来源只在全部条件齐备时生成；读取者传入服务端已完成研究及真实回执。 */
    public static Evaluation evaluate(UUID team,Hk3ReviewLedger.Kind kind,Predicate<String> completed,
            Function<String,CompoundTag> receipt,UUID firstReview){
        Objects.requireNonNull(team);var rule=rules(kind);var missing=new ArrayList<String>();
        var sources=new CompoundTag();var research=new ListTag();var facts=new CompoundTag();
        if(kind==Hk3ReviewLedger.Kind.SECOND&&firstReview==null)missing.add("本队完整一审会面许可");
        for(var item:rule.research()){
            if(completed.test(item.key()))research.add(StringTag.valueOf(item.key()));
            else missing.add(item.label()+"（"+item.key()+"）");
        }
        for(var item:rule.facts()){
            var proof=receipt.apply(item.key());
            if(proof!=null&&Hk3ResearchBatchProofs.valid(proof)
                    &&(!proof.contains("Team")||(proof.hasUUID("Team")&&team.equals(proof.getUUID("Team")))))facts.put(item.key(),proof.copy());
            else missing.add(item.label());
        }
        if(missing.isEmpty()){
            sources.putInt("RuleVersion",1);sources.putUUID("Team",team);sources.putString("Kind",kind.name());
            sources.putString("Source","industrial_research_account");sources.put("Research",research);sources.put("Facts",facts);
            if(firstReview!=null&&kind==Hk3ReviewLedger.Kind.SECOND)sources.putUUID("FirstReview",firstReview);
        }
        return new Evaluation(missing,sources);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
