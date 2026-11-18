package com.sirin.hk3gtl.common.recipe;

import com.google.gson.*;
import java.util.*;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public final class Hk3ResearchProcessPlans {
    public record Item(String id,int count) {}
    public record Fluid(String id,int amount) {}
    public record ChancedItem(Item item,int chance,int tierChanceBoost) {}
    public record Plan(String id,String role,List<String> requirements,List<Item> inputs,List<Item> outputs,
            List<Fluid> fluidInputs,List<Fluid> fluidOutputs,List<Item> catalysts,int ticks,int energyTier,
            String energyDirection,List<String> facts,String experiment,boolean provisional,long networkCredit,long outputEut,int circuit,
            List<ChancedItem> chancedOutputs,long inputEut,long inputHw,List<String> requiredFacts) {}
    private static final List<Plan> ALL=load();
    private Hk3ResearchProcessPlans() {}
    public static List<Plan> all(){return ALL;}
    private static List<String> strings(JsonObject o,String key){var out=new ArrayList<String>();o.getAsJsonArray(key).forEach(v->out.add(v.getAsString()));return List.copyOf(out);}
    private static List<Item> items(JsonObject o,String key){
        var out=new ArrayList<Item>();for(var raw:o.getAsJsonArray(key)){
            var v=raw.getAsJsonObject();int n=v.get("count").getAsInt();
            if(n<=0)throw new IllegalArgumentException("Invalid item amount");out.add(new Item(v.get("id").getAsString(),n));
        }return List.copyOf(out);
    }
    private static List<Fluid> fluids(JsonObject o,String key){
        var out=new ArrayList<Fluid>();for(var raw:o.getAsJsonArray(key)){
            var v=raw.getAsJsonObject();int n=v.get("amount").getAsInt();
            if(n<=0)throw new IllegalArgumentException("Invalid fluid amount");out.add(new Fluid(v.get("id").getAsString(),n));
        }return List.copyOf(out);
    }
    private static List<ChancedItem> chancedItems(JsonObject o,String key){
        var out=new ArrayList<ChancedItem>();for(var raw:o.getAsJsonArray(key)){
            var v=raw.getAsJsonObject();
            out.add(new ChancedItem(new Item(v.get("id").getAsString(),v.get("count").getAsInt()),
                    v.get("chance").getAsInt(),v.get("tier_chance_boost").getAsInt()));
        }return List.copyOf(out);
    }
    private static List<Plan> load(){
        try(var in=Hk3ResearchProcessPlans.class.getResourceAsStream("/data/hk3gtl/research/industrial_processes.json");
            var wonders=Hk3ResearchProcessPlans.class.getResourceAsStream("/data/hk3gtl/research/wonder_processes.json")){
            if(in==null)throw new IllegalStateException("Missing process plans");
            var root=JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonObject();
            if(root.get("schema").getAsInt()!=1)throw new IllegalArgumentException("Process schema");
            root.getAsJsonArray("recipes").addAll(JsonParser.parseReader(new InputStreamReader(wonders,StandardCharsets.UTF_8)).getAsJsonObject().getAsJsonArray("recipes"));
            var groups = new ArrayList<>(List.of("wonder_w01_w05", "wonder_w06_w10", "wonder_w11_w15"));
            for (int i = 1; i <= 15; i++) groups.add(String.format(Locale.ROOT, "wonder_expansion_w%02d", i));
            for (String group : groups) {
                try (var processes = Hk3ResearchProcessPlans.class.getResourceAsStream(
                        "/data/hk3gtl/research/" + group + "_processes.json")) {
                    root.getAsJsonArray("recipes").addAll(JsonParser.parseReader(
                            new InputStreamReader(processes, StandardCharsets.UTF_8)).getAsJsonObject().getAsJsonArray("recipes"));
                }
            }
            try (var fuels = Hk3ResearchProcessPlans.class.getResourceAsStream("/data/hk3gtl/research/reactor_fuel_processes.json")) {
                root.getAsJsonArray("recipes").addAll(JsonParser.parseReader(new InputStreamReader(fuels, StandardCharsets.UTF_8))
                        .getAsJsonObject().getAsJsonArray("recipes"));
            }
            var all=new ArrayList<Plan>();Set<String> ids=new HashSet<>();
            for(var raw:Hk3ApprovedIndustrialPlans.merge(root.getAsJsonArray("recipes"))){
                var o=raw.getAsJsonObject();String role=o.get("role").getAsString();String energyDirection=o.get("energy_direction").getAsString();
                if(!o.has("provisional")||!o.get("provisional").isJsonPrimitive()||!o.getAsJsonPrimitive("provisional").isBoolean())
                    throw new IllegalArgumentException("Missing provisional status "+o.get("id").getAsString());
                var p=new Plan(o.get("id").getAsString(),role,strings(o,"requirements"),
                        items(o,"item_inputs"),items(o,"item_outputs"),fluids(o,"fluid_inputs"),fluids(o,"fluid_outputs"),o.has("item_catalysts")?items(o,"item_catalysts"):List.of(),
                        o.get("ticks").getAsInt(),o.get("energy_tier").getAsInt(),energyDirection,strings(o,"facts"),o.get("experiment").getAsString(),o.get("provisional").getAsBoolean(),o.has("network_credit")?o.get("network_credit").getAsLong():0,
                        energyDirection.equals("output") ? o.has("output_eut") ? o.get("output_eut").getAsLong()
                                : com.sirin.hk3gtl.common.constants.Hk3Values.VA_LONG[o.get("energy_tier").getAsInt()] : 0,
                        o.has("circuit") ? o.get("circuit").getAsInt() : 0,
                        o.has("chanced_item_outputs") ? chancedItems(o,"chanced_item_outputs") : List.of(),
                        o.has("input_eut") ? o.get("input_eut").getAsLong() : 0,
                        o.has("input_hw") ? o.get("input_hw").getAsLong() : -1,
                        o.has("required_facts") ? strings(o,"required_facts") : List.of());
                if(!ids.add(p.id())||p.ticks()<=0||p.energyTier()<14||p.energyTier()>30
                        ||p.inputs().isEmpty()&&p.fluidInputs().isEmpty()
                        ||!energyDirection.equals("input")&&!energyDirection.equals("output")
                        ||Hk3ResearchProcessEnergy.isGenerator(role)!=energyDirection.equals("output")
                        ||energyDirection.equals("output")&&(p.outputEut()<=0
                            ||p.outputEut()>com.sirin.hk3gtl.common.constants.Hk3Values.VA_LONG[p.energyTier()]))
                    throw new IllegalArgumentException("Invalid process "+p.id());
                for(String id:p.requirements())if(!com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.isCurrentResearchId(id))throw new IllegalArgumentException("Unknown process prerequisite "+id);
                for(String fact:p.facts())if(!com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts.factNames().contains(fact))
                    throw new IllegalArgumentException("Unknown production fact "+fact);
                if(!p.experiment().isBlank()){
                    var contract=com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts.get(p.experiment());
                    if(contract==null||!contract.executor().equals(p.role())||!contract.recipe().equals(p.id())
                            ||!p.requirements().containsAll(contract.prerequisites()))
                        throw new IllegalArgumentException("Experiment does not match contract "+p.id());
                }
                Hk3ResearchProcessPorts.validate(p);all.add(p);
            }return com.sirin.hk3gtl.common.recipe.honkai.Hk3FuelBundlePlans.expand(all);
        }catch(Exception e){throw new IllegalStateException("Invalid process plans",e);}
    }
}
