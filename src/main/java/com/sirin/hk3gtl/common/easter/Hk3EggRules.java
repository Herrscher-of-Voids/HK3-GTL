package com.sirin.hk3gtl.common.easter;

import com.google.gson.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** 【变更记录 #1】2026-10-01 04:08:14（修订128）：删除无；新增服务端事实匹配规则；用途：缺字段与空条件关闭，不接受自由文本作为已完成事件，不将目录数量当作执行覆盖。 */
/** 【变更记录 #2】2026-10-01 05:09:29（修订128）：删除：旧固定上限或被替代的分支；新增/修改：执行规则必须携带当前审核条件全文且逐字相同，防止目录更新后无声沿用旧来源；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggRules {
    public enum Operation { EQ, CONTAINS, AT_LEAST, AT_MOST }
    public record Check(String field,Operation op,String value){
        public boolean matches(Map<String,String> facts){
            String actual=facts.get(field);if(actual==null)return false;
            return switch(op){
                case EQ -> actual.equals(value);
                case CONTAINS -> actual.contains(value);
                case AT_LEAST,AT_MOST -> compare(actual,value,op);
            };
        }
        private static boolean compare(String a,String b,Operation op){
            try{long x=Long.parseLong(a),y=Long.parseLong(b);return op==Operation.AT_LEAST?x>=y:x<=y;}
            catch(NumberFormatException bad){return false;}
        }
    }
    public record Rule(String id,String event,List<Check> checks){
        public Rule {checks=List.copyOf(checks);}
        public boolean matches(String name,Map<String,String> facts){return name.equals(event)&&!checks.isEmpty()&&checks.stream().allMatch(c->c.matches(facts));}
    }
    private static final List<Rule> RULES=load();
    private static final Map<String,List<Rule>> BY_EVENT=index(RULES);
    private Hk3EggRules(){}
    public static List<Rule> all(){return RULES;}
    public static List<Rule> forEvent(String event){return BY_EVENT.getOrDefault(event,List.of());}
    public static Map<String,List<Rule>> index(List<Rule> rules){
        var result=new LinkedHashMap<String,List<Rule>>();
        for(var r:rules)result.computeIfAbsent(r.event,k->new ArrayList<>()).add(r);
        result.replaceAll((k,v)->List.copyOf(v));return Collections.unmodifiableMap(result);
    }
    public static List<Rule> parse(Reader reader){
        var root=JsonParser.parseReader(reader).getAsJsonObject();
        if(root.get("schema").getAsInt()!=1)throw new IllegalArgumentException("未知彩蛋规则格式");
        var result=new ArrayList<Rule>();var ids=new HashSet<String>();
        for(var raw:root.getAsJsonArray("rules")){
            var r=raw.getAsJsonObject();String id=r.get("id").getAsString(),event=r.get("event").getAsString();
            if(!Hk3EggCatalog.contains(id)||!ids.add(id)||event.isBlank())throw new IllegalArgumentException("无效或重复彩蛋规则："+id);
            if(!r.has("approvedCondition")||!Hk3EggCatalog.get(id).condition().equals(r.get("approvedCondition").getAsString()))throw new IllegalArgumentException("彩蛋规则来源与审核条件不一致："+id);
            var checks=new ArrayList<Check>();
            for(var value:r.getAsJsonArray("checks")){
                var c=value.getAsJsonObject();String field=c.get("field").getAsString(),expected=c.get("value").getAsString();
                Operation op=Operation.valueOf(c.get("op").getAsString());
                if(field.isBlank()||expected.isBlank())throw new IllegalArgumentException("空彩蛋条件");
                if(op==Operation.AT_LEAST||op==Operation.AT_MOST)Long.parseLong(expected);
                checks.add(new Check(field,op,expected));
            }
            if(checks.isEmpty())throw new IllegalArgumentException("禁止无条件彩蛋："+id);
            result.add(new Rule(id,event,checks));
        }
        return List.copyOf(result);
    }
    private static List<Rule> load(){
        try(var in=Hk3EggRules.class.getResourceAsStream("/assets/hk3gtl/narrative/easter_rules.json")){
            if(in==null)throw new IllegalStateException("彩蛋执行规则缺失");
            return parse(new InputStreamReader(in,StandardCharsets.UTF_8));
        }catch(IOException e){throw new IllegalStateException("彩蛋规则读取失败",e);}
    }
}
