package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.recipe.audit.RecipeReachability;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import static com.sirin.hk3gtl.common.recipe.audit.RecipeReachability.*;

/**
 * 【变更记录 #1】2026-10-17 13:50:48（内测5修订160）
 * 新增：自循环、全部研究前置、替代标签、种子催化剂、设备和真实事实缺口的独立回归。
 * 用途：验证理论审计不会自行放行缺失条件，不代表游戏内扣料或成型已通过。
 */
public final class RecipeReachabilityTest {
    private static int checks;
    private RecipeReachabilityTest() {}

    public static void main(String[] args) {
        bootstrap(); cycles(); alternativesAndCatalyst(); devicesAndFacts(); immutabilityAndInvalidData();
        System.out.println("RecipeReachabilityTest：" + checks + " 项通过；仅验证理论闭包，未执行游戏验收");
    }

    private static void bootstrap() {
        var recipes = List.of(
                recipe("final", List.of(Set.of("sample")), Set.of("R-A", "R-B"), "lab", Set.of(), Set.of("product"), Set.of(), Set.of()),
                recipe("sample", List.of(Set.of("max")), Set.of(), "lab", Set.of(), Set.of("sample"), Set.of("experiment"), Set.of("sampled")),
                recipe("cost", List.of(Set.of("max")), Set.of(), "", Set.of(), Set.of("fee"), Set.of(), Set.of()));
        var research = List.of(
                new Research("R-A", Set.of(), Set.of("experiment"), Set.of("sampled"), List.of(Set.of("fee")), List.of()),
                new Research("R-B", Set.of("R-A"), Set.of("experiment"), Set.of(), List.of(), List.of()));
        var result = RecipeReachability.analyze(recipes, research,
                new Seeds(Set.of("max", "lab"), Set.of(), Set.of(), Set.of(), Set.of()));
        check(result.finishedRecipes().equals(Set.of("final", "sample", "cost")), "跨轮前置完成后生产配方可达");
        check(result.state().research().equals(Set.of("R-A", "R-B")), "实验、事实和费用共同满足研究");
        check(result.state().items().contains("product") && result.blockedRecipes().isEmpty(), "最终产物可达且无虚假阻断");
        var missingFee = RecipeReachability.analyze(recipes.subList(0, 2), research,
                new Seeds(Set.of("max", "lab"), Set.of(), Set.of(), Set.of(), Set.of()));
        check(missingFee.blockedResearch().get("R-A").itemAlternatives().equals(List.of(Set.of("fee"))), "研究费用未制备时保留阻断");
        check(missingFee.blockedRecipes().get("final").research().equals(Set.of("R-A", "R-B")), "报告全部研究门槛");
        var oneGate = RecipeReachability.analyze(List.of(recipes.get(0)), List.of(),
                new Seeds(Set.of("sample", "lab"), Set.of(), Set.of("R-A"), Set.of(), Set.of()));
        check(oneGate.blockedRecipes().get("final").research().equals(Set.of("R-B")), "首个研究已完成不应跳过第二门槛");
    }

    private static void cycles() {
        var cycle = List.of(
                recipe("a", List.of(Set.of("b")), Set.of(), "", Set.of(), Set.of("a"), Set.of(), Set.of()),
                recipe("b", List.of(Set.of("a")), Set.of(), "", Set.of(), Set.of("b"), Set.of(), Set.of()));
        var closed = RecipeReachability.analyze(cycle, List.of(), Seeds.empty());
        check(closed.finishedRecipes().isEmpty() && closed.state().items().isEmpty(), "无种子的物料循环不可启动");
        var seeded = RecipeReachability.analyze(cycle, List.of(), new Seeds(Set.of("a"), Set.of(), Set.of(), Set.of(), Set.of()));
        check(seeded.finishedRecipes().size() == 2, "显式外部种子可启动循环");
        var selfResearch = new Research("R-SELF", Set.of("R-SELF"), Set.of(), Set.of(), List.of(), List.of());
        var research = RecipeReachability.analyze(List.of(), List.of(selfResearch), Seeds.empty());
        check(research.state().research().isEmpty() && research.blockedResearch().get("R-SELF").research().contains("R-SELF"), "研究自循环不自动完成");
    }

    private static void alternativesAndCatalyst() {
        var recipe = new Recipe("seeded", List.of(Set.of("steel", "alloy"), Set.of("catalyst")),
                List.of(Set.of("water", "distilled_water")), Set.of(), "", Set.of(),
                Set.of("product"), Set.of("waste"), Set.of(), Set.of());
        var noSeed = RecipeReachability.analyze(List.of(recipe), List.of(),
                new Seeds(Set.of("alloy"), Set.of("distilled_water"), Set.of(), Set.of(), Set.of()));
        check(noSeed.blockedRecipes().get("seeded").itemAlternatives().equals(List.of(Set.of("catalyst"))), "催化剂不消耗仍须先获得种子");
        var seeded = RecipeReachability.analyze(List.of(recipe), List.of(),
                new Seeds(Set.of("alloy", "catalyst"), Set.of("distilled_water"), Set.of(), Set.of(), Set.of()));
        check(seeded.finishedRecipes().contains("seeded") && seeded.state().fluids().contains("waste"), "物品和流体替代各任选一个即可");
        var emptyTag = recipe("empty", List.of(Set.of()), Set.of(), "", Set.of(), Set.of("free"), Set.of(), Set.of());
        var empty = RecipeReachability.analyze(List.of(emptyTag), List.of(), Seeds.empty());
        check(empty.blockedRecipes().get("empty").itemAlternatives().equals(List.of(Set.of())) && !empty.state().items().contains("free"), "空标签必须阻断而非免费通过");
    }

    private static void devicesAndFacts() {
        var recipe = new Recipe("run", List.of(Set.of("material")), List.of(Set.of("fluid")), Set.of("R"),
                "controller", Set.of("permission"), Set.of("evidence"), Set.of("output"), Set.of(), Set.of(), Set.of());
        var result = RecipeReachability.analyze(List.of(recipe), List.of(), Seeds.empty());
        var b = result.blockedRecipes().get("run");
        check(b.controllers().equals(Set.of("controller")), "缺控制器单独报告");
        check(b.research().equals(Set.of("R")) && b.facts().equals(Set.of("permission")) && b.evidence().equals(Set.of("evidence")), "研究、事实与证据不得互相替代");
        check(b.itemAlternatives().equals(List.of(Set.of("material"))) && b.fluidAlternatives().equals(List.of(Set.of("fluid"))), "缺物品和缺流体分别报告");
        var withItemOnly = RecipeReachability.analyze(List.of(recipe), List.of(),
                new Seeds(Set.of("material", "controller"), Set.of("fluid"), Set.of("R"), Set.of(), Set.of("evidence")));
        check(withItemOnly.finishedRecipes().isEmpty() && withItemOnly.blockedRecipes().get("run").facts().equals(Set.of("permission")), "持有材料与控制器不能伪造权限事实");
        var external = recipe("external", List.of(Set.of("gtceu:max_part")), Set.of(), "", Set.of(), Set.of("output"), Set.of(), Set.of());
        check(RecipeReachability.analyze(List.of(external), List.of(), Seeds.empty()).finishedRecipes().isEmpty(), "不默认授予外部命名空间物料");
    }

    private static void immutabilityAndInvalidData() {
        var inputs = new ArrayList<Set<String>>(); inputs.add(Set.of("source"));
        var recipe = recipe("copy", inputs, Set.of(), "", Set.of(), Set.of("output"), Set.of(), Set.of());
        inputs.clear(); check(recipe.itemInputs().size() == 1, "输入列表防御复制");
        var result = RecipeReachability.analyze(List.of(recipe), List.of(), Seeds.empty());
        reject(() -> result.blockedRecipes().clear(), "结果映射不可变");
        reject(() -> result.state().items().add("source"), "闭包集合不可变");
        reject(() -> result.blockedRecipes().get("copy").itemAlternatives().get(0).add("source2"), "嵌套替代集合不可变");
        reject(() -> RecipeReachability.analyze(List.of(recipe, recipe), List.of(), Seeds.empty()), "重复配方不能静默覆盖");
        var topic = new Research("R", Set.of(), Set.of(), Set.of(), List.of(), List.of());
        reject(() -> RecipeReachability.analyze(List.of(), List.of(topic, topic), Seeds.empty()), "重复研究不能静默覆盖");
        reject(() -> recipe(" ", List.of(), Set.of(), "", Set.of(), Set.of(), Set.of(), Set.of()), "空标识拒绝加载");
    }

    private static Recipe recipe(String id, List<Set<String>> inputs, Set<String> research, String controller,
            Set<String> facts, Set<String> outputs, Set<String> evidenceOutputs, Set<String> factOutputs) {
        return new Recipe(id, inputs, List.of(), research, controller, facts, outputs, Set.of(), factOutputs, evidenceOutputs);
    }

    private static void check(boolean valid, String message) {
        checks++; if (!valid) throw new AssertionError(message);
    }

    private static void reject(Runnable action, String message) {
        try { action.run(); } catch (IllegalArgumentException | UnsupportedOperationException expected) { checks++; return; }
        throw new AssertionError(message);
    }
}
