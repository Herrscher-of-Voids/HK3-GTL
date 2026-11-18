package com.sirin.hk3gtl.common.research;

import com.sirin.hk3gtl.common.recipe.*;
import com.sirin.hk3gtl.common.machine.research.*;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.easter.Hk3EggProduction;
import com.sirin.hk3gtl.common.integration.Hk3QuestEvents;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import net.minecraft.nbt.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import java.util.*;

public final class Hk3ResearchRecipeRuntime {
    public static final String PLAN="hk3gtlExecutionPlan", MERGED="hk3gtlExecutionPlans";
    private static final String CIRCUIT_ANALYSIS="industrial_circuit_sample_analysis_";
    private static final Map<String,Hk3ResearchProcessPlans.Plan> PLANS=index();
    private Hk3ResearchRecipeRuntime() {}
    private static Map<String,Hk3ResearchProcessPlans.Plan> index(){
        Map<String,Hk3ResearchProcessPlans.Plan> map=new LinkedHashMap<>();
        Hk3ResearchProcessPlans.all().forEach(p->map.put(p.id(),p));return Map.copyOf(map);
    }
    public static CompoundTag snapshot(GTRecipe recipe){
        var out=Hk3ProcessReceipts.snapshot(recipe);out.putString(PLAN,recipe.data.getString(PLAN));return out;
    }
    public static boolean allowed(MetaMachine machine,GTRecipe recipe){
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
    private record Source(UUID owner,UUID team) {}
    private static Source source(MetaMachine machine){
        if(machine instanceof Hk3WorkableMultiblockMachine owned)return new Source(owned.getOwnerUUID(),owned.getResearchTeamUUID());
        if(!(machine.getHolder() instanceof BlockEntity holder)||!holder.getPersistentData().hasUUID(Hk3EggProduction.OWNER))return null;
        var owner=holder.getPersistentData().getUUID(Hk3EggProduction.OWNER);
        return new Source(owner,Hk3ResearchTeams.scope(machine.getLevel().getServer(),owner));
    }
    private static boolean allowed(MetaMachine machine,String id){
        var p=PLANS.get(id);if(p==null||!Hk3IndustrialExtensionPolicy.permits(p.role(),p.provisional())
                ||machine.getLevel()==null||machine.getLevel().getServer()==null)return false;
        var source=source(machine);if(source==null||source.owner()==null||source.team()==null)return false;
        // 2026-10-15：必须实际注册对应类型；切换界面当前模式不能改变固定工艺身份。
        if(!Arrays.asList(machine.getDefinition().getRecipeTypes()).contains(Hk3ResearchProcessTypes.get(p.role())))return false;
        var data=Hk3ResearchData.get(machine.getLevel().getServer());var scope=source.team();
        if(machine instanceof Hk3LiquidProcessMachine){
            if(machine instanceof Hk3HonkaiAbsorptionMachine){
                if(!Hk3IndustrialProcessRoles.acceptsCollectionRole(p.role(),machine.getDefinition().getRecipeTypes().length))return false;
            }else if(machine instanceof Hk3ResearchProcessMachine process){if(!p.role().equals(process.researchRole()))return false;}
            else if(!Set.of("I02","I03","I04","I05","I06","I07","I17","NETWORK_INJECTION").contains(p.role()))return false;
            if(machine instanceof Hk3SpectrumAnalysisMachine && !p.role().equals("I02"))return false;
            if(!Hk3ResearchExecutionContracts.permitsMachine(data,scope,p.role(),data.hasReviewPermission(scope,2)))return false;
        }else if(!p.role().startsWith("GT"))return false;
        if(!p.requirements().stream().allMatch(r->data.permits(scope,r)))return false;
        if(!p.requiredFacts().stream().allMatch(fact->data.hasProcessFact(scope,fact)))return false;
        if(!Hk3ResearchEvidenceAnalysis.ready(data,scope,p.id()))return false;
        if(p.id().startsWith(CIRCUIT_ANALYSIS)&&!data.hasCircuitTechnology(scope,p.id().substring(CIRCUIT_ANALYSIS.length())))return false;
        if(p.id().equals("wonder_cross_domain_validation")&&!java.util.stream.Stream.of("W09","W11","W13","W14")
                .allMatch(role->data.hasProcessFact(scope,"wonder_"+role)))return false;
        // 加强观测读取真实会面许可；基础QOM校准不能代替，资格/场景尚未接入时保持关闭。
        if(p.id().equals("industrial_enhanced_beacon_signal")&&!data.hasProcessFact(scope,"cocoon_authorization"))return false;
        return p.experiment().isBlank()||Hk3ResearchExecutionContracts.ready(data,scope,Hk3ResearchExecutionContracts.get(p.experiment()));
    }
    public static void settled(MetaMachine machine,GTRecipe recipe){
        if(!allowed(machine,recipe))return;
        if(recipe.data.contains(MERGED)){
            for(var raw:recipe.data.getList(MERGED,10))settled(machine,(CompoundTag)raw);
        }else if(!recipe.data.getString(PLAN).isBlank())settled(machine,snapshot(recipe));
    }
    private static void settled(MetaMachine machine,CompoundTag snapshot){
        var p=PLANS.get(snapshot.getString(PLAN));if(p==null)return;
        var level=machine.getLevel();var data=Hk3ResearchData.get(level.getServer());var source=source(machine);var scope=source.team();
        var receipt=Hk3ProcessReceipts.settle(snapshot,level.dimension().location()+"@"+machine.getPos(),level.getGameTime());
        if(!Hk3ResearchBatchProofs.valid(receipt))return;
        receipt.putUUID("Team",scope);receipt.putString("MachineRole",p.role());
        receipt.putString("Controller",machine.getDefinition().getId().toString());
        Hk3ResearchEvidenceAnalysis.settled(data,scope,p.id(),receipt);
        if(p.id().startsWith(CIRCUIT_ANALYSIS))data.recordCircuitAnalysis(scope,p.id().substring(CIRCUIT_ANALYSIS.length()));
        boolean accepted=false;
        for(String fact:p.facts()){
            boolean engineering=fact.startsWith("wonder_W")||fact.equals("hyperion_engineering")||fact.equals("wonder_application");
            boolean recorded=engineering?data.recordEngineeringFact(scope,fact,receipt):data.recordProcessFact(scope,fact,receipt);
            accepted|=recorded;
            if(recorded&&engineering){
                String role=fact.equals("hyperion_engineering")?"H01":fact.substring("wonder_".length());
                com.sirin.hk3gtl.common.narrative.story.Hk3StoryService.teamFact(level.getServer(),scope,"engineering_"+role);
            }
        }
        if(accepted)com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(level.getServer()).produced(source.owner(),"receipt:163",1);
        if(!p.experiment().isBlank())data.recordExperiment(scope,p.experiment(),receipt.getString("Facility")+"/"+receipt.getString("Recipe")+"/"+receipt.getUUID("Batch"));
        Hk3QuestEvents.recordProcess(level.getServer(),scope,p.id());
    }
}

