package com.sirin.hk3gtl.common.research;



import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.io.InputStreamReader;
import java.util.*;

 





 






public final class Hk3ResearchExecutionContracts {
    public record Contract(String id, String executor, String recipe, boolean existing,
            List<String> prerequisites, List<String> facts, List<String> unlocks,
            String precursor, int ticks, int energyTier, String source, String success) {
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
        Set<String> names=new HashSet<>();ALL.values().forEach(c -> names.addAll(c.facts()));
        for(int i=1;i<=15;i++)names.add(String.format(Locale.ROOT,"wonder_W%02d",i));
        names.add("wonder_application");names.add("hyperion_engineering");
        names.add("bounded_computation_result");names.add("lab_four_operation");
        names.add("contradictory_source_reports");names.add("contradiction_sample_retest");
        names.add("cross_machine_handoff");
        names.add("nano_coating");
        return Set.copyOf(names);
    }
    public static Set<String> factNames() { return FACTS; }
    public static boolean ready(Hk3ResearchData data, UUID scope, Contract c) {
        return c!=null && c.prerequisites().stream().allMatch(id -> data.completed(scope,id))
                && c.facts().stream().allMatch(id -> data.hasProcessFact(scope,id));
    }
    public static boolean permitsMachine(Hk3ResearchData data,UUID scope,String role,boolean secondReview) {
        if (role.equals("I01-1") || role.equals("I02") || role.equals("S01") || role.equals("NETWORK_INJECTION")) return true;
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
                        strings(o,"unlocks"),o.get("precursor").getAsString(),
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

 
