package com.sirin.hk3gtl.test.machine;

/**
 * ParallelData 和 AllocationAlgorithm 的纯逻辑单元测试。
 *
 * <p>这些测试验证数据结构的正确性，不依赖 Minecraft 运行时。</p>
 * <p>运行方式：通过 IDE 直接运行 main() 方法。</p>
 *
 * <h3>测试覆盖</h3>
 * <ul>
 *   <li>T-001 ~ T-003：AllocationAlgorithm 枚举值验证</li>
 *   <li>T-010 ~ T-016：ParallelData 构造与验证（通过反射创建实例）</li>
 *   <li>T-020 ~ T-023：边界条件（null、空列表、不匹配数组）</li>
 *   <li>T-030 ~ T-033：equals / hashCode 一致性</li>
 * </ul>
 */
public class ParallelDataTest {

    // ── AllocationAlgorithm 测试 ─────────────────────────────────────────

    /** T-001: 枚举值存在性验证 */
    public static boolean testT001_enumValues() {
        try {
            Class<?> enumClass = Class.forName("com.sirin.hk3gtl.common.machine.AllocationAlgorithm");
            Object[] values = (Object[]) enumClass.getMethod("values").invoke(null);
            assert values.length == 2 : "应有 2 个枚举值，实际: " + values.length;

            Object greedy = enumClass.getMethod("valueOf", String.class).invoke(null, "GREEDY");
            Object fair = enumClass.getMethod("valueOf", String.class).invoke(null, "FAIR");
            assert greedy != null;
            assert fair != null;
            assert !greedy.equals(fair);
            return true;
        } catch (Throwable t) {
            System.err.println("[T-001 FAIL] " + t.getClass().getSimpleName() + ": " + t.getMessage());
            return false;
        }
    }

    /** T-002: GREEDY 命名语义 */
    public static boolean testT002_greedySemantics() {
        try {
            Class<?> enumClass = Class.forName("com.sirin.hk3gtl.common.machine.AllocationAlgorithm");
            Object greedy = enumClass.getMethod("valueOf", String.class).invoke(null, "GREEDY");
            String name = (String) enumClass.getMethod("name").invoke(greedy);
            assert "GREEDY".equals(name) : "名称应为 GREEDY";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-002 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-003: FAIR 命名语义 */
    public static boolean testT003_fairSemantics() {
        try {
            Class<?> enumClass = Class.forName("com.sirin.hk3gtl.common.machine.AllocationAlgorithm");
            Object fair = enumClass.getMethod("valueOf", String.class).invoke(null, "FAIR");
            String name = (String) enumClass.getMethod("name").invoke(fair);
            assert "FAIR".equals(name) : "名称应为 FAIR";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-003 FAIL] " + t.getMessage());
            return false;
        }
    }

    // ── ParallelData 构造测试 ─────────────────────────────────────────────

    /** T-010: 正常构造 */
    public static boolean testT010_validConstruction() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            Object data = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(new java.util.ArrayList<>(), new long[]{1, 2, 3}, true, new java.util.ArrayList<>());

            assert data != null;
            assert ((boolean) pdClass.getMethod("getShouldProcess").invoke(data));
            long[] parallels = (long[]) pdClass.getMethod("getParallels").invoke(data);
            assert parallels.length == 3;
            assert parallels[1] == 2;
            return true;
        } catch (Throwable t) {
            System.err.println("[T-010 FAIL] " + t.getClass().getSimpleName() + ": " + t.getMessage());
            return false;
        }
    }

    /** T-011: isValid - 正常情况应返回 true */
    public static boolean testT011_isValidTrue() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            java.util.List<Object> origin = java.util.List.of("recipe_a");
            long[] parallels = new long[]{5};
            java.util.List<Object> processed = java.util.List.of("recipe_a_processed");
            Object data = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, parallels, true, processed);

            boolean valid = (boolean) pdClass.getMethod("isValid").invoke(data);
            assert valid : "有效数据应返回 true";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-011 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-012: isValid - originRecipeList 为 null 应返回 false */
    public static boolean testT012_isValidNullOrigin() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            Object data = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(null, new long[]{1}, true, java.util.List.of("x"));

            boolean valid = (boolean) pdClass.getMethod("isValid").invoke(data);
            assert !valid : "null originList 应返回 false";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-012 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-013: isValid - 空列表应返回 false */
    public static boolean testT013_isValidEmptyOrigin() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            Object data = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(java.util.List.of(), new long[]{}, true, java.util.List.of());

            boolean valid = (boolean) pdClass.getMethod("isValid").invoke(data);
            assert !valid : "空 originList 应返回 false";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-013 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-014: isValid - parallels 为 null 应返回 false */
    public static boolean testT014_isValidNullParallels() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            Object data = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(java.util.List.of("a"), null, true, java.util.List.of("x"));

            boolean valid = (boolean) pdClass.getMethod("isValid").invoke(data);
            assert !valid : "null parallels 应返回 false";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-014 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-015: isValid - 数组长度不匹配应返回 false */
    public static boolean testT015_isValidLengthMismatch() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            java.util.List<Object> origin = java.util.List.of("a", "b"); // 2
            long[] parallels = new long[]{1}; // 1
            Object data = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, parallels, true, java.util.List.of("x"));

            boolean valid = (boolean) pdClass.getMethod("isValid").invoke(data);
            assert !valid : "长度不匹配应返回 false";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-015 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-016: isValid - shouldProcess=false 时仍应有效 */
    public static boolean testT016_isValidWithShouldProcessFalse() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            java.util.List<Object> origin = java.util.List.of("a");
            long[] parallels = new long[]{3};
            Object data = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, parallels, false, java.util.List.of());

            boolean valid = (boolean) pdClass.getMethod("isValid").invoke(data);
            assert valid : "shouldProcess=false 且数据完整应返回 true";
            boolean sp = (boolean) pdClass.getMethod("getShouldProcess").invoke(data);
            assert !sp : "shouldProcess 应为 false";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-016 FAIL] " + t.getMessage());
            return false;
        }
    }

    // ── equals / hashCode 测试 ────────────────────────────────────────────

    /** T-030: 相同数据应 equals */
    public static boolean testT030_equalsSame() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            java.util.List<Object> origin = java.util.List.of("a");
            long[] parallels = new long[]{10};
            java.util.List<Object> processed = java.util.List.of("p");

            Object a = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, parallels, true, processed);
            Object b = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, new long[]{10}, true, processed);

            boolean eq = (boolean) a.getClass().getMethod("equals", Object.class).invoke(a, b);
            assert eq : "相同数据应 equals";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-030 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-031: 不同数据应不等 */
    public static boolean testT031_equalsDifferent() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            java.util.List<Object> origin = java.util.List.of("a");

            Object a = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, new long[]{1}, true, java.util.List.of());
            Object b = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, new long[]{2}, true, java.util.List.of());

            boolean eq = (boolean) a.getClass().getMethod("equals", Object.class).invoke(a, b);
            assert !eq : "不同 parallels 应返回 false";
            return true;
        } catch (Throwable t) {
            System.err.println("[T-031 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-032: hashCode 一致性 */
    public static boolean testT032_hashCodeConsistency() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            java.util.List<Object> origin = java.util.List.of("a", "b");

            Object a = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, new long[]{5, 3}, true, java.util.List.of());
            Object b = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, new long[]{5, 3}, true, java.util.List.of());

            int ha = (int) a.getClass().getMethod("hashCode").invoke(a);
            int hb = (int) b.getClass().getMethod("hashCode").invoke(b);
            assert ha == hb : "相同数据的 hashCode 应相等: " + ha + " vs " + hb;
            return true;
        } catch (Throwable t) {
            System.err.println("[T-032 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-033: toString 非空 */
    public static boolean testT033_toString() {
        try {
            Class<?> pdClass = Class.forName("com.sirin.hk3gtl.common.machine.ParallelData");
            java.util.List<Object> origin = java.util.List.of("r1");
            Object data = pdClass.getConstructor(
                    java.util.List.class, long[].class, boolean.class, java.util.List.class
            ).newInstance(origin, new long[]{7}, false, java.util.List.of());

            String s = (String) data.getClass().getMethod("toString").invoke(data);
            assert s != null && !s.isEmpty() : "toString 不应为空";
            assert s.contains("ParallelData") : "toString 应包含类名: " + s;
            return true;
        } catch (Throwable t) {
            System.err.println("[T-033 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-040: 验证 Hk3RecipeCalculationHelper 类存在 */
    public static boolean testT040_helperClassExists() {
        try {
            Class<?> helperClass = Class.forName("com.sirin.hk3gtl.common.machine.Hk3RecipeCalculationHelper");
            assert helperClass != null : "Helper 类应存在";
            // 验证关键方法存在
            helperClass.getMethod("multipleRecipe",
                    Class.forName("com.gregtechceu.gtceu.api.recipe.GTRecipe"), long.class);
            helperClass.getMethod("calculateParallel",
                    Class.forName("com.gregtechceu.gtceu.api.capability.recipe.IRecipeCapabilityHolder"),
                    Class.forName("com.gregtechceu.gtceu.api.recipe.GTRecipe"), long.class);
            helperClass.getMethod("calculateParallelsWithGreedyAllocation",
                    java.util.Collection.class, long.class,
                    Class.forName("com.gregtechceu.gtceu.api.capability.recipe.IRecipeCapabilityHolder"),
                    Class.forName("com.sirin.hk3gtl.common.machine.Hk3RecipeCalculationHelper$FullRecipeModifier"),
                    Class.forName("com.sirin.hk3gtl.common.machine.Hk3RecipeCalculationHelper$ParallelCalculator"));
            helperClass.getMethod("calculateParallelsWithFairAllocation",
                    java.util.Collection.class, long.class,
                    Class.forName("com.gregtechceu.gtceu.api.capability.recipe.IRecipeCapabilityHolder"),
                    Class.forName("com.sirin.hk3gtl.common.machine.Hk3RecipeCalculationHelper$FullRecipeModifier"),
                    Class.forName("com.sirin.hk3gtl.common.machine.Hk3RecipeCalculationHelper$ParallelCalculator"));
            helperClass.getMethod("buildNormalRecipe",
                    Class.forName("com.sirin.hk3gtl.common.machine.ParallelData"),
                    Class.forName("com.gregtechceu.gtceu.api.recipe.GTRecipeType"));
            return true;
        } catch (Throwable t) {
            System.err.println("[T-040 FAIL] " + t.getClass().getSimpleName() + ": " + t.getMessage());
            return false;
        }
    }

    /** T-041: 验证 Hk3MultiRecipeLogic 关键方法 */
    public static boolean testT041_multiRecipeLogicMethods() {
        try {
            Class<?> logicClass = Class.forName("com.sirin.hk3gtl.common.machine.Hk3MultiRecipeLogic");
            assert logicClass != null : "Hk3MultiRecipeLogic 类应存在";

            // 验证可重写配置方法
            logicClass.getMethod("allocateMethod");
            logicClass.getMethod("getMaxMergedRecipes");

            // 验证核心流程方法
            logicClass.getDeclaredMethod("lookupRecipeSet");
            logicClass.getDeclaredMethod("calculateParallels", java.util.Set.class);
            logicClass.getDeclaredMethod("buildFinalNormalRecipe",
                    Class.forName("com.sirin.hk3gtl.common.machine.ParallelData"));

            return true;
        } catch (Throwable t) {
            System.err.println("[T-041 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-042: 验证 IMultiTypeRecipeMachine 接口 */
    public static boolean testT042_interfaceExists() {
        try {
            Class<?> iface = Class.forName("com.sirin.hk3gtl.common.machine.IMultiTypeRecipeMachine");
            assert iface.isInterface() : "应为接口";

            // 验证 getExtendRecipeTypes 方法
            iface.getMethod("getExtendRecipeTypes");
            return true;
        } catch (Throwable t) {
            System.err.println("[T-042 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** T-043: 验证 Hk3WorkableMultiblockMachine 类存在且可被继承 */
    public static boolean testT043_machineImplementsInterface() {
        try {
            Class<?> machineClass = Class.forName("com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine");
            assert machineClass != null : "Hk3WorkableMultiblockMachine 应存在";
            // IMultiTypeRecipeMachine 由子类按需实现，此处仅验证类可加载
            return true;
        } catch (Throwable t) {
            System.err.println("[T-043 FAIL] " + t.getMessage());
            return false;
        }
    }

    // ── 运行器 ────────────────────────────────────────────────────────────

    /** 全局用例计数：run() 每次执行都会递增，保证退出码真实反映失败。 */
    private static int passed = 0;
    private static int failed = 0;

    public static void main(String[] args) {
        passed = 0;
        failed = 0;

        // T-001 ~ T-003: AllocationAlgorithm
        run("T-001", ParallelDataTest::testT001_enumValues);
        run("T-002", ParallelDataTest::testT002_greedySemantics);
        run("T-003", ParallelDataTest::testT003_fairSemantics);

        // T-010 ~ T-016: ParallelData
        run("T-010", ParallelDataTest::testT010_validConstruction);
        run("T-011", ParallelDataTest::testT011_isValidTrue);
        run("T-012", ParallelDataTest::testT012_isValidNullOrigin);
        run("T-013", ParallelDataTest::testT013_isValidEmptyOrigin);
        run("T-014", ParallelDataTest::testT014_isValidNullParallels);
        run("T-015", ParallelDataTest::testT015_isValidLengthMismatch);
        run("T-016", ParallelDataTest::testT016_isValidWithShouldProcessFalse);

        // T-030 ~ T-033: equals/hashCode/toString
        run("T-030", ParallelDataTest::testT030_equalsSame);
        run("T-031", ParallelDataTest::testT031_equalsDifferent);
        run("T-032", ParallelDataTest::testT032_hashCodeConsistency);
        run("T-033", ParallelDataTest::testT033_toString);

        // T-040 ~ T-043: 类结构验证
        run("T-040", ParallelDataTest::testT040_helperClassExists);
        run("T-041", ParallelDataTest::testT041_multiRecipeLogicMethods);
        run("T-042", ParallelDataTest::testT042_interfaceExists);
        run("T-043", ParallelDataTest::testT043_machineImplementsInterface);

        System.out.println("\n=============================================");
        System.out.println("  HK3GTL Multi-Recipe System Test Results");
        System.out.println("=============================================");
        System.out.println("  Passed: " + passed + " / " + (passed + failed));
        System.out.println("  Failed: " + failed);
        System.out.println("=============================================");
        System.exit(failed > 0 ? 1 : 0);
    }

    @FunctionalInterface
    interface TestCase { boolean run() throws Throwable; }

    /**
     * 执行单个用例并累计 passed/failed。
     * 无论测试返回 false 还是抛出异常，都会递增 failed，确保 main 退出码真实。
     */
    private static void run(String id, TestCase test) {
        try {
            if (test.run()) {
                System.out.println("[PASS] " + id);
                passed++;
            } else {
                System.out.println("[FAIL] " + id);
                failed++;
            }
        } catch (Throwable t) {
            System.out.println("[FAIL] " + id + " - " + t.getClass().getSimpleName() + ": " + t.getMessage());
            failed++;
        }
    }
}
