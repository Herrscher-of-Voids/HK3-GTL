package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.networking.crafting.ICraftingCPU;
import appeng.api.networking.crafting.ICraftingPlan;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

import java.math.BigInteger;
import java.util.function.ToLongFunction;

/** 容量权威来自实际 CPU 方块，long 仅用于未扩展的 AE 接口投影。 */
public final class Hk3ExactCpuCapacity {
    private static final BigInteger LONG_MAX = BigInteger.valueOf(Long.MAX_VALUE);
    private static final String JOB_BYTES = "hk3ExactJobBytes";
    private static final int MAX_SAVED_BYTES = 2048;

    public interface Access {
        BigInteger hk3gtl$storageBytes();
        BigInteger hk3gtl$activeBytes();
    }

    public interface JobAccess {
        BigInteger hk3gtl$activeBytes();
    }

    private Hk3ExactCpuCapacity() {}

    public static BigInteger exactBytes(ICraftingCPU cpu) {
        return cpu instanceof Access exact ? exact.hk3gtl$storageBytes()
                : BigInteger.valueOf(Math.max(0, cpu.getAvailableStorage()));
    }

    public static BigInteger activeBytes(ICraftingCPU cpu) {
        return cpu instanceof Access exact ? exact.hk3gtl$activeBytes() : BigInteger.ZERO;
    }

    public static BigInteger requiredBytes(ICraftingPlan plan) {
        BigInteger bytes = plan instanceof Hk3ExactBytePlan exact ? exact.exactBytes()
                : BigInteger.valueOf(plan.bytes());
        if (bytes.signum() < 0) throw new IllegalArgumentException("计划字节数不能为负数");
        return bytes;
    }

    public static boolean accepts(ICraftingCPU cpu, ICraftingPlan plan) {
        return exactBytes(cpu).compareTo(requiredBytes(plan)) >= 0;
    }

    public static long project(BigInteger bytes) {
        if (bytes.signum() < 0) throw new IllegalArgumentException("容量不能为负数");
        return bytes.min(LONG_MAX).longValueExact();
    }

    public static <T> BigInteger sumStorage(Iterable<T> blocks, ToLongFunction<T> contribution) {
        BigInteger bytes = BigInteger.ZERO;
        for (T block : blocks) {
            long part = contribution.applyAsLong(block);
            if (part > 0) bytes = bytes.add(BigInteger.valueOf(part));
        }
        return bytes;
    }

    /** 原生比较式仍是 long；只对精确计划用精确判定后的哨值，不能将投影误作容量。 */
    public static long admissionStorage(ICraftingCPU cpu, ICraftingPlan plan, long legacyStorage) {
        return plan instanceof Hk3ExactBytePlan
                ? accepts(cpu, plan) ? Long.MAX_VALUE : Long.MIN_VALUE : legacyStorage;
    }

    public static void writeJobBytes(CompoundTag tag, BigInteger bytes) {
        tag.remove(JOB_BYTES);
        if (bytes != null && bytes.signum() >= 0) tag.putByteArray(JOB_BYTES, bytes.toByteArray());
    }

    /** 缺失或损坏时保留原生任务，返回未知值；不能凭元数据补发任务或增加物理容量。 */
    public static BigInteger readJobBytes(CompoundTag tag) {
        if (!tag.contains(JOB_BYTES, Tag.TAG_BYTE_ARRAY)) return null;
        byte[] encoded = tag.getByteArray(JOB_BYTES);
        if (encoded.length == 0 || encoded.length > MAX_SAVED_BYTES) return null;
        BigInteger bytes = new BigInteger(encoded);
        return bytes.signum() < 0 ? null : bytes;
    }
}
