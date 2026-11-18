package com.sirin.hk3gtl.test.compat;

import com.sirin.hk3gtl.common.recipe.Hk3RejectedRecipeIndex;
import com.sirin.hk3gtl.test.compat.NativePrefixTreeFixture.AbstractMapIngredient;
import com.sirin.hk3gtl.test.compat.NativePrefixTreeFixture.GTRecipe;

import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Predicate;

/** 原生方法提取夹具；不启动Forge，不代替真实Mixin与机器运行验收。 */
public final class RejectedRecipeIndexTest {
    public static void main(String[] args) throws Exception {
        GTRecipe shortRecipe = recipe("hk3gtl:rule", "substrate", "foil");
        GTRecipe longRecipe = recipe("hk3gtl:experiment", "substrate", "foil", "plate");
        prefixOrder(longRecipe, shortRecipe, true);
        prefixOrder(shortRecipe, longRecipe, false);
        partialPath();

        Hk3RejectedRecipeIndex<GTRecipe> index = new Hk3RejectedRecipeIndex<>();
        index.record(shortRecipe.id, shortRecipe, false);
        AtomicInteger tested = new AtomicInteger();
        Set<String> inventory = Set.of("substrate", "foil");
        Predicate<GTRecipe> nativeGate = recipe -> {
            tested.incrementAndGet();
            return recipe.inputs.stream().allMatch(alternatives -> alternatives.stream()
                    .anyMatch(input -> inventory.contains(input.name()))) && "hk3gtl:rule".equals(recipe.id);
        };
        List<GTRecipe> candidates = index.appendTo(null, recipe -> recipe.id);
        check(candidates.stream().filter(nativeGate).toList().equals(List.of(shortRecipe)), "输入和外部原生门槛允许时才给出候选");
        check(tested.get() == 1, "补充候选继续经过传入canHandle");
        check(candidates.stream().noneMatch(recipe -> recipe.inputs.stream().allMatch(alternatives ->
                alternatives.stream().anyMatch(input -> "other".equals(input.name())))), "无关原料不能匹配");
        check(candidates.stream().noneMatch(recipe -> Set.<String>of().contains(recipe.id)), "外部门槛未满足仍拒绝");

        GTRecipe cached = recipe(shortRecipe.id, "substrate", "foil");
        List<GTRecipe> existing = List.of(cached);
        List<GTRecipe> merged = index.appendTo(existing, recipe -> recipe.id);
        check(merged.size() == 1 && merged.get(0) == cached && existing.size() == 1, "保留ME缓存对象且按ID去重，不改原列表");
        index.record("gtceu:foreign", recipe("gtceu:foreign", "other"), false);
        index.record("gtceu:assembler/hk3gtl_main_component_hbv_electric_motor",
                recipe("gtceu:assembler/hk3gtl_main_component_hbv_electric_motor", "other"), false);
        check(index.appendTo(null, recipe -> recipe.id).size() == 1, "仅HK命名空间；不扩展第三方及GT命名空间HK贡献配方");
        index.record(shortRecipe.id, shortRecipe, true);
        check(index.isEmpty(), "确认真实叶存在后删除旧补充条目");

        index.record(shortRecipe.id, shortRecipe, false);
        index.clear();
        check(index.isEmpty() && index.appendTo(null, recipe -> recipe.id).isEmpty(), "clear清除后续搜索中的旧世界和重载候选");
        GTRecipe reloaded = recipe(shortRecipe.id, "reloaded");
        index.record(reloaded.id, reloaded, false);
        check(index.appendTo(null, recipe -> recipe.id).equals(List.of(reloaded)), "重载后新搜索只持有新对象");
        index.record(reloaded.id, recipe(reloaded.id, "replacement"), false);
        check(index.appendTo(null, recipe -> recipe.id).get(0) != reloaded, "同ID更新只保留新对象");
        nativeFixtureContract();
        mixinContract();
        System.out.println("Rejected recipe index: extracted native true/false missing-leaf cases, partial native leaf, gates, cached identity and reload passed; live Mixin and production pending");
    }

    private static GTRecipe recipe(String id, String... inputs) {
        return new GTRecipe(id, java.util.Arrays.stream(inputs)
                .map(input -> List.of(new AbstractMapIngredient(input, false))).toList());
    }

    private static void prefixOrder(GTRecipe first, GTRecipe second, boolean secondReturn) {
        NativePrefixTreeFixture tree = new NativePrefixTreeFixture();
        Hk3RejectedRecipeIndex<GTRecipe> index = new Hk3RejectedRecipeIndex<>();
        check(tree.add(first), "首条原生入树成功");
        check(tree.add(second) == secondReturn, "真实方法：长先短后返回true但漏叶，短先长后返回false并漏叶");
        check(tree.indexed(first) && !tree.indexed(second), "两个插入方向都需真实叶identity判定");
        index.record(first.id, first, tree.indexed(first));
        index.record(second.id, second, tree.indexed(second));
        List<GTRecipe> found = new ArrayList<>(tree.leaves());
        found.addAll(index.appendTo(null, recipe -> recipe.id));
        check(found.size() == 2 && found.contains(first) && found.contains(second), "原生叶和补充候选保留两条配方且不重复");
    }

    private static void partialPath() {
        NativePrefixTreeFixture tree = new NativePrefixTreeFixture();
        check(tree.add(recipe("hk3gtl:occupied", "occupied")), "先放冲突叶");
        GTRecipe partial = new GTRecipe("hk3gtl:partial", List.of(
                List.of(new AbstractMapIngredient("free", false), new AbstractMapIngredient("occupied", false)),
                List.of(new AbstractMapIngredient("foil", false))));
        check(!tree.add(partial) && tree.indexed(partial), "真实方法可部分入叶后返回false");
        Hk3RejectedRecipeIndex<GTRecipe> index = new Hk3RejectedRecipeIndex<>();
        index.record(partial.id, partial, tree.indexed(partial));
        check(index.isEmpty(), "部分原生叶已存在时不补重复；不扩大到修复所有替代路径");
    }

    private static void nativeFixtureContract() throws Exception {
        String fixture = Files.readString(Path.of("src/test/java/com/sirin/hk3gtl/test/compat/NativePrefixTreeFixture.java")).replace("\r\n", "\n");
        String[] declarations = {"    private boolean recurseIngredientTreeAdd(",
                "    protected static Map<AbstractMapIngredient, Either<GTRecipe, Branch>> determineRootNodes("};
        String[] hashes = {"b8f801ecfd7b3719f905befd5609c9b64d7b706e13129363c7203a63f0242631",
                "9bcb77012e9078f20eb4c1dcd45bfdb4d8e2ae452ef2b180f4afd51b255433e8"};
        for (int i = 0; i < declarations.length; i++) {
            int start = fixture.indexOf(declarations[i]);
            int at = fixture.indexOf('{', start) + 1;
            int depth = 1;
            while (depth != 0) {
                char c = fixture.charAt(at++);
                if (c == '{') depth++;
                if (c == '}') depth--;
            }
            String hash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256")
                    .digest(fixture.substring(start, at).getBytes(java.nio.charset.StandardCharsets.UTF_8)));
            check(hash.equals(hashes[i]), "真实冻结方法提取原文未被手写镜像替代");
        }
    }

    private static void mixinContract() throws Exception {
        String mixin = Files.readString(Path.of("src/main/java/com/sirin/hk3gtl/mixin/gtlcore/Hk3RecipeLookupMixin.java"));
        String config = Files.readString(Path.of("src/main/resources/hk3gtl.mixins.json"));
        check(config.contains("gtlcore.Hk3RecipeLookupMixin"), "通用侧Mixin已注册");
        check(mixin.contains("priority = 500") && mixin.contains("iterator.getAdditionalRecipes()"), "后于GTL/GTLadd覆盖并保留原附加候选");
        check(mixin.contains("anyMatch(leaf -> leaf == recipe)") && !mixin.contains("callback.getReturnValueZ()"), "注册时查真实叶，不依赖错误成功标记");
        check(mixin.indexOf("getRecipes(false)") < mixin.indexOf("method = \"getRecipeIterator\""), "全树叶扫描只位于注册阶段，非每次机器搜索");
        check(mixin.contains("method = \"removeAllRecipes\"") && mixin.contains("hk3gtl$rejected.clear()"), "原生重载同步清理");
        for (String forbidden : List.of("setupRecipe(", "handleRecipe(", "setWorkingEnabled(", "Hk3RecipeAccess.", "setReturnValue("))
            check(!mixin.contains(forbidden), "不得旁路原生执行或取消原有返回：" + forbidden);
    }

    private static void check(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
}
