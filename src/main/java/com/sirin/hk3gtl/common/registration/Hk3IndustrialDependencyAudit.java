package com.sirin.hk3gtl.common.registration;

import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.ingredient.IntCircuitIngredient;
import com.gregtechceu.gtceu.api.registry.GTRegistries;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
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
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.ShapedRecipe;
import net.minecraft.world.item.crafting.ShapelessRecipe;
import net.minecraft.world.level.material.FlowingFluid;
import java.util.*;

/**
 * 【文件职责】从整包最终注册表构造工业依赖图；只读，不授予研究、事实或物品。
 * 【变更记录 #1】2026-10-17 13:55:11（第1次备注 · 内测5修订160）
 * 删除：无。新增：完整研究门槛、PLAN实验/事实、标签替代、现有控制器和研究费用的统一适配。
 * 修改：核验范围覆盖HK3物料生产者及全部已注册HK3配方，不把缺少执行器的类型当作GT通用设备。
 * 用途：输出可追溯的拓扑阻断；外部GTL资源可用仍是明确前提，不证明数量、供电、成型和生存通关。
 * 【变更记录 #2】2026-10-17 14:07:48（第2次备注 · 内测5修订160）
 * 删除：把所有设备都视为生产机器的空数组前提。新增：无配方类型和空类型项守卫。
 * 修改：储存/管网等非加工设备跳过能力桥接；用途：修复2.8实际启动时的空指针，不授予虚构执行能力。
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
        for (var definition : GTRegistries.MACHINES) {
            String item = BuiltInRegistries.ITEM.getKey(definition.asStack().getItem()).toString();
            if (definition.asStack().isEmpty()) continue;
            var recipeTypes = definition.getRecipeTypes();
            if (recipeTypes == null) continue;
            for (var type : new LinkedHashSet<>(Arrays.asList(recipeTypes))) {
                if (type == null) continue;
                String capability = "executor:" + type.registryName;
                deviceRules.add(new RecipeReachability.Recipe("device:" + definition.getId() + "/" + type.registryName,
                        List.of(Set.of(item)), List.of(), Set.of(), "", Set.of(),
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
                    List.of(Set.of(BuiltInRegistries.ITEM.getKey(institute.asStack().getItem()).toString())), List.of(),
                    permission, "", Set.of(), Set.of("laboratory_ready:" + lab), Set.of(), Set.of(), Set.of()));
        }
        var plans = new HashMap<String, Hk3ResearchProcessPlans.Plan>();
        Hk3ResearchProcessPlans.all().forEach(p -> plans.put(p.id(), p));
        var recipes = new ArrayList<RecipeReachability.Recipe>();
        var productionIds = new TreeSet<String>();
        var unresolved = new ArrayList<String>();
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
            String oldExperiment = gt.data.getString(Hk3LiquidProcessMachine.EXPERIMENT);
            if (!oldExperiment.isBlank()) evidence.add(oldExperiment);
            String planId = gt.data.getString(Hk3ResearchRecipeRuntime.PLAN);
            if (!planId.isBlank()) {
                var plan = plans.get(planId);
                if (plan == null) {
                    facts.add("invalid_execution_plan:" + planId);
                } else {
                    String expectedPath = Hk3ResearchProcessTypes.get(plan.role()).registryName.getPath() + "/" + plan.id();
                    if (!gt.id.getPath().equals(expectedPath) || !(gt.id.getNamespace().equals("gtceu") || gt.id.getNamespace().equals("hk3gtl"))
                            || gt.recipeType != Hk3ResearchProcessTypes.get(plan.role())) facts.add("invalid_plan_recipe_binding:" + planId);
                    gates.addAll(plan.requirements());
                    factOutputs.addAll(plan.facts());
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
            if (gt.id.getPath().endsWith("/industrial_liquid_sampling")) evidence.add("RN-HED");
            if (gt.id.getPath().endsWith("/industrial_initial_spectrum")) evidence.add("RN-HSA");
            recipes.add(new RecipeReachability.Recipe(gt.id.toString(), itemInputs(gt), fluidInputs(gt),
                    gates, "executor:" + gt.recipeType.registryName, facts,
                    itemOut, fluidOut, factOutputs, evidence));
        }
        recipes.addAll(deviceRules);
        addLaboratoryExperiments(recipes);
        var topics = new ArrayList<RecipeReachability.Research>();
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
                facts.add("external_ledger:three_recovery_proofs");
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。

// 【变更记录 · 修订161】2026-10-17 14:20:59：将原有GT格式校验前移至选中生产者后、加入依赖闭包前；非法配方仅进入问题清单，不计为生产者或产生拓扑资源，校验范围和判据不变。
