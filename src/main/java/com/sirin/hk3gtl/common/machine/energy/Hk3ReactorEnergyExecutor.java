package com.sirin.hk3gtl.common.machine.energy;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

import java.math.BigInteger;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;

/**
 * I19-I22 可保存的纯计算批次游标；不直接写机器仓、账户或世界状态。
 */
public final class Hk3ReactorEnergyExecutor {
    private static final int SCHEMA = 1;
    private static final Set<String> BATCH_KEYS = Set.of(
            "schema", "batchId", "owner", "role", "recipeId", "elapsedTicks", "totalTicks",
            "generatedEu", "completed");

    private Hk3ReactorEnergyExecutor() {
    }

    public record Batch(UUID batchId, UUID owner, String role, String recipeId, int elapsedTicks,
                        int totalTicks, BigInteger generatedEu, boolean completed) {
        public Batch {
            Objects.requireNonNull(batchId, "缺少反应堆批次身份");
            Objects.requireNonNull(owner, "缺少反应堆归属");
            Objects.requireNonNull(role, "缺少反应堆职责");
            Objects.requireNonNull(recipeId, "缺少反应堆配方");
            Objects.requireNonNull(generatedEu, "缺少反应堆产电累计");
            Hk3ReactorEnergyProfile profile = Hk3ReactorEnergyProfile.get(recipeId);
            if (elapsedTicks < 0 || totalTicks <= 0 || elapsedTicks > totalTicks || generatedEu.signum() < 0
                    || completed != (elapsedTicks == totalTicks)
                    || !profile.role().equals(role) || profile.totalTicks() != totalTicks
                    || !profile.euPerTick().multiply(BigInteger.valueOf(elapsedTicks)).equals(generatedEu)) {
                throw new IllegalArgumentException("反应堆批次状态无效");
            }
        }

        public CompoundTag toNbt() {
            CompoundTag tag = new CompoundTag();
            tag.putInt("schema", SCHEMA);
            tag.putUUID("batchId", batchId);
            tag.putUUID("owner", owner);
            tag.putString("role", role);
            tag.putString("recipeId", recipeId);
            tag.putInt("elapsedTicks", elapsedTicks);
            tag.putInt("totalTicks", totalTicks);
            tag.putString("generatedEu", generatedEu.toString());
            tag.putBoolean("completed", completed);
            return tag;
        }

        public static Batch fromNbt(CompoundTag tag) {
            if (tag == null || !tag.getAllKeys().equals(BATCH_KEYS))
                throw new IllegalArgumentException("反应堆批次字段缺失或包含未知字段");
            if (!tag.contains("schema", Tag.TAG_INT) || !tag.contains("elapsedTicks", Tag.TAG_INT)
                    || !tag.contains("totalTicks", Tag.TAG_INT) || !tag.contains("role", Tag.TAG_STRING)
                    || !tag.contains("recipeId", Tag.TAG_STRING) || !tag.contains("generatedEu", Tag.TAG_STRING)
                    || !tag.contains("completed", Tag.TAG_BYTE)
                    || tag.getByte("completed") != 0 && tag.getByte("completed") != 1)
                throw new IllegalArgumentException("反应堆批次字段类型或完成标记损坏");
            if (tag.getInt("schema") != SCHEMA || !tag.hasUUID("batchId") || !tag.hasUUID("owner"))
                throw new IllegalArgumentException("反应堆批次版本或身份损坏");
            try {
                return new Batch(tag.getUUID("batchId"), tag.getUUID("owner"), tag.getString("role"),
                        tag.getString("recipeId"), tag.getInt("elapsedTicks"), tag.getInt("totalTicks"),
                        new BigInteger(tag.getString("generatedEu")), tag.getBoolean("completed"));
            } catch (RuntimeException e) {
                throw new IllegalArgumentException("反应堆批次数值损坏", e);
            }
        }
    }

    /** true 表示完整接受本次金额，false 必须表示未发生任何外部余额变更。 */
    @FunctionalInterface
    public interface OutputSink {
        boolean accept(BigInteger eu);
    }

    public static Batch start(UUID owner, String recipeId) {
        Hk3ReactorEnergyProfile profile = Hk3ReactorEnergyProfile.get(recipeId);
        return new Batch(UUID.randomUUID(), Objects.requireNonNull(owner, "反应堆归属不能为空"), profile.role(),
                profile.recipeId(), 0, profile.totalTicks(), BigInteger.ZERO, false);
    }

    /** 返回更新游标供调用方保存；外部输出与SavedData并非原子事务，因此不提供崩溃后exactly-once保证。 */
    public static Batch advance(Batch batch, int ticks, OutputSink sink) {
        Objects.requireNonNull(batch, "反应堆批次不能为空");
        Objects.requireNonNull(sink, "反应堆输出端不能为空");
        Hk3ReactorEnergyProfile profile = Hk3ReactorEnergyProfile.get(batch.recipeId());
        if (!profile.role().equals(batch.role()) || batch.totalTicks() != profile.totalTicks())
            throw new IllegalArgumentException("反应堆批次与现行配方合同不一致");
        if (ticks < 0) throw new IllegalArgumentException("推进 tick 不能为负数");
        if (batch.completed() || ticks == 0) return batch;
        int acceptedTicks = Math.min(ticks, profile.totalTicks() - batch.elapsedTicks());
        BigInteger amount = profile.euPerTick().multiply(BigInteger.valueOf(acceptedTicks));
        if (!sink.accept(amount)) return batch;
        int nextTicks = batch.elapsedTicks() + acceptedTicks;
        return new Batch(batch.batchId(), batch.owner(), batch.role(), batch.recipeId(), nextTicks,
                batch.totalTicks(), batch.generatedEu().add(amount), nextTicks == batch.totalTicks());
    }

    public static String depletedOutput(String recipeId) {
        return Hk3ReactorEnergyProfile.get(recipeId).plan().outputs().get(0).id();
    }
}
