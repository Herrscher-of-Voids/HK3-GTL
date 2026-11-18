package com.sirin.hk3gtl.test.compat;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/** 真实GTCEu 1.4.4方法原文提取，外围类型为受控替身；不模拟物料消费或机器执行。 */
final class NativePrefixTreeFixture {
    final Branch lookup = new Branch();
    final Object recipeType = new Object();

    boolean add(GTRecipe recipe) {
        return recurseIngredientTreeAdd(recipe, recipe.inputs, lookup, 0, 0);
    }

    boolean indexed(GTRecipe recipe) { return lookup.leaves().stream().anyMatch(leaf -> leaf == recipe); }

    List<GTRecipe> leaves() { return lookup.leaves(); }

    private boolean recurseIngredientTreeAdd(@NotNull GTRecipe recipe, @NotNull List<List<AbstractMapIngredient>> ingredients, @NotNull Branch branchMap, int index, int count) {
        if (count >= ingredients.size()) {
            return true;
        }
        if (index >= ingredients.size()) {
            throw new RuntimeException("Index out of bounds for recurseItemTreeAdd, should not happen");
        }
        List<AbstractMapIngredient> current = ingredients.get(index);
        Branch branchRight = new Branch();
        for (AbstractMapIngredient obj : current) {
            Map<AbstractMapIngredient, Either<GTRecipe, Branch>> targetMap = GTRecipeLookup.determineRootNodes(obj, branchMap);
            Either r = targetMap.compute(obj, (k, v) -> {
                if (count == ingredients.size() - 1) {
                    if (v != null) {
                        if ((v.left().isEmpty() || v.left().get() != recipe) && (ConfigHolder.INSTANCE.dev.debug || Platform.isDevEnv())) {
                            GTCEu.LOGGER.warn("Recipe duplicate or conflict found in GTRecipeType {} and was not added. See next lines for details", (Object)BuiltInRegistries.f_256990_.m_7981_((Object)this.recipeType));
                            GTCEu.LOGGER.warn("Attempted to add GTRecipe: {}", (Object)recipe.m_6423_());
                            if (v.left().isPresent()) {
                                GTCEu.LOGGER.warn("Which conflicts with: {}", (Object)((GTRecipe)v.left().get()).m_6423_());
                            } else {
                                GTCEu.LOGGER.warn("Could not find exact duplicate/conflict.");
                            }
                        }
                        return v;
                    }
                    return Either.left((Object)recipe);
                }
                if (v == null) {
                    return Either.right((Object)branchRight);
                }
                return v;
            });
            if (r.left().isPresent()) {
                if (r.left().get() == recipe) continue;
                return false;
            }
            boolean addedNextBranch = r.right().filter(m -> this.recurseIngredientTreeAdd(recipe, ingredients, (Branch)m, (index + 1) % ingredients.size(), count + 1)).isPresent();
            if (addedNextBranch) continue;
            if (count == ingredients.size() - 1) {
                targetMap.remove(obj);
            } else if (targetMap.get(obj).right().isPresent() && ((Branch)targetMap.get(obj).right().get()).isEmptyBranch()) {
                targetMap.remove(obj);
            }
            return false;
        }
        return true;
    }

    protected static Map<AbstractMapIngredient, Either<GTRecipe, Branch>> determineRootNodes(@NotNull AbstractMapIngredient ingredient, @NotNull Branch branchMap) {
        return ingredient.isSpecialIngredient() ? branchMap.getSpecialNodes() : branchMap.getNodes();
    }

    record AbstractMapIngredient(String name, boolean special) {
        boolean isSpecialIngredient() { return special; }
    }

    static final class GTRecipe {
        final String id;
        final List<List<AbstractMapIngredient>> inputs;
        GTRecipe(String id, List<List<AbstractMapIngredient>> inputs) { this.id = id; this.inputs = inputs; }
        String m_6423_() { return id; }
    }

    static final class Branch {
        final Map<AbstractMapIngredient, Either<GTRecipe, Branch>> nodes = new LinkedHashMap<>();
        final Map<AbstractMapIngredient, Either<GTRecipe, Branch>> specialNodes = new LinkedHashMap<>();
        Map<AbstractMapIngredient, Either<GTRecipe, Branch>> getNodes() { return nodes; }
        Map<AbstractMapIngredient, Either<GTRecipe, Branch>> getSpecialNodes() { return specialNodes; }
        boolean isEmptyBranch() { return nodes.isEmpty() && specialNodes.isEmpty(); }
        List<GTRecipe> leaves() {
            List<GTRecipe> found = new ArrayList<>();
            for (var map : List.of(nodes, specialNodes)) for (var value : map.values()) {
                value.left().ifPresent(found::add);
                value.right().ifPresent(branch -> found.addAll(branch.leaves()));
            }
            return found;
        }
    }

    static final class Either<L, R> {
        private final L left;
        private final R right;
        private Either(L left, R right) { this.left = left; this.right = right; }
        @SuppressWarnings("unchecked")
        static <L, R> Either<L, R> left(Object value) { return new Either<>((L) value, null); }
        @SuppressWarnings("unchecked")
        static <L, R> Either<L, R> right(Object value) { return new Either<>(null, (R) value); }
        Optional<L> left() { return Optional.ofNullable(left); }
        Optional<R> right() { return Optional.ofNullable(right); }
    }

    static final class GTRecipeLookup {
        static Map<AbstractMapIngredient, Either<GTRecipe, Branch>> determineRootNodes(AbstractMapIngredient ingredient, Branch branch) {
            return NativePrefixTreeFixture.determineRootNodes(ingredient, branch);
        }
    }

    @interface NotNull { }
    static final class ConfigHolder {
        static final ConfigHolder INSTANCE = new ConfigHolder();
        final Dev dev = new Dev();
        static final class Dev { boolean debug; }
    }
    static final class Platform { static boolean isDevEnv() { return false; } }
    static final class GTCEu {
        static final Logger LOGGER = new Logger();
        static final class Logger { void warn(String message, Object... args) { } }
    }
    static final class BuiltInRegistries {
        static final Registry f_256990_ = new Registry();
        static final class Registry { Object m_7981_(Object value) { return value; } }
    }
}
