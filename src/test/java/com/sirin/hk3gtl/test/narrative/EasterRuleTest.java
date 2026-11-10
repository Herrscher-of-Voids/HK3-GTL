package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.easter.*;
import java.util.*;

/** 【变更记录 #1】2026-10-01 03:55:00（修订128）：删除无；新增真实规则评估与空字段/错误事件/边界值回归；用途：报告已绑定数，不把目录测试冒充所有触发验收。 */
/** 【变更记录 #2】2026-10-01 05:30:00（修订128）：删除：旧固定上限或被替代的分支；新增/修改：执行规则检查前验证当前依赖字节码中的所有彩蛋Mixin目标，仍不宣称游戏启动通过；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 05:41:36（修订128）：删除：旧固定上限或被替代的分支；新增/修改：建筑布局测试覆盖缺格与不足尺寸，不把总方块数当矩形；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 05:44:13（修订128）：删除：旧固定上限或被替代的分支；新增/修改：四向门边界测试覆盖实际跨度16、缺方向与跨度32反例；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class EasterRuleTest {
    private static int checks;
    private static void check(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
    public static void main(String[] args){
        EasterHookContractTest.main(args);
        var doors=List.of(new Hk3EggDoorPattern.Door(0,0,0,0),new Hk3EggDoorPattern.Door(16,0,0,1),new Hk3EggDoorPattern.Door(0,16,0,2),new Hk3EggDoorPattern.Door(0,0,16,3));
        check(Hk3EggDoorPattern.matches(doors),"四向门完整16格边界");
        check(!Hk3EggDoorPattern.matches(doors.subList(0,3)),"缺少一个方向不通过");
        check(!Hk3EggDoorPattern.matches(List.of(new Hk3EggDoorPattern.Door(-16,0,0,0),new Hk3EggDoorPattern.Door(16,0,0,1),new Hk3EggDoorPattern.Door(0,0,0,2),new Hk3EggDoorPattern.Door(0,0,1,3))),"两侧各16不能冒充同一16格范围");
        var floor=new boolean[13][13];for(int x=4;x<11;x++)for(int z=3;z<10;z++)floor[x][z]=true;
        check(Hk3EggFloorPattern.contains(floor,7,7),"完整7乘7布局");floor[7][7]=false;
        check(!Hk3EggFloorPattern.contains(floor,7,7),"布局缺一格不通过");
        check(!Hk3EggFloorPattern.contains(new boolean[6][7],7,7),"边界不足不通过");
        check(Hk3EggCatalog.all().size()==500,"审核正文500条");
        check(!Hk3EggCatalog.contains("E-EG-999999"),"拒绝未知ID");
        for(var r:Hk3EggRules.all()){
            check(Hk3EggCatalog.contains(r.id()),"规则正文存在");
            check(!r.matches(r.event(),Map.of()),"空事实不触发");
            var facts=new HashMap<String,String>();
            for(var c:r.checks())facts.put(c.field(),c.value());
            check(r.matches(r.event(),facts),"边界事实满足");
            check(!r.matches("unknown_event",facts),"其他事件不能借用事实");
            for(var c:r.checks()){
                var missing=new HashMap<>(facts);missing.remove(c.field());
                check(!r.matches(r.event(),missing),"任一必要字段缺失拒绝");
                if(c.op()==Hk3EggRules.Operation.AT_LEAST){
                    var below=new HashMap<>(facts);below.put(c.field(),Long.toString(Long.parseLong(c.value())-1));
                    check(!r.matches(r.event(),below),"不足阈值拒绝");
                }
            }
        }
        check(Hk3EggNoteFacts.hasValidDate("备份 2024-02-29"),"接受闰日");
        check(Hk3EggNoteFacts.hasValidDate("备份 2026年10月1日"),"接受中文日期");
        for(String invalid:List.of("2026-99-99","2026-02-29","2026年4月31日","12026-10-01","2026年10-01"))check(!Hk3EggNoteFacts.hasValidDate(invalid),"拒绝无效日期");
        var paragraphs=Hk3EggNoteFacts.saved("笔记","一\n\n二\n三\n四\n五\n六\n七\n八\n九\n十");
        check(paragraphs.get("paragraphs").equals("10"),"不把空白行算成段落");
        check(Hk3EggNoteFacts.saved("标题","abcdefghijklmnopqrstuvwxyz").get("alphabet").equals("true"),"字母大小写兼容");
        check(Hk3EggNoteFacts.saved("ABCDEFGHIJKLMNOPQRSTUVWXYZ","abc").get("alphabet").equals("false"),"题目不能冒充正文");
        check(new Hk3EggRules.Check("n",Hk3EggRules.Operation.AT_LEAST,"20").matches(Map.of("n","20")),"整数边界");
        for(String invalid:List.of("NaN","Infinity","1.5","9999999999999999999999"))
            check(!new Hk3EggRules.Check("n",Hk3EggRules.Operation.AT_LEAST,"20").matches(Map.of("n",invalid)),"非法数字拒绝");
        check(!new Hk3EggRules.Rule("x","event",List.of()).matches("event",Map.of()),"无条件规则不能触发");
        var cursor=new Hk3EggReadingCursor("第一段\n 第二段\n末句☆");
        check(!cursor.accept(6,"末句☆"),"直接跳末尾不算全读");
        check(cursor.accept(0,"第一段"),"第一页确实匹配");
        check(!cursor.accept(0,"第一段"),"旧页重复不计");
        check(!cursor.accept(3,"伪造内容"),"未投递的正文不能读完");
        check(cursor.accept(3,"第二段"),"连续页匹配");check(cursor.accept(6,"末句☆"),"最后一页匹配");
        check(cursor.done()&&cursor.pages()==3,"全文完整连续读取");
        check(!new Hk3EggReadingCursor("").done(),"空正文不会完成");
        var egg388=Hk3EggRules.all().stream().filter(r->r.id().equals("E-EG-388")).findFirst().orElseThrow();
        check(egg388.matches("note_open",Map.of("title","不是圆的")),"SCP055使用已审笔记标题");
        check(!egg388.matches("note_open",Map.of("title","世界是圆的")),"旧笔记标题不得触发已审新条件");
        var egg406=Hk3EggRules.all().stream().filter(r->r.id().equals("E-EG-406")).findFirst().orElseThrow();
        check(egg406.matches("note_saved",Map.of("body","我是一台烤面包机")),"SCP426按审核文本检测");
        check(!egg406.matches("note_saved",Map.of("body","我是一台咖啡机")),"旧关键词不得替代正文");
        var empty=new Hk3EggStorageFacts.Stack("minecraft:air",0,0,false,"","");
        var initial=new ArrayList<Hk3EggStorageFacts.Stack>(Collections.nCopies(27,empty));
        var layout=new ArrayList<>(initial);int[] fib={1,1,2,3,5,8};
        for(int i=0;i<fib.length;i++)layout.set(i,new Hk3EggStorageFacts.Stack("minecraft:stone",fib[i],0,false,"",""));
        var authored=new BitSet();authored.set(0,6);
        check(Hk3EggStorageFacts.evaluate(initial,layout,true,authored).contains(331),"本人逐槽保存斐波那契布局");
        check(!Hk3EggStorageFacts.evaluate(initial,layout,true,new BitSet()).contains(331),"他人现有布局拒绝");
        check(Hk3EggStorageFacts.evaluate(layout,layout,true,authored).isEmpty(),"纯打开不产生容器事务");
        var unrelated=new ArrayList<>(layout);unrelated.set(26,new Hk3EggStorageFacts.Stack("minecraft:dirt",1,0,false,"",""));
        var onlyOther=new BitSet();onlyOther.set(26);
        check(!Hk3EggStorageFacts.evaluate(layout,unrelated,true,onlyOther).contains(331),"无关物品存入不会领取现有数字布局");
        var two=List.of(new Hk3EggStorageFacts.Stack("minecraft:iron_pickaxe",1,20,false,"",""),new Hk3EggStorageFacts.Stack("minecraft:iron_pickaxe",1,21,false,"",""));
        var touched=new BitSet();touched.set(0,2);
        check(Hk3EggStorageFacts.evaluate(List.of(empty,empty),two,true,touched).contains(282),"同种镐不同耐久的本人存放");
        check(!Hk3EggStorageFacts.evaluate(List.of(empty,empty),List.of(two.get(0),two.get(0)),true,touched).contains(282),"相同耐久不能替代");
        var blackKit=List.of(new Hk3EggStorageFacts.Stack("minecraft:black_dye",1,0,false,"",""),new Hk3EggStorageFacts.Stack("minecraft:glass_bottle",1,0,false,"",""),new Hk3EggStorageFacts.Stack("minecraft:paper",1,0,false,"",""));
        var three=new BitSet();three.set(0,3);
        check(Hk3EggStorageFacts.evaluate(List.of(empty,empty,empty),blackKit,true,three).contains(387),"049严格采用审核黑色物品组合");
        var oldKit=List.of(new Hk3EggStorageFacts.Stack("minecraft:pink_dye",1,0,false,"",""),new Hk3EggStorageFacts.Stack("minecraft:honey_bottle",1,0,false,"",""),blackKit.get(2));
        check(!Hk3EggStorageFacts.evaluate(List.of(empty,empty,empty),oldKit,true,three).contains(387),"旧题材组合不可解锁049");
        check(Hk3EggProductionData.plus(Long.MAX_VALUE-1,2)==Long.MAX_VALUE,"工业累计溢出饱和");
        check(Hk3EggProductionData.plus(0,100)==100,"正常实际产量");
        System.out.println("Easter rules: "+checks+" checks passed; "+Hk3EggRules.all().size()+" bound / "+Hk3EggCatalog.all().size()+" catalog entries. This is not complete trigger coverage.");
    }
}
