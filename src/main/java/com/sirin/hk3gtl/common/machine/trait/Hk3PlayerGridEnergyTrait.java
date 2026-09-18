package com.sirin.hk3gtl.common.machine.trait;



import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import com.gregtechceu.gtceu.api.capability.recipe.EURecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.RecipeCapability;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableRecipeHandlerTrait;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.hepdd.gtmthings.api.misc.WirelessEnergyManager;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import net.minecraft.core.Direction;
import org.jetbrains.annotations.Nullable;

import java.math.BigInteger;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * 玩家电网 EU 特征：把控制器本体变成一个"电压极高、容量无限"的 EU 输入代理，
 * 背后的存量是 GTMThings 无线电网中绑定玩家（或其 FTB 队伍）的余额。
 */
public class Hk3PlayerGridEnergyTrait extends NotifiableRecipeHandlerTrait<Long> implements IEnergyContainer {

    private static final BigInteger LONG_MAX = BigInteger.valueOf(Long.MAX_VALUE);

    /** 名义输入电压（终焉 III 档）。仅影响 tier 显示与超频上限，实际扣电全按电网余额。 */
    private static final long NOMINAL_VOLTAGE = Hk3Values.VA_LONG[29];

    /** 电网绑定玩家 UUID 提供者（由控制器持有并持久化，本特征只读） */
    private final Supplier<@Nullable UUID> ownerSupplier;

    public Hk3PlayerGridEnergyTrait(MetaMachine machine, Supplier<@Nullable UUID> ownerSupplier) {
        super(machine);
        this.ownerSupplier = ownerSupplier;
    }

    @Nullable
    private UUID owner() {
        return ownerSupplier.get();
    }

    @Override
    public IO getHandlerIO() {
        return IO.IN;
    }

    @Override
    public RecipeCapability<Long> getCapability() {
        return EURecipeCapability.CAP;
    }

    /**
     * 配方 EU 结算入口。
     * <p>边界：owner 未绑定时原样返回 left（一分电都出不了，配方进入 WAITING）；
     * simulate 路径只做余额比较，绝不写电网。</p>
     */
    @Override
    public List<Long> handleRecipeInner(IO io, GTRecipe recipe, List<Long> left, @Nullable String slotName, boolean simulate) {
        UUID owner = owner();
        if (owner == null) return left;

        long sum = saturatedSum(left);
        if (io == IO.IN) {
            long available = getEnergyStored();
            if (!simulate) {
                long drawn = Math.min(available, sum);
                if (drawn > 0) {
                    WirelessEnergyManager.addEUToGlobalEnergyMap(owner, -drawn, getMachine());
                }
            }
            long remaining = sum - available;
            return remaining <= 0 ? null : Collections.singletonList(remaining);
        } else if (io == IO.OUT) {
            // 电网视为无限容量，发电类配方全额注入
            if (!simulate && sum > 0) {
                WirelessEnergyManager.addEUToGlobalEnergyMap(owner, sum, getMachine());
            }
            return null;
        }
        return left;
    }

    /** 饱和求和，防止超大 EU/t × 并行下 long 溢出翻负 */
    private static long saturatedSum(List<Long> values) {
        long sum = 0;
        for (Long v : values) {
            if (v == null) continue;
            try {
                sum = Math.addExact(sum, v);
            } catch (ArithmeticException e) {
                return Long.MAX_VALUE;
            }
        }
        return sum;
    }

    // ── IEnergyContainer：给 EnergyContainerList / 反射调用方使用 ─────────

    @Override
    public long acceptEnergyFromNetwork(Direction side, long voltage, long amperage) {
        return 0; // 不接受线缆输电，电只来自电网
    }

    @Override
    public boolean inputsEnergy(Direction side) {
        return false;
    }

    /**
     * 直改存量：正数注入电网、负数从电网扣除（按余额裁剪）。
     * 研究矩阵 removeEnergy / 双转换矩阵 changeEnergy 反射路径都会走到这里。
     */
    @Override
    public long changeEnergy(long differenceAmount) {
        UUID owner = owner();
        if (owner == null || differenceAmount == 0) return 0;
        if (differenceAmount > 0) {
            return WirelessEnergyManager.addEUToGlobalEnergyMap(owner, differenceAmount, getMachine())
                    ? differenceAmount : 0;
        }
        long drawn = Math.min(getEnergyStored(), -differenceAmount);
        if (drawn <= 0) return 0;
        return WirelessEnergyManager.addEUToGlobalEnergyMap(owner, -drawn, getMachine()) ? -drawn : 0;
    }

    @Override
    public long getEnergyStored() {
        UUID owner = owner();
        if (owner == null) return 0;
        BigInteger eu = WirelessEnergyManager.getUserEU(owner);
        return eu.compareTo(LONG_MAX) >= 0 ? Long.MAX_VALUE : eu.longValue();
    }

    @Override
    public long getEnergyCapacity() {
        return Long.MAX_VALUE;
    }

    @Override
    public long getInputVoltage() {
        return NOMINAL_VOLTAGE;
    }

    /** 刻意返回 2：让 getOverclockVoltage 走 amperage != 1 分支，避开 GTValues.VEX 高 tier 越界 */
    @Override
    public long getInputAmperage() {
        return 2;
    }

    @Override
    public List<Object> getContents() {
        return List.of(getEnergyStored());
    }

    @Override
    public double getTotalContentAmount() {
        return getEnergyStored();
    }
}
