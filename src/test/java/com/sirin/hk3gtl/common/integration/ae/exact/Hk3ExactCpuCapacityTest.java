package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.networking.crafting.ICraftingCPU;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.stacks.KeyCounter;
import appeng.crafting.CraftingPlan;
import net.minecraft.nbt.CompoundTag;

import java.lang.reflect.Proxy;
import java.math.BigInteger;
import java.util.List;
import java.util.Map;

/** 验证单 CPU 超 long 字节准入，不以父订单分批或界面饱和代替。 */
public final class Hk3ExactCpuCapacityTest {
    private static final BigInteger MAX = BigInteger.valueOf(Long.MAX_VALUE);
    private static int checked;

    public static void main(String[] args) {
        BigInteger physical = Hk3ExactCpuCapacity.sumStorage(List.of(Long.MAX_VALUE, Long.MAX_VALUE, 7L), Long::longValue);
        check(physical.equals(MAX.multiply(BigInteger.TWO).add(BigInteger.valueOf(7))), "真实单块容量精确相加");
        check(Hk3ExactCpuCapacity.sumStorage(List.of(0L, -4L, 8L), Long::longValue).equals(BigInteger.valueOf(8)),
                "无存储贡献不产生容量");
        check(Hk3ExactCpuCapacity.project(physical) == Long.MAX_VALUE, "公共 long 接口仅饱和投影");
        check(Hk3ExactCpuCapacity.project(BigInteger.valueOf(123)) == 123, "小容量原值保留");
        rejects(() -> Hk3ExactCpuCapacity.project(BigInteger.valueOf(-1)), "负容量拒绝");

        ICraftingPlan delegate = plan(9);
        Hk3ExactCapacityPlan large = new Hk3ExactCapacityPlan(delegate, MAX.add(BigInteger.ONE));
        check(large.bytes() == Long.MAX_VALUE && large.exactBytes().equals(MAX.add(BigInteger.ONE)), "需求精度不因兼容投影丢失");
        check(large.usedItems() == delegate.usedItems() && large.patternTimes() == delegate.patternTimes(), "真实物料和任务完整委托");
        rejects(() -> new Hk3ExactCapacityPlan(delegate, BigInteger.valueOf(-1)), "负计划字节拒绝");

        ICraftingCPU exactMax = cpu(MAX, BigInteger.ZERO);
        ICraftingCPU bigger = cpu(physical, MAX.add(BigInteger.valueOf(2)));
        check(!Hk3ExactCpuCapacity.accepts(exactMax, large), "MAX 容量不能接 MAX+1 任务");
        check(Hk3ExactCpuCapacity.accepts(bigger, large), "同一 CPU 真实容量超 long 后准入单个超 long 字节任务");
        check(!Hk3ExactCpuCapacity.accepts(bigger, new Hk3ExactCapacityPlan(delegate, physical.add(BigInteger.ONE))),
                "超 long 容量仍有精确上限");
        check(Hk3ExactCpuCapacity.activeBytes(bigger).equals(MAX.add(BigInteger.valueOf(2))), "状态保留活动任务精确字节");
        check(Hk3ExactCpuCapacity.admissionStorage(exactMax, large, Long.MAX_VALUE) < large.bytes(), "自动选择精确拒绝");
        check(Hk3ExactCpuCapacity.admissionStorage(bigger, large, Long.MAX_VALUE) >= large.bytes(), "自动选择精确准入");
        check(Hk3ExactCpuCapacity.admissionStorage(bigger, delegate, 123) == 123, "原生计划比较值保留");
        ICraftingPlan composed = composed(delegate, physical);
        check(Hk3ExactCpuCapacity.requiredBytes(composed).equals(physical), "组合计划通过公共精确接口保持容量");
        check(Hk3ExactCpuCapacity.accepts(bigger, composed), "组合计划按精确字节准入");

        CompoundTag tag = new CompoundTag();
        Hk3ExactCpuCapacity.writeJobBytes(tag, physical);
        check(physical.equals(Hk3ExactCpuCapacity.readJobBytes(tag)), "活动任务超 long 需求二进制持久化往返");
        Hk3ExactCpuCapacity.writeJobBytes(tag, null);
        check(Hk3ExactCpuCapacity.readJobBytes(tag) == null, "结束任务清除旧计费");
        tag.putByteArray("hk3ExactJobBytes", BigInteger.valueOf(-3).toByteArray());
        check(Hk3ExactCpuCapacity.readJobBytes(tag) == null, "负值持久化不增加容量");
        tag.putByteArray("hk3ExactJobBytes", new byte[2049]);
        check(Hk3ExactCpuCapacity.readJobBytes(tag) == null, "异常长持久化拒绝");
        tag.putByteArray("hk3ExactJobBytes", new byte[0]);
        check(Hk3ExactCpuCapacity.readJobBytes(tag) == null, "空持久化拒绝");
        Hk3ExactCpuCapacity.writeJobBytes(tag, BigInteger.ZERO);
        check(BigInteger.ZERO.equals(Hk3ExactCpuCapacity.readJobBytes(tag)), "零字节合法往返");
        System.out.println("Hk3ExactCpuCapacityTest：" + checked + " 项通过");
    }

    private static ICraftingPlan plan(long bytes) {
        return new CraftingPlan(null, bytes, false, false,
                new KeyCounter(), new KeyCounter(), new KeyCounter(), Map.of());
    }

    private static ICraftingCPU cpu(BigInteger capacity, BigInteger active) {
        return (ICraftingCPU) Proxy.newProxyInstance(Hk3ExactCpuCapacityTest.class.getClassLoader(),
                new Class<?>[]{ICraftingCPU.class, Hk3ExactCpuCapacity.Access.class}, (proxy, method, args) -> {
                    return switch (method.getName()) {
                        case "hk3gtl$storageBytes" -> capacity;
                        case "hk3gtl$activeBytes" -> active;
                        case "getAvailableStorage" -> Hk3ExactCpuCapacity.project(capacity);
                        case "isBusy" -> false;
                        case "getCoProcessors" -> 0;
                        case "getName" -> null;
                        default -> throw new UnsupportedOperationException(method.getName());
                    };
                });
    }

    private static ICraftingPlan composed(ICraftingPlan delegate, BigInteger bytes) {
        return (ICraftingPlan) Proxy.newProxyInstance(Hk3ExactCpuCapacityTest.class.getClassLoader(),
                new Class<?>[]{ICraftingPlan.class, Hk3ExactBytePlan.class}, (proxy, method, args) -> {
                    return method.getName().equals("exactBytes") ? bytes : method.invoke(delegate, args);
                });
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
        checked++;
    }

    private static void rejects(Runnable action, String message) {
        try {
            action.run();
            throw new AssertionError(message);
        } catch (IllegalArgumentException expected) {
            checked++;
        }
    }
}
