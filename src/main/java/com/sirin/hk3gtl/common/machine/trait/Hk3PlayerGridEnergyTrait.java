package com.sirin.hk3gtl.common.machine.trait;

/**
 * 【变更记录 #5】2026-10-26 19:57:03（修订177）
 * 删除：发电控制器始终被挂入EU输入代理的限制。
 * 新增／修改：发电定义以OUT能力挂载玩家电网，输出电压取控制器批准档位，保留精确金额和工作票据退款。
 * 用途：I19至I23具备真实发电结算通道；普通耗电控制器的输入行为保持。
 */
/**
 * 【文件职责】
 * - 控制器自带的"玩家电网 EU"配方处理特征：多方块不再需要能源仓，
 *   所有 EU 消耗直接从绑定玩家（UUID）的 GTMThings 无线电网中扣除。
 * - 关键调用链：
 *   1) WorkableMultiblockMachine.onStructureFormed -> 自身 trait 扫描 -> 本类注入 capabilitiesProxy(IN, EU)；
 *   2) GTRecipe.matchTickRecipe / handleTickRecipeIO -> handleRecipeInner -> WirelessEnergyManager 扣电/充电；
 *   3) WorkableElectricMultiblockMachine.getEnergyContainer -> 聚合本类（实现 IEnergyContainer），
 *      研究矩阵 consumeEnergy / 双转换矩阵 fillGtEnergy 的反射调用零改动兼容。
 *
 * 【变更记录 #1】2026-07-03 01:10:00（第 1 次备注 · 内测三第 26 次更新）
 * - 删除：无（新建文件）。
 * - 新增：
 *   1) 新建 Hk3PlayerGridEnergyTrait，继承 NotifiableRecipeHandlerTrait<Long> 并实现 IEnergyContainer；
 *      handlerIO = IN，capability = EURecipeCapability，因此结构成型时被 GT 自动注入 EU 输入代理。
 *   2) handleRecipeInner：IN 方向按可用电网 EU 裁剪（simulate 不扣），实际执行时调
 *      WirelessEnergyManager.addEUToGlobalEnergyMap(owner, -drawn, machine) 扣电；
 *      OUT 方向视电网为无限容量，全额注入（发电类配方兼容）。
 *   3) IEnergyContainer 实现：getEnergyStored 返回电网余额（BigInteger 钳制到 Long.MAX_VALUE），
 *      capacity = Long.MAX_VALUE；inputVoltage 取 Hk3Values.VA_LONG[29]（终焉 III 档，避免依赖
 *      GTValuesMixin 扩展成功）、amperage = 2 —— EnergyContainerList 聚合后 getOverclockVoltage
 *      走 amperage != 1 分支直接返回电压本身，绕开只有 15 元素的 GTValues.VEX 数组越界。
 * - 修改：无。
 * - 用途：
 *   1) 业务目标：结构上取消能源仓后机器仍能跑配方，EU 从玩家电网直接结算。
 *   2) 关键风险点：owner 为 null（未绑定）时 stored=0，配方进入 WAITING 而非崩溃；
 *      仅服务端 tick 调用，无并发问题；simulate 路径绝不改动电网余额。
 */

import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import com.gregtechceu.gtceu.api.capability.recipe.EURecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.RecipeCapability;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableRecipeHandlerTrait;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.hepdd.gtmthings.api.misc.WirelessEnergyManager;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.capability.Hk3GridEnergyPayment;
import com.sirin.hk3gtl.common.capability.Hk3GridEnergyRefund;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.machine.Hk3RecipeLogic;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import net.minecraft.core.Direction;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.math.BigInteger;

/**
 * 玩家电网 EU 特征：把控制器本体变成一个"电压极高、容量无限"的 EU 输入代理，
 * 背后的存量是 GTMThings 无线电网中绑定玩家（或其 FTB 队伍）的余额。
 */
/** 【变更记录 #2】2026-10-01 06:11:31（修订128）：删除：无；新增/修改：只在真实电网扣EU返回成功后写双能源旁注，不以模拟余额代替扣款；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/**
 * 【变更记录 #3】2026-10-01 17:33:35（修订138）
 * 删除：配方耗电饱和求和、仅按预查余额报告支付成功以及long直接取反。
 * 新增：精确支付适配与发电写入失败的剩余返回；同一次操作固定绑定玩家。
 * 修改：调用电网BigInteger入口，按后端成功结果返回实际数量；显示仍适配long上限。
 * 用途：覆盖配方消费、发电回存、研究所直接扣电，不改变能源价格或第三方团队账户规则。
 */
/**
 * 【变更记录 #4】2026-10-01 17:41:38（修订139）
 * 删除：普通工作tick支付后立即发彩蛋回执的时机。
 * 新增：成功EU改量的反向操作，绑定付款时实际团队与存档；覆盖tick内直接取电。
 * 修改：推进后再记录EU运行事实；失败退回实际改量，不影响独立研究队列原取电入口。
 * 用途：与HW预留和实际推进对齐；第三方监控可能仍展示尝试的毛流量，余额按净结算。
 */
public class Hk3PlayerGridEnergyTrait extends NotifiableRecipeHandlerTrait<Long> implements IEnergyContainer {

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
        return getMachine().getDefinition() instanceof com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition definition
                && definition.isGenerator() ? IO.OUT : IO.IN;
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

        if (io == IO.IN) {
            var payment = Hk3GridEnergyPayment.input(left, () -> WirelessEnergyManager.getUserEU(owner),
                    delta -> changeForTick(owner, delta), simulate);
            return payment.remaining();
        } else if (io == IO.OUT) {
            return Hk3GridEnergyPayment.output(left,
                    delta -> changeForTick(owner, delta), simulate).remaining();
        }
        return left;
    }

    private Hk3EnergyTick energyTick() {
        return getMachine() instanceof Hk3WorkableMultiblockMachine machine
                && machine.getRecipeLogic() instanceof Hk3RecipeLogic logic ? logic.getEnergyTick() : null;
    }

    private boolean changeForTick(UUID owner, BigInteger delta) {
        var tick = energyTick();
        if (tick != null) tick.requireOpen();
        var refund = tick == null ? null : Hk3GridEnergyRefund.capture(getMachine().getLevel().getServer(), owner);
        boolean paid = WirelessEnergyManager.addEUToGlobalEnergyMap(owner, delta, getMachine());
        if (paid && refund != null && delta.signum() != 0) {
            tick.undoWith(() -> refund.undo(delta));
            if (delta.signum() < 0) tick.onCommit(() -> com.sirin.hk3gtl.common.easter.Hk3EggEnergy.paid(getMachine(), owner, false));
        }
        return paid;
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
        return Hk3GridEnergyPayment.change(differenceAmount, () -> WirelessEnergyManager.getUserEU(owner),
                delta -> changeForTick(owner, delta));
    }

    @Override
    public long getEnergyStored() {
        UUID owner = owner();
        if (owner == null) return 0;
        return Hk3GridEnergyPayment.visibleBalance(WirelessEnergyManager.getUserEU(owner));
    }

    @Override
    public long getEnergyCapacity() {
        return Long.MAX_VALUE;
    }

    @Override
    public long getInputVoltage() {
        return getHandlerIO() == IO.OUT ? 0 : NOMINAL_VOLTAGE;
    }

    /** 刻意返回 2：让 getOverclockVoltage 走 amperage != 1 分支，避开 GTValues.VEX 高 tier 越界 */
    @Override
    public long getInputAmperage() {
        return getHandlerIO() == IO.OUT ? 0 : 2;
    }

    @Override
    public long getOutputVoltage() {
        return getHandlerIO() == IO.OUT ? Hk3Values.getV(getMachine().getDefinition().getTier()) : 0;
    }

    @Override
    public long getOutputAmperage() {
        return getHandlerIO() == IO.OUT ? 2 : 0;
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
