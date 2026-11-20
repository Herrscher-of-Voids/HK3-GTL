package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.GenericStack;
import appeng.crafting.pattern.AEProcessingPattern;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** 保留原生操作次数，实际投料复用 ExtendedAE Plus 的缩放样板。 */
public final class Hk3ExactScaledPattern implements IPatternDetails {
    static final String MARKER = "hk3ScaledPattern";
    private static final String MULTIPLIER = "hk3ScaleMultiplier";
    private static final String INPUTS = "hk3ScaleInputs";
    private static final String OUTPUTS = "hk3ScaleOutputs";
    private static final String SOURCE = "hk3ScaleSource";
    private static final String ADVANCED_PROCESSING = "net.pedroksl.advanced_ae.common.patterns.AdvProcessingPattern";
    private static final Access ACCESS = access();
    private record Access(Method enabled, Method limit, Method create, Object config, Field globalLimit) {}
    private final AEProcessingPattern source;
    private final long multiplier;
    private final IPatternDetails delegate;

    private Hk3ExactScaledPattern(AEProcessingPattern source, long multiplier) {
        this.source = source;
        this.multiplier = multiplier;
        try {
            delegate = (IPatternDetails) ACCESS.create().invoke(null, source, multiplier);
            if (source.getClass().getName().equals(ADVANCED_PROCESSING)
                    && (!delegate.getClass().getName().equals("com.extendedae_plus.api.crafting.ScaledProcessingPatternAdv")
                        || !Objects.equals(source.getClass().getMethod("getDirectionMap").invoke(source),
                            delegate.getClass().getMethod("getDirectionMap").invoke(delegate))))
                throw new IllegalArgumentException("高级缩放样板的方向映射未保留");
        } catch (ReflectiveOperationException failure) {
            throw new IllegalArgumentException("原生缩放样板创建失败", failure);
        }
        var baseInputs = source.getInputs();
        var scaledInputs = delegate.getInputs();
        var baseOutputs = source.getOutputs();
        var scaledOutputs = delegate.getOutputs();
        if (baseInputs.length != scaledInputs.length || baseOutputs.length != scaledOutputs.length)
            throw new IllegalArgumentException("原生缩放槽位已改变");
        for (int i = 0; i < baseInputs.length; i++)
            if (Math.multiplyExact(baseInputs[i].getMultiplier(), multiplier) != scaledInputs[i].getMultiplier())
                throw new IllegalArgumentException("原生缩放输入倍率不一致");
        for (int i = 0; i < baseOutputs.length; i++)
            if (!new GenericStack(baseOutputs[i].what(), Math.multiplyExact(baseOutputs[i].amount(), multiplier))
                    .equals(scaledOutputs[i])) throw new IllegalArgumentException("原生缩放产物不一致");
    }

    private static Access access() {
        try {
            Method enabled = AEProcessingPattern.class.getMethod("eap$allowScaling");
            Method limit = AEProcessingPattern.class.getMethod("eap$getMultiplierLimit");
            Method create = Class.forName("com.extendedae_plus.util.smartDoubling.PatternScaler")
                    .getMethod("createScaled", AEProcessingPattern.class, long.class);
            Class<?> config = Class.forName("com.extendedae_plus.config.ModConfig");
            return new Access(enabled, limit, create, config.getField("INSTANCE").get(null),
                    config.getField("smartScalingMaxMultiplier"));
        } catch (ReflectiveOperationException absent) {
            return null;
        }
    }

    static boolean processing(IPatternDetails pattern) {
        return pattern.getClass() == AEProcessingPattern.class
                || pattern.getClass().getName().equals(ADVANCED_PROCESSING)
                    && pattern.getClass().getSuperclass() == AEProcessingPattern.class;
    }

    static boolean enabled(IPatternDetails pattern) {
        if (ACCESS == null || !processing(pattern)) return false;
        try {
            return Boolean.TRUE.equals(ACCESS.enabled().invoke(pattern));
        } catch (ReflectiveOperationException failure) {
            throw new IllegalArgumentException("原生缩放许可不可读", failure);
        }
    }

    static boolean supports(IPatternDetails pattern) {
        if (ACCESS != null) return true;
        try {
            return !Boolean.TRUE.equals(pattern.getClass().getMethod("eap$allowScaling").invoke(pattern));
        } catch (NoSuchMethodException absent) {
            return true;
        } catch (ReflectiveOperationException failure) {
            return false;
        }
    }

    private static long limit(IPatternDetails pattern, long count) {
        try {
            int configured = ((Number) ACCESS.limit().invoke(pattern)).intValue();
            if (configured <= 0) configured = ACCESS.globalLimit().getInt(ACCESS.config());
            return configured > 0 ? Math.min(count, configured) : count;
        } catch (ReflectiveOperationException failure) {
            throw new IllegalArgumentException("原生缩放上限不可读", failure);
        }
    }

    static List<Hk3ExactPlanner.Step<IPatternDetails>> compress(
            List<Hk3ExactPlanner.Step<IPatternDetails>> execution, Hk3AeExactSnapshot snapshot) {
        List<Hk3ExactPlanner.Step<IPatternDetails>> result = new ArrayList<>();
        for (var step : execution) {
            IPatternDetails pattern = step.recipes().get(0);
            var recipe = snapshot.recipe(pattern);
            if (step.recipes().size() != 1 || !processing(pattern)
                    || !enabled(pattern) || recipe.inputs().keySet().stream().anyMatch(recipe.outputs()::containsKey)) {
                result.add(step);
                continue;
            }
            long count = step.repetitions().longValueExact();
            long scale = limit(pattern, count);
            if (scale <= 1) {
                result.add(step);
                continue;
            }
            result.add(new Hk3ExactPlanner.Step<>(List.of(new Hk3ExactScaledPattern((AEProcessingPattern) pattern, scale)),
                    BigInteger.valueOf(count / scale)));
            long remainder = count % scale;
            if (remainder > 0) result.add(new Hk3ExactPlanner.Step<>(List.of(remainder == 1 ? pattern
                    : new Hk3ExactScaledPattern((AEProcessingPattern) pattern, remainder)), BigInteger.ONE));
        }
        return List.copyOf(result);
    }

    public static IPatternDetails forDispatch(IPatternDetails pattern, long count) {
        if (count <= 1 || !enabled(pattern)) return pattern;
        long scale = limit(pattern, count);
        return scale > 1 ? new Hk3ExactScaledPattern((AEProcessingPattern) pattern, scale) : pattern;
    }

    public IPatternDetails source() { return source; }
    public static long operations(IPatternDetails pattern) {
        return pattern instanceof Hk3ExactScaledPattern scaled ? scaled.multiplier : 1;
    }
    public static IPatternDetails providerPattern(IPatternDetails pattern) {
        return pattern instanceof Hk3ExactScaledPattern scaled ? scaled.delegate : Hk3ExactBoundPattern.original(pattern);
    }

    void writeSelection(CompoundTag tag) {
        tag.putLong(MULTIPLIER, multiplier);
        tag.putString(SOURCE, source.getClass().getName());
        tag.put(INPUTS, inputSignature());
        ListTag outputs = new ListTag();
        for (var output : getOutputs()) outputs.add(GenericStack.writeTag(output));
        tag.put(OUTPUTS, outputs);
    }

    private ListTag inputSignature() {
        ListTag result = new ListTag();
        for (var input : getInputs()) {
            var candidates = input.getPossibleInputs();
            if (candidates.length != 1) throw new IllegalArgumentException("缩放样板不是固定输入");
            CompoundTag entry = GenericStack.writeTag(candidates[0]);
            entry.putLong("multiplier", input.getMultiplier());
            var remainder = input.getRemainingKey(candidates[0].what());
            if (remainder != null) entry.put("remainder", remainder.toTagGeneric());
            result.add(entry);
        }
        return result;
    }

    static IPatternDetails readSelection(IPatternDetails pattern, CompoundTag tag) {
        if (!tag.getBoolean(MARKER)) {
            if (tag.contains(MULTIPLIER) || tag.contains(INPUTS) || tag.contains(OUTPUTS) || tag.contains(SOURCE))
                throw new IllegalArgumentException("缩放样板标记缺失");
            return pattern;
        }
        if (ACCESS == null || !processing(pattern)
                || (tag.contains(SOURCE) ? !pattern.getClass().getName().equals(tag.getString(SOURCE))
                    : pattern.getClass() != AEProcessingPattern.class)
                || !tag.contains(MULTIPLIER, Tag.TAG_LONG) || tag.getLong(MULTIPLIER) <= 1
                || !tag.contains(INPUTS, Tag.TAG_LIST) || !tag.contains(OUTPUTS, Tag.TAG_LIST))
            throw new IllegalArgumentException("缩放样板持久化合同缺失");
        var restored = new Hk3ExactScaledPattern((AEProcessingPattern) pattern, tag.getLong(MULTIPLIER));
        CompoundTag signature = new CompoundTag();
        restored.writeSelection(signature);
        if (!signature.get(INPUTS).equals(tag.get(INPUTS)) || !signature.get(OUTPUTS).equals(tag.get(OUTPUTS)))
            throw new IllegalArgumentException("缩放样板输入或产物已改变");
        return restored;
    }

    @Override public AEItemKey getDefinition() { return source.getDefinition(); }
    @Override public IInput[] getInputs() { return delegate.getInputs(); }
    @Override public GenericStack[] getOutputs() { return delegate.getOutputs(); }
    @Override public boolean equals(Object other) {
        return other instanceof Hk3ExactScaledPattern scaled && source.equals(scaled.source) && multiplier == scaled.multiplier;
    }
    @Override public int hashCode() { return Objects.hash(source, multiplier); }
}
