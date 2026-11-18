package com.sirin.hk3gtl.test.research;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3SpectrumAnalysisMachine;
import com.sirin.hk3gtl.common.research.Hk3OutputReceiptDispatch;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.LdcInsnNode;
import org.objectweb.asm.tree.MethodInsnNode;
import org.objectweb.asm.tree.MethodNode;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

/** 执行生产派发器、Liquid入口与Mixin回调；世界、库存和必要HW提交用受控替身，不启动游戏。 */
public final class OutputReceiptDispatchTest {
    private static final String SETTLED = "hk3gtlLiquidOutputSettled";
    private static final String REQUIRED = "hk3gtlLiquidRequiredOutputSettled";
    private static int checks;

    public static void main(String[] args) throws Exception {
        net.minecraft.SharedConstants.tryDetectVersion();
        dispatcher();
        liquidStages();
        setupNewBatch();
        actualMixinFinish();
        actualSamplingAndSpectrum();
        productionWiring();
        System.out.println("输出回执隔离：" + checks + "项检查通过");
    }

    private static void dispatcher() {
        Hk3OutputReceiptDispatch.dispatch(false, null, null, null, null);
        check(true, "false与模拟路径不能读取任一回调");
        var events = new ArrayList<String>();
        Hk3OutputReceiptDispatch.dispatch(true, () -> { events.add("资格"); return false; },
                () -> events.add("必要"), () -> events.add("回执"), e -> events.add("日志"));
        check(events.equals(List.of("资格")), "不符合资格不提交必要输出与回执");
        events.clear();
        Hk3OutputReceiptDispatch.dispatch(true, () -> { events.add("资格"); return true; },
                () -> events.add("必要"), () -> events.add("回执"), e -> events.add("日志"));
        check(events.equals(List.of("资格", "必要", "回执")), "正常顺序保留资格、必要输出、回执");
        var failure = new IllegalStateException("受控回执失败");
        var fatal = new AssertionError("受控不可恢复错误");
        int[] called = {0};
        expect(failure, () -> Hk3OutputReceiptDispatch.dispatch(true, () -> { throw failure; },
                () -> called[0]++, () -> called[0]++, e -> called[0]++));
        check(called[0] == 0, "资格异常外抛且不继续必要输出、回执或日志");
        expect(failure, () -> Hk3OutputReceiptDispatch.dispatch(true, () -> true,
                () -> { throw failure; }, () -> called[0]++, e -> called[0]++));
        check(called[0] == 0, "必要输出异常外抛且不执行回执、日志");
        Hk3OutputReceiptDispatch.dispatch(true, () -> { throw failure; }, e -> {
            check(e == failure, "日志接收原始回执异常");
            throw new IllegalStateException("受控日志失败");
        });
        check(true, "回执与日志RuntimeException均不截断收尾");
        expect(fatal, () -> Hk3OutputReceiptDispatch.dispatch(true, () -> { throw fatal; }, e -> called[0]++));
        check(called[0] == 0, "回执Error不得进入Runtime日志通道");
        expect(fatal, () -> Hk3OutputReceiptDispatch.dispatch(true, () -> { throw failure; }, e -> { throw fatal; }));
        expect(fatal, () -> Hk3OutputReceiptDispatch.dispatch(true, () -> { throw fatal; }, () -> {}, () -> {}, e -> {}));
        expect(fatal, () -> Hk3OutputReceiptDispatch.dispatch(true, () -> true, () -> { throw fatal; }, () -> {}, e -> {}));
        for (int bad = -1; bad < 4; bad++) {
            events.clear();
            for (int channel = 0; channel < 4; channel++) {
                final int at = channel, failing = bad;
                Hk3OutputReceiptDispatch.dispatch(true, () -> {
                    events.add("通道" + at);
                    if (at == failing) throw failure;
                }, e -> {
                    check(e == failure, "各通道保留自己的原始异常");
                    events.add("故障" + at);
                });
            }
            var expected = new ArrayList<String>();
            for (int channel = 0; channel < 4; channel++) {
                expected.add("通道" + channel);
                if (channel == bad) expected.add("故障" + channel);
            }
            check(events.equals(expected), "一个旁注失败不阻断后续独立通道");
        }
    }

    private static void liquidStages() throws Exception {
        Machine machine = machine();
        GTRecipe recipe = recipe("liquid");
        var failure = new IllegalStateException("受控机器回执失败");
        machine.observerFailure = failure;
        machine.onLiquidOutputSettled(recipe);
        check(machine.requiredCalls == 1 && machine.credit == 7 && machine.observerCalls == 1,
                "真实Liquid先完成必要结算，再执行回执");
        check(recipe.data.getBoolean(REQUIRED) && !recipe.data.getBoolean(SETTLED),
                "必要阶段成功保留，回执失败不能写SETTLED");
        machine.onLiquidOutputSettled(recipe);
        check(machine.requiredCalls == 1 && machine.credit == 7 && machine.observerCalls == 2,
                "同批回调重入不重复必要HW结算，但允许重试未完成回执");
        machine.observerFailure = null;
        machine.onLiquidOutputSettled(recipe);
        check(recipe.data.getBoolean(SETTLED) && machine.credit == 7 && machine.observerCalls == 3,
                "回执恢复后才能写SETTLED");
        machine.onLiquidOutputSettled(recipe);
        check(machine.requiredCalls == 1 && machine.observerCalls == 3, "完整结算后再次回调零副作用");
        check(machine.events.subList(0, 3).equals(List.of("资格", "必要", "回执")), "真实Liquid执行顺序");

        Machine requiredFailed = machine();
        requiredFailed.requiredFailure = failure;
        GTRecipe unpaid = recipe("required_failure");
        expect(failure, () -> requiredFailed.onLiquidOutputSettled(unpaid));
        check(requiredFailed.credit == 0 && requiredFailed.observerCalls == 0
                        && !unpaid.data.getBoolean(REQUIRED) && !unpaid.data.getBoolean(SETTLED),
                "必要结算失败不授信、不记完成、不执行回执");
        requiredFailed.requiredFailure = null;
        requiredFailed.onLiquidOutputSettled(unpaid);
        check(requiredFailed.credit == 7 && unpaid.data.getBoolean(SETTLED), "必要结算失败后可在真实成功时重试");

        Machine gateFailed = machine();
        gateFailed.gateFailure = failure;
        GTRecipe gated = recipe("gate_failure");
        expect(failure, () -> gateFailed.onLiquidOutputSettled(gated));
        check(gateFailed.requiredCalls == 0 && gateFailed.observerCalls == 0 && gated.data.isEmpty(),
                "真实Liquid门槛读取失败外抛，不伪造任何阶段或证据");
        Machine denied = machine(); denied.observation = false;
        denied.onLiquidOutputSettled(recipe("denied"));
        denied.onLiquidOutputSettled(null);
        check(denied.requiredCalls == 0 && denied.observerCalls == 0, "无观察资格或null配方不结算");
        Machine unformed = machine(); unformed.formed = false;
        unformed.onLiquidOutputSettled(recipe("unformed"));
        check(unformed.requiredCalls == 0 && unformed.observerCalls == 0, "未成型机器不能生成回执");
        Machine fatalMachine = machine();
        var fatal = new AssertionError("受控机器Error");
        fatalMachine.observerFailure = fatal;
        GTRecipe fatalRecipe = recipe("fatal");
        expect(fatal, () -> fatalMachine.onLiquidOutputSettled(fatalRecipe));
        check(fatalRecipe.data.getBoolean(REQUIRED) && !fatalRecipe.data.getBoolean(SETTLED),
                "真实回执Error外抛，不伪造SETTLED");
    }

    private static void setupNewBatch() throws Exception {
        Machine machine = machine();
        GTRecipe old = recipe("new_batch");
        old.data.putBoolean(REQUIRED, true); old.data.putBoolean(SETTLED, true);
        old.data.putString("夹具标记", "原元数据");
        Machine.Logic logic = allocate(Machine.Logic.class);
        var field = RecipeLogic.class.getDeclaredField("machine"); field.setAccessible(true); field.set(logic, machine);
        logic.setupRecipe(old);
        GTRecipe fresh = logic.captured;
        check(fresh != null && fresh != old && fresh.data != old.data, "实际ProcessLogic.setupRecipe复制新批次");
        check(!fresh.data.getBoolean(REQUIRED) && !fresh.data.getBoolean(SETTLED), "实际setup清除新批两阶段标记");
        check(old.data.getBoolean(REQUIRED) && old.data.getBoolean(SETTLED), "setup不能清除上一批次标记");
        check(fresh.data.getString("夹具标记").equals("原元数据"), "setup保留其他原元数据");
        machine.onLiquidOutputSettled(fresh);
        check(machine.credit == 7 && fresh.data.getBoolean(SETTLED), "实际新批副本可以正常再次必要结算");
    }

    private static void actualMixinFinish() throws Exception {
        Machine machine = machine();
        machine.eggFailure = new IllegalStateException("受控工业彩蛋旁注失败");
        machine.observerFailure = new IllegalStateException("受控Liquid旁注失败");
        GTRecipe recipe = recipe("mixin_finish");
        invokeMixin(machine, recipe, false);
        check(machine.events.isEmpty() && recipe.data.isEmpty(), "真实Mixin返回false时不触发任何读取或回执");
        int outputs = 0, progress = 1; boolean active = true;
        // 保留GTL输出→回调→复位的先后关系；不是服务器tick或库存实测。
        for (int tick = 0; tick < 2; tick++) {
            if (active && progress == 1) {
                outputs++;
                invokeMixin(machine, recipe, true);
                progress = 0; active = false;
            }
        }
        check(outputs == 1 && progress == 0 && !active, "真实Mixin旁注Runtime失败后GTL式收尾继续，第二tick不重复输出");
        check(machine.events.equals(List.of("彩蛋", "资格", "必要", "回执")), "真实Mixin彩蛋失败后仍执行Liquid必要结算及旁注");
        check(machine.credit == 7 && recipe.data.getBoolean(REQUIRED) && !recipe.data.getBoolean(SETTLED),
                "真实Mixin失败回执不伪造完成，必要结算仅一次");
    }

    private static void actualSamplingAndSpectrum() throws Exception {
        Hk3HonkaiAbsorptionMachine sampling = allocate(Hk3HonkaiAbsorptionMachine.class);
        sampling.onSamplingOutputSettled(recipe(Hk3HonkaiAbsorptionMachine.SAMPLING.getPath()));
        check(true, "实际采样入口隔离无持有者夹具的门槛与日志Runtime失败");
        Hk3SpectrumAnalysisMachine spectrum = allocate(Hk3SpectrumAnalysisMachine.class);
        var formed = com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine.class.getDeclaredField("isFormed");
        formed.setAccessible(true); formed.setBoolean(spectrum, true);
        spectrum.onSpectrumOutputSettled(recipe(Hk3SpectrumAnalysisMachine.INITIAL.getPath()));
        check(true, "实际光谱入口隔离无持有者夹具的门槛与日志Runtime失败");
    }

    private static void productionWiring() throws Exception {
        MethodNode mixin = method("com/sirin/hk3gtl/mixin/Hk3ResearchOutputMixin", "hk3gtl$recordSampling");
        var calls = new ArrayList<String>();
        for (var instruction : mixin.instructions) if (instruction instanceof MethodInsnNode call
                && (call.name.equals("dispatch") || call.name.endsWith("OutputSettled"))) calls.add(call.name);
        check(calls.equals(List.of("dispatch", "onSamplingOutputSettled", "onSpectrumOutputSettled", "onLiquidOutputSettled")),
                "已编译Mixin接线保留四通道原次序");
        String process = "com/sirin/hk3gtl/common/machine/research/Hk3LiquidProcessMachine$ProcessLogic";
        for (String name : List.of("setupRecipe", "buildFinalNormalRecipe")) {
            var keys = new ArrayList<String>();
            for (var instruction : method(process, name).instructions) if (instruction instanceof LdcInsnNode constant
                    && (REQUIRED.equals(constant.cst) || SETTLED.equals(constant.cst))) keys.add((String) constant.cst);
            check(keys.contains(REQUIRED) && keys.contains(SETTLED), "已编译单批与合并新批均有两阶段清理：" + name);
        }
        MethodNode required = method("com/sirin/hk3gtl/common/machine/energy/Hk3HonkaiNetworkInjectorMachine", "onRequiredProcessOutput");
        boolean insert = false;
        for (var instruction : required.instructions) if (instruction instanceof MethodInsnNode call
                && call.owner.endsWith("HonkaiWirelessNetwork") && call.name.equals("insert")) insert = true;
        check(insert, "实际注入器HW入账接在必要结算钩子，不能当旁注吞掉");
        for (String type : List.of("Hk3HonkaiAbsorptionMachine", "Hk3SpectrumAnalysisMachine")) {
            MethodNode fallback = method("com/sirin/hk3gtl/common/machine/research/" + type + "$1", "handleRecipeIO");
            boolean safeEntry = false;
            for (var instruction : fallback.instructions) if (instruction instanceof MethodInsnNode call
                    && call.name.endsWith("OutputSettled")) safeEntry = true;
            check(safeEntry, "已编译fallback仍共用安全输出入口：" + type);
        }
    }

    private static MethodNode method(String internal, String name) throws Exception {
        var node = new ClassNode();
        try (var stream = OutputReceiptDispatchTest.class.getClassLoader().getResourceAsStream(internal + ".class")) {
            if (stream == null) throw new AssertionError("缺少已编译生产类：" + internal);
            new ClassReader(stream).accept(node, 0);
        }
        return node.methods.stream().filter(method -> method.name.equals(name)).findFirst().orElseThrow();
    }

    private static void invokeMixin(IRecipeLogicMachine machine, GTRecipe recipe, boolean success) throws Exception {
        var method = Class.forName("com.sirin.hk3gtl.mixin.Hk3ResearchOutputMixin").getDeclaredMethod(
                "hk3gtl$recordSampling", IRecipeLogicMachine.class, GTRecipe.class, CallbackInfoReturnable.class);
        method.setAccessible(true);
        try { method.invoke(null, machine, recipe, new CallbackInfoReturnable<Boolean>("handleRecipeOutput", false, success)); }
        catch (InvocationTargetException failure) { raise(failure.getCause()); throw failure; }
    }

    private static GTRecipe recipe(String path) {
        return new GTRecipe(null, new ResourceLocation("hk3gtl", path),
                new HashMap<>(), new HashMap<>(), new HashMap<>(), new HashMap<>(),
                new HashMap<>(), new HashMap<>(), new HashMap<>(), new HashMap<>(),
                new ArrayList<>(), new ArrayList<>(), new CompoundTag(), 20, false);
    }

    private static Machine machine() throws Exception {
        Machine machine = allocate(Machine.class); machine.events = new ArrayList<>();
        machine.observation = true; machine.formed = true; return machine;
    }

    private static <T> T allocate(Class<T> type) throws Exception {
        var field = sun.misc.Unsafe.class.getDeclaredField("theUnsafe"); field.setAccessible(true);
        return type.cast(((sun.misc.Unsafe) field.get(null)).allocateInstance(type));
    }

    private static void expect(Throwable expected, Runnable work) {
        try { work.run(); } catch (Throwable failure) { check(failure == expected, "原始异常必须保持身份外抛"); return; }
        throw new AssertionError("异常不应被吞掉：" + expected);
    }

    private static void raise(Throwable failure) {
        if (failure instanceof RuntimeException runtime) throw runtime;
        if (failure instanceof Error error) throw error;
    }

    private static void check(boolean value, String message) {
        checks++; if (!value) throw new AssertionError(message);
    }

    public static class Machine extends Hk3LiquidProcessMachine {
        List<String> events;
        boolean observation, formed;
        int requiredCalls, observerCalls, credit;
        Throwable gateFailure, requiredFailure, observerFailure, eggFailure;
        public Machine() { super(null); }
        @Override protected boolean hasObservationData() { events.add("资格"); raise(gateFailure); return observation; }
        @Override public boolean isFormed() { return formed; }
        @Override public boolean beforeWorking(GTRecipe recipe) { return true; }
        @Override public BlockPos getPos() { return BlockPos.ZERO; }
        @Override public Machine self() { events.add("彩蛋"); raise(eggFailure); return this; }
        @Override protected void onRequiredProcessOutput(GTRecipe recipe) {
            requiredCalls++; events.add("必要"); raise(requiredFailure); credit += 7;
        }
        @Override protected void onProcessOutput(GTRecipe recipe) {
            observerCalls++; events.add("回执"); raise(observerFailure);
        }
        public static final class Logic extends ProcessLogic {
            GTRecipe captured;
            public Logic(Machine machine) { super(machine); }
            @Override public boolean handleFuelRecipe() { return true; }
            @Override protected boolean handleRecipeIO(GTRecipe recipe, IO io) { captured = recipe; return false; }
        }
    }
}
