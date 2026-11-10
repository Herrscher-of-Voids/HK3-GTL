package com.sirin.hk3gtl.common.narrative;

import java.util.*;

/** 【变更记录 #1】2026-10-01 01:54:14（修订127）：删除无；新增逐项核对的收藏分类目录；修改无；用途：旧角色评论、特殊数字和工业纪念属于可选收藏，正式交流单独保留；未知条目不自动豁免。 */
/** 【变更记录 #2】2026-10-01 03:50:42（修订128）：删除：旧固定上限或被替代的分支；新增/修改：新增目录逐项显式分类，未知ID仍不属于可选条目；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3CollectionCatalog {
    public enum Kind {
        OPTIONAL("optional"), FORMAL("formal"), MILESTONE("milestone"), UNCLASSIFIED("unclassified");
        public final String id;
        Kind(String id){this.id=id;}
        public String key(){return "hk3gtl.collection.kind."+id;}
    }
    private static final Map<String,String> OPTIONAL=new LinkedHashMap<>();
    private static final Set<String> FORMAL=new HashSet<>();
    private static final Set<String> MILESTONES=Set.of("MS-001","MS-002","MS-003","MS-004","MS-005");
    static {
        optional("comment",1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,51,52,54,58,74,88,90);
        optional("industry",31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49);
        optional("time",50,53,55,56,57,59,60,70,100);
        optional("number",61,62,63,64,65,66,67,68,69);
        optional("curiosity",71,72,73,75,76,77,78,79,80,81,82,83,84,85,86,87,89,91,92,93,94,95,96,97,98,99);
        for(var egg:com.sirin.hk3gtl.common.easter.Hk3EggCatalog.all())OPTIONAL.putIfAbsent(egg.id(),"catalog");
        OPTIONAL.put("EG-001","fragment");OPTIONAL.put("EG-002","fragment");OPTIONAL.put("EG-003","failure");
        formal("OT",5);formal("HQ",5);formal("WL",4);formal("FH",5);formal("EL",3);
        formal("WS",6);formal("AE",5);formal("SF",4);formal("FM",5);formal("BR",4);
        formal("SA",4);formal("MB",4);formal("KI",4);formal("LB",4);formal("TS",3);
        FORMAL.addAll(List.of("HQ-001","HQ-002","HQ-003","HQ-004","HQ-005","OT-001","OT-002","OT-003",
                "WL-001","WL-002","FH-001","EL-001","EL-002","WS-001","AE-001"));
    }
    private Hk3CollectionCatalog(){}
    private static void optional(String reason,int... indexes){for(int i:indexes){
        String id=String.format(Locale.ROOT,"E-EG-%03d",i);
        if(OPTIONAL.put(id,reason)!=null)throw new IllegalStateException("重复收藏分类："+id);
    }}
    private static void formal(String group,int count){for(int i=1;i<=count;i++)FORMAL.add(String.format(Locale.ROOT,"E-%s-%03d",group,i));}
    public static Kind kind(String id){
        if(OPTIONAL.containsKey(id))return Kind.OPTIONAL;
        if(FORMAL.contains(id))return Kind.FORMAL;
        if(MILESTONES.contains(id))return Kind.MILESTONE;
        return Kind.UNCLASSIFIED;
    }
    public static boolean optional(String id){return kind(id)==Kind.OPTIONAL;}
    public static boolean optionalEvent(String event){
        var nodes=Hk3NarrativeNodes.byEventIdAll(event);
        return !nodes.isEmpty()&&nodes.stream().allMatch(n->optional(n.id()));
    }
    public static String reasonKey(String id){return "hk3gtl.collection.reason."+OPTIONAL.getOrDefault(id,kind(id).id);}
    public static boolean matches(String id,String filter){return "all".equals(filter)||kind(id).id.equals(filter);}
    public static boolean validFilter(String filter){return List.of("all","optional","formal","milestone","unclassified").contains(filter);}
}
