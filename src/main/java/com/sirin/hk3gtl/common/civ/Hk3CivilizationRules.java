package com.sirin.hk3gtl.common.civ;
import java.util.*;
import java.util.function.Predicate;

/** 【变更记录 #1】2026-09-30 23:43:42（修订120）：删除无；新增/修改：C0—C7八级固定名称、逐级累计真实成果条件与缺项查询；用途：按真实团队事实展示文明进度，不给机器/配方增加等级锁。 */
public final class Hk3CivilizationRules {
    public record Requirement(String key,String label){}
    public record Level(int index,String name,List<Requirement> requirements){public Level{requirements=List.copyOf(requirements);}}
    private static Requirement r(String key,String label){return new Requirement(key,label);}
    public static final List<Level> LEVELS=List.of(
        new Level(0,"新生文明",List.of()),
        new Level(1,"崩坏识别",List.of(r("contact","本队完成奥托首信及任一回信"),r("research:RN-HED","完成崩坏能识别研究"),r("experiment:RN-HED","真实采样记录"),r("experiment:RN-HSA","真实光谱检测记录"))),
        new Level(2,"稳定工业",List.of(r("research:RN-LES","完成液态稳定化研究"),r("research:RN-SMR","完成稳定介质再生研究"),r("experiment:RN-LES","实际生产稳定液"),r("experiment:RN-SMR","实际完成基础再生"))),
        new Level(3,"材料与核心",List.of(r("research:RN-SPM","完成魂钢精密加工研究"),r("research:RN-CCE","完成核心结晶研究"),r("fact:soulium_processing","合格魂钢加工件生产"),r("fact:crystal_growth","基础核心晶体生产"))),
        new Level(4,"量子航路",List.of(r("review:1","本队完成一审"),r("research:RN-WCP","完成世界泡坐标解析研究"),r("research:RN-UED","完成无人采掘研究"),r("fact:drone_return","真实世界泡采掘结算"))),
        new Level(5,"虚数联系",List.of(r("research:RN-IAA","完成虚数锚定研究"),r("research:RN-WME","完成世界维系研究"),r("fact:real_termination","真实世界泡终止回收"),r("fact:simulation_full_chain","同批模拟构筑、稳定、回收"),r("fact:world_maintenance","维系原型真实运行"),r("review:2","本队完成二审"))),
        new Level(6,"文明奇观",List.of(r("research:RN-CEE","完成工程验收方法研究"),r("engineering:any_wonder","至少一座奇观真实工程验收"))),
        new Level(7,"认知与审判准备",List.of(r("all_research","完成全部100课题"),r("engineering:15_wonders","十五座奇观工程验收"),r("engineering:hyperion","仿制休伯利安工程验收"),r("research:RN-CAV","完成文明成果交叉验证")))
    );
    private Hk3CivilizationRules(){}
    /** 必须按级累计，不允许持有后期物品或只满足高等级条件跳过前级。 */
    public static int achieved(Predicate<String> facts){
        int level=0;for(int i=1;i<LEVELS.size();i++){
            if(!LEVELS.get(i).requirements.stream().allMatch(r->facts.test(r.key)))break;level=i;
        }return level;
    }
    public static String title(int level){if(level<0||level>=LEVELS.size())throw new IllegalArgumentException("文明等级越界");return "C"+level+" "+LEVELS.get(level).name;}
    public static List<Requirement> missingThrough(int target,Predicate<String> facts){
        if(target<0||target>7)throw new IllegalArgumentException("文明目标越界");
        var result=new ArrayList<Requirement>();for(int i=1;i<=target;i++)for(var r:LEVELS.get(i).requirements)if(!facts.test(r.key))result.add(r);return List.copyOf(result);
    }
}
