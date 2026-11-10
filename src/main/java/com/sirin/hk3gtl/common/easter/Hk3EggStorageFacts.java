package com.sirin.hk3gtl.common.easter;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:12:10（修订128）：删除无；新增容器事务前后快照纯判定；修改无；用途：只有本人有效存取后检测布局，搬运不算制作，最多54槽。 */
/** 【变更记录 #2】2026-10-01 04:30:25（修订128）：删除：旧固定上限或被替代的分支；新增/修改：容器布局要求本次本人操作已确认的槽位，拒绝读取别人现成布局误领奖；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 04:43:52（修订128）：删除：旧固定上限或被替代的分支；新增/修改：15本书及本人存入两种GT信用币只在实际数量增加后判断；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 04:47:12（修订128）：删除：旧固定上限或被替代的分支；新增/修改：按SCP已审修订2纠正049所需黑色染料和玻璃瓶、1762所需龙息瓶，移除旧题材混用物品；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggStorageFacts {
    public record Stack(String id,int count,int damage,boolean food,String name,String potion){
        public boolean empty(){return count<=0;}
    }
    private Hk3EggStorageFacts(){}
    public static long count(List<Stack> slots,String id){return slots.stream().filter(s->s.id.equals(id)).mapToLong(Stack::count).sum();}
    public static Set<Integer> evaluate(List<Stack> before,List<Stack> after,boolean chest,BitSet authored){
        if(before.size()!=after.size()||after.isEmpty()||after.size()>54||before.equals(after))return Set.of();
        var ids=new HashSet<Integer>();
        if(increased(before,after,"minecraft:book")&&count(after,"minecraft:book")==15)ids.add(295);
        if(increased(before,after,"gtceu:silver_credit")||increased(before,after,"gtceu:copper_credit")){
            if(count(after,"gtceu:silver_credit")>0&&count(after,"gtceu:copper_credit")>0)ids.add(238);
        }
        if(increased(before,after,"gtlcore:compressed_pufferfish"))ids.add(243);
        if(before.stream().allMatch(Stack::empty)&&increased(before,after,"gtlcore:contaminated_petri_dish")&&after.stream().filter(s->!s.empty()).allMatch(s->s.id.equals("gtlcore:contaminated_petri_dish")))ids.add(244);
        if(increased(before,after,"gtceu:tantalum_capacitor")&&before.stream().anyMatch(s->!s.empty())&&before.stream().filter(s->!s.empty()).allMatch(s->s.id.startsWith("gtceu:")&&s.id.endsWith("capacitor")))ids.add(214);
        for(int i=0;i<after.size();i++)for(int j=i+1;j<after.size();j++){
            Stack a=after.get(i),b=after.get(j);
            if(!a.empty()&&!b.empty()&&a.id.endsWith("_pickaxe")&&a.id.equals(b.id)&&a.damage!=b.damage&&(!a.equals(before.get(i))||!b.equals(before.get(j))))ids.add(282);
        }
        if(sequence(after,new int[]{1,1,2,3,5,8},true,false))ids.add(331);
        if(sequence(after,new int[]{2,3,5,7,11},false,false))ids.add(332);
        if(sequence(after,new int[]{1,2,4,8,16,32,64,1},true,true))ids.add(333);
        for(int i=0;i+5<=after.size();i++)if(after.subList(i,i+5).stream().allMatch(s->!s.empty()&&s.food)&&after.subList(i,i+5).stream().map(Stack::id).distinct().count()==5)ids.add(285);
        if(chest&&after.size()==27){
            if(after.subList(0,12).stream().allMatch(s->s.count==1)&&after.subList(0,12).stream().map(Stack::id).distinct().count()==12)ids.add(292);
            if(after.stream().noneMatch(Stack::empty))ids.add(307);
        }
        if(count(after,"minecraft:stone_bricks")==256&&increased(before,after,"minecraft:stone_bricks"))ids.add(323);
        if(count(after,"minecraft:cobblestone")==64&&after.stream().filter(s->!s.empty()).count()==16&&after.stream().filter(s->!s.empty()).allMatch(s->s.id.equals("minecraft:cobblestone")&&s.count==4))ids.add(296);
        var nonempty=after.stream().filter(s->!s.empty()).toList();
        if(nonempty.size()==2&&nonempty.get(0).id.equals(nonempty.get(1).id)&&nonempty.stream().allMatch(s->s.count==32))ids.add(312);
        if(count(before,"minecraft:cobblestone")==64&&before.stream().filter(s->!s.empty()).count()==1&&count(after,"minecraft:cobblestone")==65&&after.stream().filter(s->!s.empty()).count()==2)ids.add(318);
        if(chest&&increasedAny(before,after)&&count(after,"minecraft:black_dye")==1&&count(after,"minecraft:glass_bottle")==1&&count(after,"minecraft:paper")==1)ids.add(387);
        if(chest&&increasedAny(before,after)&&count(after,"minecraft:paper")>=1&&count(after,"minecraft:feather")>=1&&count(after,"minecraft:dragon_breath")>=1)ids.add(420);
        if(after.stream().filter(s->!s.empty()&&!s.potion.isEmpty()).map(Stack::potion).distinct().count()>=4&&increasedAny(before,after))ids.add(442);
        // 布局必须来自本人的成功点击；既有布置不能因存入一个无关物品而领取。
        boolean authoredContents=true;
        for(int i=0;i<after.size();i++)if(!after.get(i).empty()&&!authored.get(i)){authoredContents=false;break;}
        if(!authoredContents)ids.removeAll(Set.of(238,282,285,292,296,307,312,331,332,333,387,420,442));
        return Set.copyOf(ids);
    }
    public static boolean increased(List<Stack> before,List<Stack> after,String id){return count(after,id)>count(before,id);}
    private static boolean increasedAny(List<Stack> before,List<Stack> after){return after.stream().anyMatch(s->!s.empty()&&increased(before,after,s.id));}
    private static boolean sequence(List<Stack> a,int[] counts,boolean same,boolean lastDifferent){
        for(int start=0;start+counts.length<=a.size();start++){
            boolean ok=true;String id=a.get(start).id;
            for(int j=0;j<counts.length;j++){var s=a.get(start+j);if(s.count!=counts[j]||(same&&j<counts.length-(lastDifferent?1:0)&&!s.id.equals(id))||(lastDifferent&&j==counts.length-1&&s.id.equals(id))){ok=false;break;}}
            if(ok)return true;
        }return false;
    }
}
