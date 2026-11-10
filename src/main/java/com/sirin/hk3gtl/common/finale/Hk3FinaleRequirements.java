package com.sirin.hk3gtl.common.finale;

import net.minecraft.nbt.*;
import java.util.*;

/**
 * 【变更记录 #1】2026-10-01 16:49:18（修订135）
 * 删除：无；新增：终审固定准入清单、缺失与未接入的区分及完整来源快照。
 * 修改：只接受服务端适配器提供的事实，缺任一项不产生资格，不把库存或历史最高等级当现状。
 * 用途：个人经历与团队工程分开核对；未接入提供者必须返回等待，不开放客户端赋值入口。
 */
/** 【变更记录 #2】2026-10-01 22:50:14（第2次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
public final class Hk3FinaleRequirements {
    public enum State { COMPLETE, MISSING, WAITING }
    public record Requirement(String key,String label) {}
    public record Fact(State state,String detail,CompoundTag source) {
        public Fact { Objects.requireNonNull(state);Objects.requireNonNull(detail);source=source.copy(); }
        @Override public CompoundTag source(){return source.copy();}
        public static Fact missing(String detail){return new Fact(State.MISSING,detail,new CompoundTag());}
        public static Fact waiting(String detail){return new Fact(State.WAITING,detail,new CompoundTag());}
        public static Fact complete(CompoundTag source){return new Fact(State.COMPLETE,"",source);}
    }
    public record Item(Requirement requirement,State state,String detail) {}
    public static final List<Requirement> REQUIREMENTS;
    static {
        var list=new ArrayList<Requirement>();
        list.add(new Requirement("research","本队完成全部100课题"));
        list.add(new Requirement("first_person","本人完成一审会面"));
        list.add(new Requirement("second_person","本人完成二审会面"));
        list.add(new Requirement("second_team","本队二审许可"));
        list.add(new Requirement("communication","本人六组正式通信经历"));
        list.add(new Requirement("archive","完整文明档案"));
        list.add(new Requirement("c7","当前已核验C7文明事实"));
        for(int i=1;i<=15;i++)list.add(new Requirement(String.format(Locale.ROOT,"W%02d",i),String.format(Locale.ROOT,"W%02d 本队真实验收且当前结构完整",i)));
        list.add(new Requirement("hyperion","仿制休伯利安真实工程验收"));
        list.add(new Requirement("application","W15本次实际运行的申请校验回执"));
        REQUIREMENTS=List.copyOf(list);
    }
    public static final class Evaluation {
        private final List<Item> items;
        private final CompoundTag sources;
        private Evaluation(List<Item> items,CompoundTag sources){this.items=List.copyOf(items);this.sources=sources.copy();}
        public List<Item> items(){return items;}
        public boolean ready(){return !sources.isEmpty();}
        public CompoundTag sources(){return sources.copy();}
    }
    private Hk3FinaleRequirements(){}
    /** 输入只在申请时采集；全部通过才冻结来源，查询本身不授予任何许可。 */
    public static Evaluation evaluate(UUID actor,UUID team,long tick,Map<String,Fact> facts){
        Objects.requireNonNull(actor);Objects.requireNonNull(team);
        if(tick<0)throw new IllegalArgumentException("校验时刻无效");
        var items=new ArrayList<Item>();var proof=new CompoundTag();
        for(var r:REQUIREMENTS){
            var f=facts.getOrDefault(r.key(),Fact.waiting("尚未开放"));
            State state=f.state();String detail=f.detail();
            if(state==State.COMPLETE&&f.source().isEmpty()){state=State.MISSING;detail="缺少可追溯来源";}
            items.add(new Item(r,state,detail));
            if(state==State.COMPLETE)proof.put(r.key(),f.source());
        }
        var sources=new CompoundTag();
        if(items.stream().allMatch(i->i.state()==State.COMPLETE)){
            sources.putInt("Version",1);sources.putUUID("Actor",actor);sources.putUUID("Team",team);
            sources.putLong("Tick",tick);sources.put("Facts",proof);
        }
        return new Evaluation(items,sources);
    }
    public static boolean validSnapshot(CompoundTag n,UUID actor){
        if(n.getInt("Version")!=1||!n.hasUUID("Actor")||!actor.equals(n.getUUID("Actor"))
                ||!n.hasUUID("Team")||!n.contains("Tick",Tag.TAG_LONG)||n.getLong("Tick")<0
                ||!n.contains("Facts",Tag.TAG_COMPOUND))return false;
        var facts=n.getCompound("Facts");
        return facts.getAllKeys().size()==REQUIREMENTS.size()&&REQUIREMENTS.stream()
            .allMatch(r->facts.contains(r.key(),Tag.TAG_COMPOUND)&&!facts.getCompound(r.key()).isEmpty());
    }
}
