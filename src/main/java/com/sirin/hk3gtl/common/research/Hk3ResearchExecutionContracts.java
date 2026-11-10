package com.sirin.hk3gtl.common.research;



import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.io.InputStreamReader;
import java.util.*;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：100课题执行来源、全部前置、真实工况及解锁对象。
 * 修改：实验与研究权限分离；用途：启动即拒绝漏题、自锁和重复机型授权。
 * 本表与物理机器注册独立；定义工艺不等于批准结构或通过游戏验收。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：载入100题批准来源、真实工况、前置及解锁对象，拒绝漏题与目录内自锁。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public final class Hk3ResearchExecutionContracts {
    public record Contract(String id, String executor, String recipe, boolean existing,
            List<String> prerequisites, List<String> facts, List<String> unlocks,
            String specimen, String precursor, int ticks, int energyTier, String source, String success) {
        public Contract {
            prerequisites=List.copyOf(prerequisites);facts=List.copyOf(facts);unlocks=List.copyOf(unlocks);
        }
    }
    private static final Map<String,Contract> ALL=load();
    private static final Set<String> FACTS=collectFacts();
    private Hk3ResearchExecutionContracts() {}
    public static Map<String,Contract> all() { return ALL; }
    public static Contract get(String id) { return ALL.get(id); }
    private static Set<String> collectFacts() {
        Set<String> names=new HashSet<>();ALL.values().forEach(c -> names.addAll(c.facts()));return Set.copyOf(names);
    }
    public static Set<String> factNames() { return FACTS; }
    public static boolean ready(Hk3ResearchData data, UUID scope, Contract c) {
        return c!=null && c.prerequisites().stream().allMatch(id -> data.completed(scope,id))
                && c.facts().stream().allMatch(id -> data.hasProcessFact(scope,id));
    }
    public static boolean permitsMachine(Hk3ResearchData data,UUID scope,String role,boolean secondReview) {
        if (role.equals("I01-1") || role.equals("I02") || role.equals("S01")) return true;
        if (role.startsWith("W") && !secondReview) return false;
        for (var c:ALL.values()) if(c.unlocks().contains(role))return data.completed(scope,c.id());
        return false;
    }
    private static List<String> strings(JsonObject o,String key) {
        List<String> values=new ArrayList<>();for(var v:o.getAsJsonArray(key))values.add(v.getAsString());
        if(new HashSet<>(values).size()!=values.size())throw new IllegalArgumentException("Duplicate "+key);
        return values;
    }
    private static Map<String,Contract> load() {
        try(var in=Hk3ResearchExecutionContracts.class.getResourceAsStream("/data/hk3gtl/research/research_execution.json")) {
            if(in==null)throw new IllegalStateException("Missing execution contracts");
            var root=JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonObject();
            if(root.get("schema").getAsInt()!=1)throw new IllegalArgumentException("Execution schema");
            Map<String,Contract> result=new LinkedHashMap<>();Set<String> roles=new HashSet<>();
            for(var raw:root.getAsJsonArray("topics")) {
                var o=raw.getAsJsonObject();var c=new Contract(o.get("id").getAsString(),o.get("executor").getAsString(),
                        o.get("recipe").getAsString(),o.get("existing").getAsBoolean(),strings(o,"prerequisites"),strings(o,"facts"),
                        strings(o,"unlocks"),o.get("specimen").getAsString(),o.get("precursor").getAsString(),
                        o.get("ticks").getAsInt(),o.get("energy_tier").getAsInt(),o.get("source").getAsString(),o.get("success").getAsString());
                if(Hk3ResearchCatalog.bundled().get(c.id())==null || result.putIfAbsent(c.id(),c)!=null
                        || c.ticks()<=0 || c.energyTier()<14 || c.energyTier()>30)throw new IllegalArgumentException("Invalid contract "+c.id());
                for(String parent:c.prerequisites())if(requires(parent,c.id(),new HashSet<>()))throw new IllegalArgumentException("Self-lock "+c.id()+" via "+parent);
                for(String role:c.unlocks())if(!roles.add(role))throw new IllegalArgumentException("Duplicate machine unlock "+role);
            }
            if(!result.keySet().equals(Hk3ResearchCatalog.bundled().topics().keySet()))throw new IllegalArgumentException("Incomplete execution contracts");
            return Collections.unmodifiableMap(result);
        } catch(Exception e) { throw new IllegalStateException("Invalid research execution contracts",e); }
    }
    private static boolean requires(String id,String target,Set<String> seen) {
        if(id.equals(target))return true;if(!seen.add(id))return false;
        var c=Hk3ResearchCatalog.bundled().get(id);if(c==null)throw new IllegalArgumentException("Unknown prerequisite "+id);
        return c.prerequisites().stream().anyMatch(p -> requires(p,target,seen));
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
