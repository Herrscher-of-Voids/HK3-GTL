package com.sirin.hk3gtl.common.research;



import com.sirin.hk3gtl.common.recipe.*;
import com.sirin.hk3gtl.common.machine.research.*;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import net.minecraft.nbt.*;
import java.util.*;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：全部暂定工艺的服务端验证及真实输出结算。
 * 修改：合并配方保留每项来源和实际执行收支；用途：满输出、模拟或扣料失败不发证据。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：核对设备类型、工艺身份和全部证据，实际输出成功才记录实验，缺少真实事实时保持锁定。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/** 【变更记录 #3】2026-09-30 20:28:36（修订117）：删除无；新增：奇观运行访问读取本队二审许可并仍核验对应研究；修改许可读取/结算守卫；用途：分开审查与研究，防预览或关闭误授予。 */
/** 【变更记录 #4】2026-10-01 04:58:34（修订128）：删除：旧固定上限或被替代的分支；新增/修改：正式研究证据确被接收后记录实际设备归属的可选旁注，重复证据和无归属不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #5】2026-10-15 01:12:48（修订156）：按真实注册类型及固定工业身份校验，采集塔仅可执行本阶与前阶工艺；其他研究检查保持。 */
/**
 * 【变更记录 #6】2026-10-23 13:35:32（第6次备注 · 内测5修订175）
 * - 删除：新批准I14/I15/I16/I18按结构批准直接执行暂定工艺的可能路径。
 * - 新增：同源计划provisional定向守卫，单配方与合并批次共同检查。
 * - 修改：仅非暂定计划可继续原类型、固定职责、研究、实验和实际输出校验。
 * - 用途：隔离外观/结构批准与工艺批准；既有I17真实MAX配方和数值不变。
 */
public final class Hk3ResearchRecipeRuntime {
    public static final String PLAN="hk3gtlExecutionPlan", MERGED="hk3gtlExecutionPlans";
    private static final Map<String,Hk3ResearchProcessPlans.Plan> PLANS=index();
    private Hk3ResearchRecipeRuntime() {}
    private static Map<String,Hk3ResearchProcessPlans.Plan> index(){
        Map<String,Hk3ResearchProcessPlans.Plan> map=new LinkedHashMap<>();
        Hk3ResearchProcessPlans.all().forEach(p->map.put(p.id(),p));return Map.copyOf(map);
    }
    public static CompoundTag snapshot(GTRecipe recipe){
        var out=Hk3ProcessReceipts.snapshot(recipe);out.putString(PLAN,recipe.data.getString(PLAN));return out;
    }
    public static boolean allowed(Hk3LiquidProcessMachine machine,GTRecipe recipe){
        if(recipe.data.contains(MERGED)){
            if(!recipe.data.contains(MERGED,Tag.TAG_LIST))return false;
            var entries=recipe.data.getList(MERGED,Tag.TAG_COMPOUND);
            if(entries.size()!=((ListTag)recipe.data.get(MERGED)).size())return false;
            if(entries.isEmpty()&&(!recipe.data.getString(PLAN).isBlank()||knownRecipe(recipe)))return false;
            for(var raw:entries){
                var entry=(CompoundTag)raw;var p=PLANS.get(entry.getString(PLAN));
                if(!matches(p,entry.getString("Recipe"))||!allowed(machine,entry.getString(PLAN)))return false;
            }
            return true;
        }
        String id=recipe.data.getString(PLAN);
        if(id.isBlank()){
            String path=recipe.id.getPath();String name=path.substring(path.lastIndexOf('/')+1);
            return !PLANS.containsKey(name);
        }
        return matches(PLANS.get(id),recipe.id.toString())&&allowed(machine,id);
    }
    private static boolean knownRecipe(GTRecipe recipe){
        String path=recipe.id.getPath();return PLANS.containsKey(path.substring(path.lastIndexOf('/')+1));
    }
    private static boolean matches(Hk3ResearchProcessPlans.Plan plan,String recipe){
        if(plan==null)return false;
        String path=Hk3ResearchProcessTypes.get(plan.role()).registryName.getPath()+"/"+plan.id();
        return recipe.equals("hk3gtl:"+path)||recipe.equals("gtceu:"+path);
    }
    private static boolean allowed(Hk3LiquidProcessMachine machine,String id){
        var p=PLANS.get(id);if(p==null||!Hk3IndustrialExtensionPolicy.permits(p.role(),p.provisional())
                ||machine.getLevel()==null||machine.getLevel().getServer()==null||machine.getResearchTeamUUID()==null)return false;
        // 2026-10-15：必须实际注册对应类型；切换界面当前模式不能改变固定工艺身份。
        if(!Arrays.asList(machine.getDefinition().getRecipeTypes()).contains(Hk3ResearchProcessTypes.get(p.role())))return false;
        if(machine instanceof Hk3HonkaiAbsorptionMachine){
            if(!Hk3IndustrialProcessRoles.acceptsCollectionRole(p.role(),machine.getDefinition().getRecipeTypes().length))return false;
        }else if(machine instanceof Hk3ResearchProcessMachine process){if(!p.role().equals(process.researchRole()))return false;}
        else if(!Set.of("I02","I03","I04","I05","I06","I07","I17").contains(p.role()))return false;
        // 既有I02与I05还需核对真实配方类型，不能用元数据改换设备职责。
        if(machine instanceof Hk3SpectrumAnalysisMachine && !p.role().equals("I02"))return false;
        var data=Hk3ResearchData.get(machine.getLevel().getServer());var scope=machine.getResearchTeamUUID();
        if(!Hk3ResearchExecutionContracts.permitsMachine(data,scope,p.role(),data.hasReviewPermission(scope,2)))return false;
        if(!p.requirements().stream().allMatch(r->data.completed(scope,r)))return false;
        // 加强观测读取真实会面许可；基础QOM校准不能代替，资格/场景尚未接入时保持关闭。
        if(p.id().equals("industrial_enhanced_beacon_signal")&&!data.hasProcessFact(scope,"cocoon_authorization"))return false;
        return p.experiment().isBlank()||Hk3ResearchExecutionContracts.ready(data,scope,Hk3ResearchExecutionContracts.get(p.experiment()));
    }
    public static void settled(Hk3LiquidProcessMachine machine,GTRecipe recipe){
        if(!allowed(machine,recipe))return;
        if(recipe.data.contains(MERGED)){
            for(var raw:recipe.data.getList(MERGED,10))settled(machine,(CompoundTag)raw);
        }else if(!recipe.data.getString(PLAN).isBlank())settled(machine,snapshot(recipe));
    }
    private static void settled(Hk3LiquidProcessMachine machine,CompoundTag snapshot){
        var p=PLANS.get(snapshot.getString(PLAN));if(p==null)return;
        var level=machine.getLevel();var data=Hk3ResearchData.get(level.getServer());var scope=machine.getResearchTeamUUID();
        var receipt=Hk3ProcessReceipts.settle(snapshot,level.dimension().location()+"@"+machine.getPos(),level.getGameTime());
        if(!Hk3ResearchBatchProofs.valid(receipt))return;
        boolean accepted=false;for(String fact:p.facts())accepted|=data.recordProcessFact(scope,fact,receipt);
        if(accepted&&machine.getOwnerUUID()!=null)com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(level.getServer()).produced(machine.getOwnerUUID(),"receipt:163",1);
        if(!p.experiment().isBlank())data.recordExperiment(scope,p.experiment(),receipt.getString("Facility")+"/"+receipt.getString("Recipe")+"/"+receipt.getUUID("Batch"));
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
