package com.sirin.hk3gtl.common.registration;

import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.ingredient.IntCircuitIngredient;
import com.gregtechceu.gtceu.api.registry.GTRegistries;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.multiblock.build.Hk3BuildPlans;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ArchitectureMaterials;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes;
import com.sirin.hk3gtl.common.recipe.audit.RecipeReachability;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.ShapedRecipe;
import net.minecraft.world.item.crafting.ShapelessRecipe;
import net.minecraft.world.level.material.FlowingFluid;
import java.util.*;

/**
 * 从整包最终注册表构造工业依赖图；只读，不授予研究、事实或物品。
 */
public final class Hk3IndustrialDependencyAudit {
    private Hk3IndustrialDependencyAudit() {}

    public record Snapshot(int registeredRecipes, Set<String> productionRecipes,
            RecipeReachability.Result result, List<String> unresolvedViews) {}

    /** 服务器完成配方和标签加载后调用，所有注册表读取均留在服务器线程。 */
    public static Snapshot inspect(MinecraftServer server) {
        Set<String> internalFluids = new HashSet<>();
        Hk3IndustrialFluids.materials().values().forEach(m -> internalFluids.add(fluidId(m.getFluid())));
        internalFluids.add(fluidId(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid()));
        internalFluids.add(fluidId(SouliumMaterial.SOULIUM.getFluid()));
        var seedItems = new HashSet<String>();
        BuiltInRegistries.ITEM.keySet().stream().filter(id -> !internalItem(id)).map(Object::toString).forEach(seedItems::add);
        var seedFluids = new HashSet<String>();
        BuiltInRegistries.FLUID.keySet().forEach(id -> {
            String canonical = fluidId(BuiltInRegistries.FLUID.get(id));
            if (!id.getNamespace().equals("hk3gtl") && !internalFluids.contains(canonical)) seedFluids.add(canonical);
        });
        // 真实注册定义提供设备类型，不以规划清单或配方类型注册冒充已存在的控制器。
        var deviceRules = new ArrayList<RecipeReachability.Recipe>();
        var unresolved = new ArrayList<String>();
        for (var definition : GTRegistries.MACHINES) {
            String item = BuiltInRegistries.ITEM.getKey(definition.asStack().getItem()).toString();
            if (definition.asStack().isEmpty()) continue;
            var recipeTypes = definition.getRecipeTypes();
            if (recipeTypes == null) continue;
            var inputs = deviceInputs(definition.getId().toString(), item, unresolved);
            for (var type : new LinkedHashSet<>(Arrays.asList(recipeTypes))) {
                if (type == null) continue;
                String capability = "executor:" + type.registryName;
                deviceRules.add(new RecipeReachability.Recipe("device:" + definition.getId() + "/" + type.registryName,
                        inputs, List.of(), Set.of(), "", Set.of(),
                        Set.of(capability), Set.of(), Set.of(), Set.of()));
            }
        }
        for (int lab = 1; lab <= 5; lab++) {
            var institute = com.sirin.hk3gtl.common.machine.research.Hk3ResearchMachines.institute(lab);
            if (institute == null || institute.asStack().isEmpty()) continue;
            String role = "S0" + lab;
            var permission = new TreeSet<String>();
            if (lab > 1) Hk3ResearchExecutionContracts.all().values().stream()
                    .filter(c -> c.unlocks().contains(role)).findFirst().ifPresentOrElse(
                            c -> permission.add(c.id()), () -> permission.add("unassigned_machine_permission:" + role));
            deviceRules.add(new RecipeReachability.Recipe("facility:" + role,
                    deviceInputs(institute.getId().toString(), BuiltInRegistries.ITEM.getKey(institute.asStack().getItem()).toString(), unresolved), List.of(),
                    permission, "", Set.of(), Set.of("laboratory_ready:" + lab), Set.of(), Set.of(), Set.of()));
        }
        var plans = new HashMap<String, Hk3ResearchProcessPlans.Plan>();
        Hk3ResearchProcessPlans.all().forEach(p -> plans.put(p.id(), p));
        var recipes = new ArrayList<RecipeReachability.Recipe>();
        var productionIds = new TreeSet<String>();
        var registered = server.getRecipeManager().getRecipes();
        for (var raw : registered) {
            if (!(raw instanceof GTRecipe gt)) {
                if (raw instanceof ShapedRecipe || raw instanceof ShapelessRecipe) {
                    var output = raw.getResultItem(server.registryAccess());
                    var id = BuiltInRegistries.ITEM.getKey(output.getItem());
                    if (!output.isEmpty() && (raw.getId().getNamespace().equals("hk3gtl") || internalItem(id))) {
                        var inputs = new ArrayList<Set<String>>();
                        for (var ingredient : raw.getIngredients()) if (!ingredient.isEmpty()) inputs.add(itemIds(ingredient.getItems()));
                        productionIds.add(raw.getId().toString());
                        recipes.add(new RecipeReachability.Recipe(raw.getId().toString(), inputs, List.of(),
                                new HashSet<>(Hk3RecipeResearchGate.getAllRequiredResearch(raw.getId())), "", Set.of(),
                                Set.of(id.toString()), Set.of(), Set.of(), Set.of()));
                    }
                    continue;
                }
                // 非GT自定义配方的通用ingredients视图可能遗漏约束，记录而不自动放行。
                if (raw.getId().getNamespace().equals("hk3gtl"))
                    unresolved.add(raw.getId() + "：非GT配方需单独核验约束");
                continue;
            }
            var itemOut = itemOutputs(gt);
            var fluidOut = fluidOutputs(gt);
            boolean owned = gt.id.getNamespace().equals("hk3gtl")
                    || gt.id.getPath().contains("/hk3gtl_") || gt.id.getPath().contains("/industrial_");
            if (!owned && itemOut.stream().noneMatch(id -> internalItem(new ResourceLocation(id)))
                    && fluidOut.stream().noneMatch(internalFluids::contains)) continue;
            try { validate(gt); }
            catch (IllegalStateException error) { unresolved.add(error.getMessage()); continue; }
            productionIds.add(gt.id.toString());
            var gates = new TreeSet<>(Hk3RecipeResearchGate.getAllRequiredResearch(gt.id));
            var facts = new TreeSet<String>();
            var factOutputs = new TreeSet<String>();
            var evidence = new TreeSet<String>();
            String circuitManufacturing = "assembler/hk3gtl_functional_honkai_circuit_";
            if(gt.id.getPath().startsWith(circuitManufacturing))
                factOutputs.add("circuit_technology:"+gt.id.getPath().substring(circuitManufacturing.length()));
            String recovery=Hk3ProcessReceipts.category(gt);
            if(!recovery.isBlank())factOutputs.add("recovery:"+recovery);
            String oldExperiment = gt.data.getString(Hk3LiquidProcessMachine.EXPERIMENT);
            if (!oldExperiment.isBlank()) evidence.add(oldExperiment);
            String planId = gt.data.getString(Hk3ResearchRecipeRuntime.PLAN);
            if (!planId.isBlank()) {
                var plan = plans.get(planId);
                if (plan == null) {
                    facts.add("invalid_execution_plan:" + planId);
                } else {
                    if (!Hk3IndustrialExtensionPolicy.permits(plan.role(), plan.provisional()))
                        facts.add("provisional_process_locked:" + plan.id());
                    String expectedPath = Hk3ResearchProcessTypes.of(plan).registryName.getPath() + "/" + plan.id();
                    if (!gt.id.getPath().equals(expectedPath) || !(gt.id.getNamespace().equals("gtceu") || gt.id.getNamespace().equals("hk3gtl"))
                            || gt.recipeType != Hk3ResearchProcessTypes.of(plan)) facts.add("invalid_plan_recipe_binding:" + planId);
                    gates.addAll(plan.requirements());
                    factOutputs.addAll(plan.facts());
                    String circuitAnalysis="industrial_circuit_sample_analysis_";
                    if(plan.id().startsWith(circuitAnalysis)) {
                        String tier=plan.id().substring(circuitAnalysis.length());
                        facts.add("circuit_technology:"+tier);factOutputs.add("circuit_analysis:"+tier);
                    }
                    if (!plan.experiment().isBlank()) {
                        evidence.add(plan.experiment());
                        var contract = Hk3ResearchExecutionContracts.get(plan.experiment());
                        gates.addAll(contract.prerequisites());
                        facts.addAll(contract.facts());
                    }
                    if (!Set.of("I01-1", "I02", "S01").contains(plan.role())) {
                        var permission = Hk3ResearchExecutionContracts.all().values().stream()
                                .filter(c -> c.unlocks().contains(plan.role())).findFirst();
                        if (permission.isPresent()) gates.add(permission.get().id());
                        else facts.add("unassigned_machine_permission:" + plan.role());
                    }
                    if (plan.role().startsWith("W")) facts.add("external_ledger:second_review_permission");
                    if (plan.id().equals("industrial_enhanced_beacon_signal")) facts.add("cocoon_authorization");
                }
            }
            if (gt.id.equals(com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine.SAMPLING)) evidence.add("RN-HED");
            if (gt.id.getPath().endsWith("/industrial_initial_spectrum")) evidence.add("RN-HSA");
            recipes.add(new RecipeReachability.Recipe(gt.id.toString(), itemInputs(gt), fluidInputs(gt),
                    gates, "executor:" + gt.recipeType.registryName, facts,
                    itemOut, fluidOut, factOutputs, evidence));
        }
        recipes.addAll(deviceRules);
        addLaboratoryExperiments(recipes);
        var topics = new ArrayList<RecipeReachability.Research>();
        for(String tier:Hk3ResearchData.CIRCUIT_TIERS)
            topics.add(new RecipeReachability.Research(Hk3ResearchData.CIRCUIT_PREFIX+tier,
                    Set.of(Hk3ResearchData.CORE_RESEARCH),Set.of(),
                    Set.of("circuit_technology:"+tier,"circuit_analysis:"+tier),List.of(),List.of()));
        for (var topic : Hk3ResearchCatalog.bundled().topics().values()) {
            var contract = Hk3ResearchExecutionContracts.get(topic.id());
            var parents = new TreeSet<>(topic.prerequisites());
            parents.addAll(contract.prerequisites());
            var costs = new ArrayList<Set<String>>();
            for (var cost : Hk3ResearchPlans.get(topic.id()).materials()) {
                var ingredient = Ingredient.of(TagKey.create(Registries.ITEM, new ResourceLocation(cost.tag())));
                costs.add(itemIds(ingredient.getItems()));
            }
            costs.add(institutes(topic.lab()));
            topics.add(new RecipeReachability.Research(topic.id(), parents, Set.of(topic.id()),
                    Set.copyOf(contract.facts()), costs, List.of()));
        }
        var result = RecipeReachability.analyze(recipes, topics,
                new RecipeReachability.Seeds(seedItems, seedFluids, Set.of(), Set.of(), Set.of()));
        return new Snapshot(registered.size(), Collections.unmodifiableSet(productionIds), result, List.copyOf(unresolved));
    }

    private static List<Set<String>> deviceInputs(String machine, String item, List<String> unresolved) {
        var inputs = new ArrayList<Set<String>>();
        inputs.add(Set.of(item));
        String layout = Hk3BuildPlans.layoutForMachine(machine);
        if (layout == null) {
            if (machine.startsWith("hk3gtl:")) unresolved.add(machine + "：未映射批准建筑，结构建材可达性未核验");
            return inputs;
        }
        for (String state : Hk3ArchitectureMaterials.states(layout)) {
            var material = BuiltInRegistries.BLOCK.get(new ResourceLocation(state.split("\\[", 2)[0])).asItem();
            if (material == Items.AIR) {
                inputs.add(Set.of());
                unresolved.add(layout + "：固定材料不能映射为物品，阻断设备可达性：" + state);
            } else inputs.add(Set.of(BuiltInRegistries.ITEM.getKey(material).toString()));
        }
        return inputs;
    }

    /** 空标签、无效数量与超出配方类型接口上限均属于错误。 */
    private static void validate(GTRecipe recipe) {
        require(recipe.duration>0,"工时无效："+recipe.id);
        for(var cap:List.of(ItemRecipeCapability.CAP,FluidRecipeCapability.CAP)) {
            require(recipe.getInputContents(cap).size()<=recipe.recipeType.getMaxInputs(cap),"输入超限："+recipe.id);
            require(recipe.getOutputContents(cap).size()<=recipe.recipeType.getMaxOutputs(cap),"输出超限："+recipe.id);
        }
        for(var map:List.of(recipe.inputs,recipe.outputs)) {
            for(var content:map.getOrDefault(ItemRecipeCapability.CAP,List.of())) {
                var stacks=ItemRecipeCapability.CAP.of(content.content).getItems();
                require(stacks.length>0&&Arrays.stream(stacks).allMatch(s -> !s.isEmpty()),"空物品/标签："+recipe.id);
            }
            for(var content:map.getOrDefault(FluidRecipeCapability.CAP,List.of())) {
                var stacks=FluidRecipeCapability.CAP.of(content.content).getStacks();
                require(stacks.length>0&&Arrays.stream(stacks).allMatch(s -> !s.isEmpty()&&s.getAmount()>0),"空流体/标签："+recipe.id);
            }
        }
    }
    private static void require(boolean valid,String message) { if(!valid)throw new IllegalStateException(message); }

    private static boolean internalItem(ResourceLocation id) {
        return id.getNamespace().equals("hk3gtl") || id.getPath().contains("soulium");
    }
    private static Set<String> institutes(int requiredLab) {
        var ids = new TreeSet<String>();
        for (int lab = requiredLab; lab <= 5; lab++) {
            var institute = com.sirin.hk3gtl.common.machine.research.Hk3ResearchMachines.institute(lab);
            if (institute != null && !institute.asStack().isEmpty()) ids.add("laboratory_ready:" + lab);
        }
        return ids;
    }
    /** 固定研究所实验不属于生产配方，按真实服务的耗材与凭据条件建图，不免费授予证据。 */
    private static void addLaboratoryExperiments(List<RecipeReachability.Recipe> recipes) {
        for (String id : List.of("LAB-ALE", "LAB-OPR", "LAB-ERM-BASE", "LAB-ERM-AID")) {
            var spec = Hk3LabExperimentRules.get(id);
            var needs = new ArrayList<Set<String>>();
            needs.add(institutes(spec.lab()));
            var facts = new TreeSet<String>();
            var evidenceInputs = new TreeSet<String>();
            var evidenceOutputs = new TreeSet<String>();
            needs.add(Set.of("minecraft:paper"));
            if (id.equals("LAB-ALE")) {
                needs.add(tagItems("forge:plates/soulium"));
                needs.add(tagItems("forge:fine_wires/soulium"));
                needs.add(Set.of("hk3gtl:etched_circuit_layer"));
                needs.add(Set.of(BuiltInRegistries.ITEM.getKey(org.gtlcore.gtlcore.common.data.GTLItems.SENSOR_MAX.asItem()).toString()));
                evidenceOutputs.add(spec.research());
            } else if (id.equals("LAB-OPR")) {
                Hk3ResearchBatchProofs.RECOVERY.forEach(category->facts.add("recovery:"+category));
                evidenceOutputs.add(spec.research());
            } else {
                needs.add(tagItems("gtceu:circuits/max"));
                if (spec.baseline()) evidenceOutputs.add("LAB-ERM-BASE");
                else {
                    needs.add(Set.of("hk3gtl:imitation_corruption_core"));
                    evidenceInputs.add("LAB-ERM-BASE");
                    evidenceOutputs.add(spec.research());
                }
            }
            var topic = Hk3ResearchCatalog.bundled().get(spec.research());
            recipes.add(new RecipeReachability.Recipe("laboratory:" + id, needs, List.of(),
                    new HashSet<>(topic.prerequisites()), "", facts, evidenceInputs,
                    Set.of(), Set.of(), Set.of(), evidenceOutputs));
        }
    }
    private static Set<String> tagItems(String tag) {
        return itemIds(Ingredient.of(TagKey.create(Registries.ITEM, new ResourceLocation(tag))).getItems());
    }
    private static String fluidId(net.minecraft.world.level.material.Fluid fluid) {
        return BuiltInRegistries.FLUID.getKey(fluid instanceof FlowingFluid flowing ? flowing.getSource() : fluid).toString();
    }
    private static Set<String> itemIds(ItemStack[] stacks) {
        var ids = new TreeSet<String>();
        for (var stack : stacks) if (!stack.isEmpty()) ids.add(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
        return ids;
    }
    private static List<Set<String>> itemInputs(GTRecipe recipe) {
        var groups = new ArrayList<Set<String>>();
        for (var content : recipe.getInputContents(ItemRecipeCapability.CAP)) {
            var ingredient = ItemRecipeCapability.CAP.of(content.content);
            if (!(ingredient instanceof IntCircuitIngredient)) groups.add(itemIds(ingredient.getItems()));
        }
        return groups;
    }
    private static List<Set<String>> fluidInputs(GTRecipe recipe) {
        var groups = new ArrayList<Set<String>>();
        for (var content : recipe.getInputContents(FluidRecipeCapability.CAP)) {
            var ids = new TreeSet<String>();
            for (var stack : FluidRecipeCapability.CAP.of(content.content).getStacks())
                if (!stack.isEmpty()) ids.add(fluidId(stack.getFluid()));
            groups.add(ids);
        }
        return groups;
    }
    private static Set<String> itemOutputs(GTRecipe recipe) {
        var ids = new TreeSet<String>();
        for (var content : recipe.getOutputContents(ItemRecipeCapability.CAP))
            ids.addAll(itemIds(ItemRecipeCapability.CAP.of(content.content).getItems()));
        return ids;
    }
    private static Set<String> fluidOutputs(GTRecipe recipe) {
        var ids = new TreeSet<String>();
        for (var content : recipe.getOutputContents(FluidRecipeCapability.CAP))
            for (var stack : FluidRecipeCapability.CAP.of(content.content).getStacks())
                if (!stack.isEmpty()) ids.add(fluidId(stack.getFluid()));
        return ids;
    }
}


