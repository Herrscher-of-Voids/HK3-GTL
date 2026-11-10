package com.sirin.hk3gtl.common.recipe;



import com.google.gson.*;
import java.util.*;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：暂定配方的强类型只读数值表。修改：加载时检查全部研究门槛。
 * 用途：游戏与交付数值表使用同一份JSON，不散落复制数值。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：验证暂定工艺的数据类型、研究条件、事实名称、实验契约和输入输出容量。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #3】2026-09-30 00:01:44（内测5修订102）
 * 删除：消耗并重造原图纸的路径。新增／修改：可选非消耗模板列表，旧配方默认空列表。
 * 用途：落实已确认的图纸成本，保留非消耗模板；新结构与物品来源交付另行接入。
 */
/**
 * 【变更记录 #4】2026-10-18 23:13:00（修订170）
 * - 删除：无；保留原有工艺字段与校验。
 * - 新增：Plan显式读取并暴露JSON的provisional状态，缺失或类型错误时拒绝加载。
 * - 修改：能源合同可以从同一工艺计划读取暂定状态，避免把草案误称为正式可执行设计。
 * - 用途：为I19-I22公共能源合同提供单一计划来源，并保留全系统配方草案状态。
 */
public final class Hk3ResearchProcessPlans {
    public record Item(String id,int count) {}
    public record Fluid(String id,int amount) {}
    public record Plan(String id,String role,List<String> requirements,List<Item> inputs,List<Item> outputs,
            List<Fluid> fluidInputs,List<Fluid> fluidOutputs,List<Item> catalysts,int ticks,int energyTier,
            String energyDirection,List<String> facts,String experiment,boolean provisional) {}
    private static final List<Plan> ALL=load();
    private Hk3ResearchProcessPlans() {}
    public static List<Plan> all(){return ALL;}
    private static List<String> strings(JsonObject o,String key){var out=new ArrayList<String>();o.getAsJsonArray(key).forEach(v->out.add(v.getAsString()));return List.copyOf(out);}
    private static List<Item> items(JsonObject o,String key){
        var out=new ArrayList<Item>();for(var raw:o.getAsJsonArray(key)){
            var v=raw.getAsJsonObject();int n=v.get("count").getAsInt();
            if(n<=0||n>64)throw new IllegalArgumentException("Invalid item amount");out.add(new Item(v.get("id").getAsString(),n));
        }return List.copyOf(out);
    }
    private static List<Fluid> fluids(JsonObject o,String key){
        var out=new ArrayList<Fluid>();for(var raw:o.getAsJsonArray(key)){
            var v=raw.getAsJsonObject();int n=v.get("amount").getAsInt();
            if(n<=0)throw new IllegalArgumentException("Invalid fluid amount");out.add(new Fluid(v.get("id").getAsString(),n));
        }return List.copyOf(out);
    }
    private static List<Plan> load(){
        try(var in=Hk3ResearchProcessPlans.class.getResourceAsStream("/data/hk3gtl/research/industrial_processes.json")){
            if(in==null)throw new IllegalStateException("Missing process plans");
            var root=JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonObject();
            if(root.get("schema").getAsInt()!=1)throw new IllegalArgumentException("Process schema");
            var all=new ArrayList<Plan>();Set<String> ids=new HashSet<>();
            for(var raw:root.getAsJsonArray("recipes")){
                var o=raw.getAsJsonObject();String role=o.get("role").getAsString();String energyDirection=o.get("energy_direction").getAsString();
                if(!o.has("provisional")||!o.get("provisional").isJsonPrimitive()||!o.getAsJsonPrimitive("provisional").isBoolean())
                    throw new IllegalArgumentException("Missing provisional status "+o.get("id").getAsString());
                var p=new Plan(o.get("id").getAsString(),role,strings(o,"requirements"),
                        items(o,"item_inputs"),items(o,"item_outputs"),fluids(o,"fluid_inputs"),fluids(o,"fluid_outputs"),o.has("item_catalysts")?items(o,"item_catalysts"):List.of(),
                        o.get("ticks").getAsInt(),o.get("energy_tier").getAsInt(),energyDirection,strings(o,"facts"),o.get("experiment").getAsString(),o.get("provisional").getAsBoolean());
                int ratedTier=Hk3ResearchProcessEnergy.ratedVoltageTier(role);
                if(!ids.add(p.id())||p.ticks()<=0||p.energyTier()<14||p.energyTier()>30
                        ||p.inputs().isEmpty()&&p.fluidInputs().isEmpty()
                        ||!energyDirection.equals("input")&&!energyDirection.equals("output")
                        ||Hk3ResearchProcessEnergy.isGenerator(role)!=energyDirection.equals("output")
                        ||ratedTier>0&&p.energyTier()>ratedTier)
                    throw new IllegalArgumentException("Invalid process "+p.id());
                for(String id:p.requirements())if(Hk3ResearchCatalog.bundled().get(id)==null)throw new IllegalArgumentException("Unknown process prerequisite "+id);
                for(String fact:p.facts())if(!com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts.factNames().contains(fact))
                    throw new IllegalArgumentException("Unknown production fact "+fact);
                if(!p.experiment().isBlank()){
                    var contract=com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts.get(p.experiment());
                    if(contract==null||!contract.executor().equals(p.role())||!contract.recipe().equals(p.id())
                            ||!p.requirements().containsAll(contract.prerequisites()))
                        throw new IllegalArgumentException("Experiment does not match contract "+p.id());
                }
                Hk3ResearchProcessPorts.validate(p);all.add(p);
            }return List.copyOf(all);
        }catch(Exception e){throw new IllegalStateException("Invalid process plans",e);}
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
