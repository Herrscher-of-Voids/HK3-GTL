package com.sirin.hk3gtl.common.recipe.audit;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;

/**
 * 【变更记录 #1】2026-10-17 13:50:48（内测5修订160）
 * 删除：无。新增：不依赖游戏运行时的物料、设备、研究与事实定点闭包及逐项阻断原因。
 * 修改：统一缺项结果与不可变快照；用途：修正旧判定基础，只证明拓扑可能性，不证明数量、供电或生存验收。
 */
public final class RecipeReachability {
    private RecipeReachability() {}

    /** 同一替代组任取一种，各组必须同时满足；非消耗催化剂也必须存在，不能无种子启动。 */
    public record Recipe(String id, List<Set<String>> itemInputs, List<Set<String>> fluidInputs,
            Set<String> researchInputs, String controller, Set<String> factInputs, Set<String> evidenceInputs,
            Set<String> itemOutputs, Set<String> fluidOutputs, Set<String> factOutputs, Set<String> evidenceOutputs) {
        public Recipe {
            id = identifier(id);
            itemInputs = alternatives(itemInputs); fluidInputs = alternatives(fluidInputs);
            researchInputs = names(researchInputs); controller = Objects.requireNonNullElse(controller, "");
            if (!controller.isEmpty()) identifier(controller);
            factInputs = names(factInputs); evidenceInputs = names(evidenceInputs);
            itemOutputs = names(itemOutputs); fluidOutputs = names(fluidOutputs);
            factOutputs = names(factOutputs); evidenceOutputs = names(evidenceOutputs);
        }

        public Recipe(String id, List<Set<String>> itemInputs, List<Set<String>> fluidInputs,
                Set<String> researchInputs, String controller, Set<String> factInputs,
                Set<String> itemOutputs, Set<String> fluidOutputs, Set<String> factOutputs, Set<String> evidenceOutputs) {
            this(id, itemInputs, fluidInputs, researchInputs, controller, factInputs, Set.of(),
                    itemOutputs, fluidOutputs, factOutputs, evidenceOutputs);
        }
    }

    /** 费用只检查可制备性；不模拟库存扣费、研究点、时长、电压或研究所的真实运行。 */
    public record Research(String id, Set<String> prerequisites, Set<String> evidence, Set<String> facts,
            List<Set<String>> itemCosts, List<Set<String>> fluidCosts) {
        public Research {
            id = identifier(id); prerequisites = names(prerequisites);
            evidence = names(evidence); facts = names(facts);
            itemCosts = alternatives(itemCosts); fluidCosts = alternatives(fluidCosts);
        }
    }

    /** 只有调用方明确认可的外部资源和已有事实可作为种子；核心不会默认放行任何命名空间。 */
    public record Seeds(Set<String> items, Set<String> fluids, Set<String> research,
            Set<String> facts, Set<String> evidence) {
        public Seeds {
            items = names(items); fluids = names(fluids); research = names(research);
            facts = names(facts); evidence = names(evidence);
        }

        public static Seeds empty() { return new Seeds(Set.of(), Set.of(), Set.of(), Set.of(), Set.of()); }
    }

    public record State(Set<String> items, Set<String> fluids, Set<String> research,
            Set<String> facts, Set<String> evidence) {
        public State {
            items = names(items); fluids = names(fluids); research = names(research);
            facts = names(facts); evidence = names(evidence);
        }
    }

    /** 空替代组仍作为阻断保留，防止把空标签错误当成不需要材料。 */
    public record Blockers(Set<String> research, Set<String> controllers,
            List<Set<String>> itemAlternatives, List<Set<String>> fluidAlternatives,
            Set<String> facts, Set<String> evidence) {
        public Blockers {
            research = names(research); controllers = names(controllers);
            itemAlternatives = alternatives(itemAlternatives); fluidAlternatives = alternatives(fluidAlternatives);
            facts = names(facts); evidence = names(evidence);
        }

        public boolean isEmpty() {
            return research.isEmpty() && controllers.isEmpty() && itemAlternatives.isEmpty()
                    && fluidAlternatives.isEmpty() && facts.isEmpty() && evidence.isEmpty();
        }
    }

    public record Result(State state, Set<String> finishedRecipes,
            Map<String, Blockers> blockedRecipes, Map<String, Blockers> blockedResearch) {
        public Result {
            Objects.requireNonNull(state); finishedRecipes = names(finishedRecipes);
            blockedRecipes = Collections.unmodifiableMap(new LinkedHashMap<>(blockedRecipes));
            blockedResearch = Collections.unmodifiableMap(new LinkedHashMap<>(blockedResearch));
        }
    }

    /** 定点只扩大可达集合；自循环没有初始种子时不会自行产生任何材料或研究。 */
    public static Result analyze(Collection<Recipe> recipes, Collection<Research> research, Seeds seeds) {
        Objects.requireNonNull(seeds);
        var recipeIndex = indexRecipes(recipes);
        var researchIndex = indexResearch(research);
        var items = new TreeSet<>(seeds.items()); var fluids = new TreeSet<>(seeds.fluids());
        var completed = new TreeSet<>(seeds.research()); var facts = new TreeSet<>(seeds.facts());
        var evidence = new TreeSet<>(seeds.evidence()); var finished = new TreeSet<String>();
        boolean changed;
        do {
            changed = false;
            for (var recipe : recipeIndex.values()) {
                if (finished.contains(recipe.id()) || !blockers(recipe, items, fluids, completed, facts, evidence).isEmpty()) continue;
                finished.add(recipe.id());
                items.addAll(recipe.itemOutputs()); fluids.addAll(recipe.fluidOutputs());
                facts.addAll(recipe.factOutputs()); evidence.addAll(recipe.evidenceOutputs());
                changed = true;
            }
            for (var topic : researchIndex.values()) {
                if (!completed.contains(topic.id()) && blockers(topic, items, fluids, completed, facts, evidence).isEmpty()) {
                    completed.add(topic.id()); changed = true;
                }
            }
        } while (changed);
        var blockedRecipes = new LinkedHashMap<String, Blockers>();
        for (var recipe : recipeIndex.values()) if (!finished.contains(recipe.id()))
            blockedRecipes.put(recipe.id(), blockers(recipe, items, fluids, completed, facts, evidence));
        var blockedResearch = new LinkedHashMap<String, Blockers>();
        for (var topic : researchIndex.values()) if (!completed.contains(topic.id()))
            blockedResearch.put(topic.id(), blockers(topic, items, fluids, completed, facts, evidence));
        return new Result(new State(items, fluids, completed, facts, evidence), finished, blockedRecipes, blockedResearch);
    }

    private static Blockers blockers(Recipe r, Set<String> items, Set<String> fluids,
            Set<String> research, Set<String> facts, Set<String> evidence) {
        return new Blockers(missing(r.researchInputs(), research),
                r.controller().isEmpty() || items.contains(r.controller()) ? Set.of() : Set.of(r.controller()),
                missingAlternatives(r.itemInputs(), items), missingAlternatives(r.fluidInputs(), fluids),
                missing(r.factInputs(), facts), missing(r.evidenceInputs(), evidence));
    }

    private static Blockers blockers(Research r, Set<String> items, Set<String> fluids,
            Set<String> research, Set<String> facts, Set<String> evidence) {
        return new Blockers(missing(r.prerequisites(), research), Set.of(),
                missingAlternatives(r.itemCosts(), items), missingAlternatives(r.fluidCosts(), fluids),
                missing(r.facts(), facts), missing(r.evidence(), evidence));
    }

    private static Set<String> missing(Set<String> required, Set<String> available) {
        var missing = new TreeSet<>(required); missing.removeAll(available); return missing;
    }

    private static List<Set<String>> missingAlternatives(List<Set<String>> required, Set<String> available) {
        var missing = new ArrayList<Set<String>>();
        for (var group : required) if (Collections.disjoint(group, available)) missing.add(group);
        return missing;
    }

    private static Map<String, Recipe> indexRecipes(Collection<Recipe> recipes) {
        var result = new LinkedHashMap<String, Recipe>();
        for (var recipe : recipes) if (result.putIfAbsent(recipe.id(), recipe) != null)
            throw new IllegalArgumentException("重复配方标识：" + recipe.id());
        return result;
    }

    private static Map<String, Research> indexResearch(Collection<Research> research) {
        var result = new LinkedHashMap<String, Research>();
        for (var topic : research) if (result.putIfAbsent(topic.id(), topic) != null)
            throw new IllegalArgumentException("重复研究标识：" + topic.id());
        return result;
    }

    private static String identifier(String value) {
        if (value == null || value.isBlank()) throw new IllegalArgumentException("标识不能为空");
        return value;
    }

    private static Set<String> names(Collection<String> values) {
        var copy = new TreeSet<String>();
        for (var value : Objects.requireNonNull(values)) copy.add(identifier(value));
        return Collections.unmodifiableSet(copy);
    }

    private static List<Set<String>> alternatives(List<Set<String>> groups) {
        var copy = new ArrayList<Set<String>>();
        for (var group : Objects.requireNonNull(groups)) copy.add(names(group));
        return List.copyOf(copy);
    }
}
