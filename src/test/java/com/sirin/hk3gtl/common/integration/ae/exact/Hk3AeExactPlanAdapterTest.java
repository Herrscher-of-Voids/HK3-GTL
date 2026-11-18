package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.AEKeyType;
import appeng.api.stacks.GenericStack;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** 使用实际AE15计划类型核验守恒与long边界，不启动游戏或模拟CPU完成。 */
public final class Hk3AeExactPlanAdapterTest {
    private static final Hk3ExactPlanner.Limits LIMITS = new Hk3ExactPlanner.Limits(100, 100);
    private static final TestType TYPE = new TestType(8);
    private static int checks;

    public static void main(String[] args) throws Exception {
        conservation();
        unsupportedAndOverflow();
        stockAndOutputOverflow();
        treeAccounting();
        System.out.println("AE15原生计划桥接离线核验通过：" + checks + "项；未启动游戏或执行CPU。");
    }

    private static void conservation() throws Exception {
        Key ore = key("ore"), middle = key("middle"), target = key("target");
        Pattern refine = new Pattern("refine"), assemble = new Pattern("assemble");
        var recipes = graph(recipe(refine, Map.of(ore, n(2)), middle, n(4)),
                recipe(assemble, Map.of(middle, n(3)), target, n(1)));
        var snapshot = snapshot(target, Map.of(ore, n(100), middle, n(3)), recipes, n(3));
        var result = snapshot.plan(n(2), () -> false);
        var plan = Hk3AeExactPlanAdapter.toNative(snapshot, 2, result).orElseThrow();
        check(plan.finalOutput().what().equals(target) && plan.finalOutput().amount() == 2, "新增成品目标原样保留");
        check(plan.usedItems().get(ore) == 2 && plan.usedItems().get(middle) == 3, "库存仅消费一次且含中间件");
        check(plan.usedItems().get(target) == 0, "现有成品不能顶替新增订单");
        check(plan.patternTimes().get(refine) == 1 && plan.patternTimes().get(assemble) == 2, "原生样板次数与批量取整一致");
        check(result.surplus().equals(Map.of(middle, n(1))), "四个新中间件加三库存减六投料剩一");
        check(plan.emittedItems().isEmpty() && plan.missingItems().isEmpty() && !plan.simulation(), "真实计划未伪造发信器或缺料成功");
        check(plan.bytes() == 37, "字节保留三树节点与全部请求流量");
        check(snapshot.inventory().equals(Map.of(ore, n(100), middle, n(3))), "规划不修改捕获库存");
        var changedStock = snapshot(target, Map.of(ore, n(1)), recipes, n(3));
        check(snapshot.sameRecipes(changedStock), "重捕库存变化不改变样板身份");
        var changedRecipe = snapshot(target, Map.of(), graph(recipe(refine, Map.of(ore, n(3)), middle, n(4)),
                recipe(assemble, Map.of(middle, n(3)), target, n(1))), n(3));
        check(!snapshot.sameRecipes(changedRecipe), "输入数量变化拒绝复用旧图");
        var missing = changedStock.plan(n(2), () -> false);
        check(!missing.successful() && Hk3AeExactPlanAdapter.toNative(changedStock, 2, missing).isEmpty(), "缺料诊断不能生成可提交计划");
    }

    private static void unsupportedAndOverflow() throws Exception {
        Key ore = key("ore2"), target = key("target2");
        Pattern pattern = new Pattern("large");
        var recipes = graph(recipe(pattern, Map.of(ore, n(1)), target, n(1)));
        var large = snapshot(target, Map.of(ore, BigInteger.ONE.shiftLeft(100)), recipes, n(2));
        var result = large.plan(BigInteger.ONE.shiftLeft(100), () -> false);
        check(result.successful() && Hk3AeExactPlanAdapter.estimateBytes(large, BigInteger.ONE.shiftLeft(100), result)
                .compareTo(BigInteger.valueOf(Long.MAX_VALUE)) > 0, "大数字节估计未截断为long");
        check(Hk3AeExactPlanAdapter.toNative(large, Long.MAX_VALUE, result).isEmpty(), "超过原生计数拒绝适配");
        check(Hk3AeExactPlanAdapter.toNative(large, 0, result).isEmpty(), "零批次不能提交");

        TestType hugeByte = new TestType(Integer.MAX_VALUE);
        Key bigMiddle = new Key("big_middle", hugeByte), bigTarget = new Key("big_target", hugeByte);
        Pattern massive = new Pattern("massive"), finish = new Pattern("finish");
        var overflowGraph = graph(recipe(massive, Map.of(ore, n(1)), bigMiddle, n(Long.MAX_VALUE)),
                recipe(finish, Map.of(bigMiddle, n(Long.MAX_VALUE)), bigTarget, n(1)));
        var overflow = snapshot(bigTarget, Map.of(ore, n(1)), overflowGraph, n(3));
        var overflowResult = overflow.plan(n(1), () -> false);
        check(overflowResult.successful(), "大输出逻辑配方仍可精确规划");
        check(Hk3AeExactPlanAdapter.toNative(overflow, 1, overflowResult).isEmpty(), "同类资源进度总和溢出时回退");
    }

    private static void treeAccounting() throws Exception {
        Key ore = key("diamond_ore"), shared = key("shared"), left = key("left"), right = key("right"), target = key("diamond");
        var recipes = graph(recipe(new Pattern("shared"), Map.of(ore, n(1)), shared, n(1)),
                recipe(new Pattern("left"), Map.of(shared, n(1)), left, n(1)),
                recipe(new Pattern("right"), Map.of(shared, n(1)), right, n(1)),
                recipe(new Pattern("diamond"), Map.of(left, n(1), right, n(1)), target, n(1)));
        var count = Hk3AeExactSnapshot.class.getDeclaredMethod("countTreeNodes", AEKey.class, Map.class);
        count.setAccessible(true);
        check(n(7).equals(count.invoke(null, target, recipes)), "共享DAG不偷减未折叠原生树节点容量");
        var cyclic = graph(recipe(new Pattern("cycle_a"), Map.of(left, n(1)), target, n(1)),
                recipe(new Pattern("cycle_b"), Map.of(target, n(1)), left, n(1)));
        check(count.invoke(null, target, cyclic) == null, "循环图拒绝捕获为可提交快照");
    }

    private static void stockAndOutputOverflow() throws Exception {
        TestType compressed = new TestType(Integer.MAX_VALUE);
        Key ore = new Key("merge_ore", compressed), middle = new Key("merge_middle", compressed),
                target = new Key("merge_target", compressed);
        var recipes = graph(recipe(new Pattern("merge_refine"), Map.of(ore, n(1)), middle, n(2)),
                recipe(new Pattern("merge_assemble"), Map.of(middle, n(Long.MAX_VALUE)), target, n(1)));
        var snapshot = snapshot(target, Map.of(ore, n(1), middle, n(Long.MAX_VALUE - 1)), recipes, n(3));
        var result = snapshot.plan(n(1), () -> false);
        check(result.successful(), "初始中间件加小批产出在精确算术下守恒");
        check(Hk3AeExactPlanAdapter.estimateBytes(snapshot, n(1), result).bitLength() < 63,
                "该合并案例不依赖字节超限保护");
        check(Hk3AeExactPlanAdapter.toNative(snapshot, 1, result).isEmpty(),
                "中间件初始MAX减一加两产出会溢出原生库存，必须回退");
    }

    static Hk3AeExactSnapshot batchSnapshot(long stock, long inputPerBatch) throws Exception {
        Key ore = key("batch_ore"), target = key("batch_target");
        return snapshot(target, Map.of(ore, n(stock)),
                graph(recipe(new Pattern("batch_make"), Map.of(ore, n(inputPerBatch)), target, n(1))), n(2));
    }

    static Hk3AeExactSnapshot snapshot(AEKey target, Map<AEKey, BigInteger> inventory,
            Map<AEKey, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> recipes, BigInteger nodes) throws Exception {
        var constructor = Hk3AeExactSnapshot.class.getDeclaredConstructor(AEKey.class, Map.class, Map.class,
                Hk3ExactPlanner.Limits.class, BigInteger.class);
        constructor.setAccessible(true);
        return constructor.newInstance(target, inventory, recipes, LIMITS, nodes);
    }

    @SafeVarargs
    static Map<AEKey, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> graph(
            Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>... recipes) {
        Map<AEKey, List<Hk3ExactPlanner.Recipe<AEKey, IPatternDetails>>> graph = new LinkedHashMap<>();
        for (var recipe : recipes) graph.put(recipe.outputs().keySet().iterator().next(), List.of(recipe));
        for (var recipe : recipes) recipe.inputs().keySet().forEach(key -> graph.putIfAbsent(key, List.of()));
        return graph;
    }

    static Hk3ExactPlanner.Recipe<AEKey, IPatternDetails> recipe(IPatternDetails pattern,
            Map<AEKey, BigInteger> inputs, AEKey output, BigInteger amount) {
        return new Hk3ExactPlanner.Recipe<>(pattern, inputs, Map.of(output, amount), BigInteger.ONE);
    }

    static Key key(String name) { return new Key(name, TYPE); }
    static BigInteger n(long value) { return BigInteger.valueOf(value); }
    private static void check(boolean value, String message) {
        checks++;
        if (!value) throw new AssertionError(message);
    }

    record Pattern(String name) implements IPatternDetails {
        public AEItemKey getDefinition() { throw new UnsupportedOperationException("测试不序列化样板"); }
        public IInput[] getInputs() { return new IInput[0]; }
        public GenericStack[] getOutputs() { return new GenericStack[0]; }
    }

    static final class Key extends AEKey {
        private final String name;
        private final AEKeyType type;
        Key(String name, AEKeyType type) { this.name = name; this.type = type; }
        public AEKeyType getType() { return type; }
        public AEKey dropSecondary() { return this; }
        public CompoundTag toTag() { return new CompoundTag(); }
        public Object getPrimaryKey() { return name; }
        public ResourceLocation getId() { return new ResourceLocation("hk3test", name); }
        public void writeToPacket(FriendlyByteBuf data) { throw new UnsupportedOperationException("测试不联网"); }
        protected Component computeDisplayName() { return Component.literal(name); }
        public void addDrops(long amount, List<ItemStack> drops, Level level, BlockPos pos) {}
    }

    static final class TestType extends AEKeyType {
        private final int perByte;
        TestType(int perByte) { super(new ResourceLocation("hk3test", "resource"), Key.class, null); this.perByte = perByte; }
        public int getAmountPerByte() { return perByte; }
        public AEKey readFromPacket(FriendlyByteBuf input) { throw new UnsupportedOperationException("测试不联网"); }
        public AEKey loadKeyFromTag(CompoundTag tag) { throw new UnsupportedOperationException("测试不读存档"); }
    }
}
