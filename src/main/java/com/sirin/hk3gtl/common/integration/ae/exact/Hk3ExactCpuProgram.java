package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.crafting.IPatternDetails;
import appeng.api.stacks.AEItemKey;
import appeng.api.crafting.PatternDetailsHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.Level;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

/** CPU 与原生任务一起保存压缩见证；损坏或次数不符时由调用方冻结。 */
public final class Hk3ExactCpuProgram {
    public static final String NBT = "hk3ExactProgram";
    private static final int MAX_PARTS = 8192;
    private final List<Hk3ExactPlanner.Step<IPatternDetails>> execution;
    private final Hk3ExactProgramCursor<IPatternDetails> cursor;
    private final long targetSeed;

    public Hk3ExactCpuProgram(Hk3ExactProgramPlan plan) {
        this(plan.execution(), new Hk3ExactProgramCursor<>(plan.execution()), plan.targetSeed());
    }

    private Hk3ExactCpuProgram(List<Hk3ExactPlanner.Step<IPatternDetails>> execution,
            Hk3ExactProgramCursor<IPatternDetails> cursor, long targetSeed) {
        this.execution = List.copyOf(execution); this.cursor = cursor; this.targetSeed = targetSeed;
        validate(execution);
        if (targetSeed < 0)
            throw new IllegalArgumentException("CPU执行程序范围无效");
    }

    static void validate(List<Hk3ExactPlanner.Step<IPatternDetails>> execution) {
        if (execution.isEmpty() || execution.size() > MAX_PARTS)
            throw new IllegalArgumentException("CPU执行程序长度无效");
        int references = 0;
        for (var step : execution) {
            references = Math.addExact(references, step.recipes().size());
            if (references > MAX_PARTS || step.repetitions().signum() <= 0)
                throw new IllegalArgumentException("CPU执行程序引用数无效");
            step.repetitions().longValueExact();
        }
    }

    public Hk3ExactProgramCursor<IPatternDetails> cursor() { return cursor; }
    public long targetSeed() { return targetSeed; }

    public CompoundTag write() {
        return write(pattern -> pattern.getDefinition().toTag());
    }

    CompoundTag write(Function<IPatternDetails, CompoundTag> encode) {
        CompoundTag tag = new CompoundTag();
        tag.putInt("version", 3);
        tag.putLong("seed", targetSeed);
        Map<IPatternDetails, Integer> indices = new LinkedHashMap<>();
        execution.forEach(step -> step.recipes().forEach(pattern -> indices.computeIfAbsent(pattern, ignored -> indices.size())));
        ListTag patterns = new ListTag();
        indices.keySet().forEach(pattern -> {
            CompoundTag encoded = encode.apply(Hk3ExactBoundPattern.original(pattern));
            encoded.putBoolean(Hk3ExactBoundPattern.MARKER, pattern instanceof Hk3ExactBoundPattern);
            encoded.putBoolean(Hk3ExactScaledPattern.MARKER, pattern instanceof Hk3ExactScaledPattern);
            if (pattern instanceof Hk3ExactBoundPattern bound) bound.writeSelection(encoded);
            if (pattern instanceof Hk3ExactScaledPattern scaled) scaled.writeSelection(encoded);
            patterns.add(encoded);
        });
        tag.put("patterns", patterns);
        ListTag parts = new ListTag();
        for (var step : execution) {
            CompoundTag part = new CompoundTag();
            part.putLong("repeat", step.repetitions().longValueExact());
            part.putIntArray("recipes", step.recipes().stream().mapToInt(indices::get).toArray());
            parts.add(part);
        }
        tag.put("steps", parts);
        var position = cursor.position();
        tag.putInt("step", position.step()); tag.putInt("recipe", position.recipe());
        tag.putLong("remaining", position.repetitions().longValueExact()); tag.putBoolean("waiting", position.waiting());
        return tag;
    }

    public static Hk3ExactCpuProgram read(CompoundTag tag, Level level,
            Map<IPatternDetails, BigInteger> nativeRemaining, long finalAmount) {
        Map<AEItemKey, IPatternDetails> canonical = new LinkedHashMap<>();
        nativeRemaining.keySet().forEach(pattern -> canonical.put(pattern.getDefinition(), pattern));
        return read(tag, encoded -> {
            AEItemKey definition = AEItemKey.fromTag(encoded);
            IPatternDetails pattern = canonical.get(definition);
            if (pattern == null && definition != null) pattern = PatternDetailsHelper.decodePattern(definition, level);
            return pattern == null ? null : Hk3ExactScaledPattern.readSelection(
                    Hk3ExactBoundPattern.readSelection(pattern, encoded, level), encoded);
        }, nativeRemaining, finalAmount);
    }

    static Hk3ExactCpuProgram read(CompoundTag tag, Function<CompoundTag, IPatternDetails> decode,
            Map<IPatternDetails, BigInteger> nativeRemaining, long finalAmount) {
        int version = tag.getInt("version");
        if (version != 1 && version != 2 && version != 3 || !tag.contains("seed", Tag.TAG_LONG)
                || !tag.contains("step", Tag.TAG_INT) || !tag.contains("recipe", Tag.TAG_INT)
                || !tag.contains("remaining", Tag.TAG_LONG) || !tag.contains("waiting", Tag.TAG_BYTE))
            throw new IllegalArgumentException("CPU执行程序字段不完整");
        long seed = tag.getLong("seed");
        if (seed < 0 || finalAmount <= 0) throw new IllegalArgumentException("CPU目标与种子损坏");
        Math.addExact(seed, finalAmount);
        ListTag storedPatterns = tag.getList("patterns", Tag.TAG_COMPOUND);
        ListTag storedSteps = tag.getList("steps", Tag.TAG_COMPOUND);
        if (storedPatterns.isEmpty() || storedPatterns.size() > MAX_PARTS
                || storedSteps.isEmpty() || storedSteps.size() > MAX_PARTS)
            throw new IllegalArgumentException("CPU执行程序长度无效");
        List<IPatternDetails> patterns = new ArrayList<>();
        for (int i = 0; i < storedPatterns.size(); i++) {
            CompoundTag encoded = storedPatterns.getCompound(i);
            if (version >= 2 && !encoded.contains(Hk3ExactBoundPattern.MARKER, Tag.TAG_BYTE)
                    || version == 3 && !encoded.contains(Hk3ExactScaledPattern.MARKER, Tag.TAG_BYTE))
                throw new IllegalArgumentException("CPU样板绑定标记缺失");
            IPatternDetails pattern = decode.apply(encoded);
            if (pattern == null) throw new IllegalArgumentException("CPU执行程序样板无法解析");
            patterns.add(pattern);
        }
        List<Hk3ExactPlanner.Step<IPatternDetails>> parts = new ArrayList<>();
        int references = 0;
        for (int i = 0; i < storedSteps.size(); i++) {
            CompoundTag part = storedSteps.getCompound(i);
            if (!part.contains("repeat", Tag.TAG_LONG) || !part.contains("recipes", Tag.TAG_INT_ARRAY))
                throw new IllegalArgumentException("CPU执行步骤字段损坏");
            int[] refs = part.getIntArray("recipes");
            references += refs.length;
            if (refs.length == 0 || references > MAX_PARTS || part.getLong("repeat") <= 0)
                throw new IllegalArgumentException("CPU执行步骤超出范围");
            List<IPatternDetails> ordered = new ArrayList<>();
            for (int ref : refs) {
                if (ref < 0 || ref >= patterns.size()) throw new IllegalArgumentException("CPU样板索引损坏");
                ordered.add(patterns.get(ref));
            }
            parts.add(new Hk3ExactPlanner.Step<>(ordered, BigInteger.valueOf(part.getLong("repeat"))));
        }
        var cursor = new Hk3ExactProgramCursor<>(parts, new Hk3ExactProgramCursor.Position(tag.getInt("step"),
                tag.getInt("recipe"), BigInteger.valueOf(tag.getLong("remaining")), tag.getBoolean("waiting")));
        if (!Hk3ExactBoundPattern.nativeCounts(cursor.remainingCounts()).equals(nativeRemaining))
            throw new IllegalArgumentException("CPU执行游标与原生剩余任务不一致");
        return new Hk3ExactCpuProgram(parts, cursor, seed);
    }
}

