package com.sirin.hk3gtl.common.recipe.power;

import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import com.gregtechceu.gtceu.api.capability.recipe.EURecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableEnergyContainer;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;

/**
 * 【文件职责】从GT实际配方代理取出可验证的现有能源缓冲仓，不按聚合电压猜测单仓供能。
 * 【变更记录 #1】2026-10-17 16:43:35（第1次备注 · 修订165）
 * 删除：无；新增：身份去重、GT标准changeEnergy契约核验及BigInteger功率适配。
 * 修改：无线仓沿自身缓冲参与，不直接改第三方团队账户；用途：只给显式HK配方开启可回滚付款。
 * 边界：自行覆写取电/余额语义的仓室不参与，避免NoConsume网络仓被错误当作普通缓冲退款。
 */
/**
 * 【变更记录 #2】2026-10-17 16:55:08（第2次备注 · 修订165）
 * 删除：只相信changeEnergy回执的分支。
 * 新增：操作前后真实余额差校验，异常也携带实际改量；修改：不覆盖整仓快照。
 * 用途：监听器在余额写入后抛错时仍能退回已扣能源，非标准契约保持不参与。
 */
public final class Hk3PowerPorts {
    private Hk3PowerPorts() {}
    public static List<Hk3PortPayment.Port> of(RecipeLogic logic) {
        var result = new ArrayList<Hk3PortPayment.Port>();
        var seen = Collections.newSetFromMap(new IdentityHashMap<IEnergyContainer, Boolean>());
        for (IO io : List.of(IO.IN, IO.BOTH)) {
            var handlers = logic.machine.getCapabilitiesProxy().get(io, EURecipeCapability.CAP);
            if (handlers == null) continue;
            for (var handler : handlers) if (handler instanceof IEnergyContainer energy && seen.add(energy) && standard(energy))
                result.add(new Buffer(energy));
        }
        return result;
    }
    private static boolean standard(IEnergyContainer energy) {
        try {
            return energy.getInputVoltage() > 0 && energy.getInputAmperage() > 0
                    && energy.getClass().getMethod("changeEnergy", long.class).getDeclaringClass() == NotifiableEnergyContainer.class
                    && energy.getClass().getMethod("getEnergyStored").getDeclaringClass() == NotifiableEnergyContainer.class;
        } catch (ReflectiveOperationException unsupported) { return false; }
    }
    private record Buffer(IEnergyContainer energy) implements Hk3PortPayment.Port {
        @Override public BigInteger available() { return BigInteger.valueOf(energy.getEnergyStored()).max(BigInteger.ZERO); }
        @Override public BigInteger power() {
            return BigInteger.valueOf(energy.getInputVoltage()).multiply(BigInteger.valueOf(energy.getInputAmperage()));
        }
        @Override public BigInteger change(BigInteger delta) {
            long before = energy.getEnergyStored();
            try {
                long reported = energy.changeEnergy(delta.longValueExact());
                BigInteger actual = BigInteger.valueOf(energy.getEnergyStored()).subtract(BigInteger.valueOf(before));
                if (!actual.equals(BigInteger.valueOf(reported)))
                    throw new Hk3PortPayment.ChangeFailure(actual, new IllegalStateException("能源仓回执与实际余额不一致"));
                return actual;
            } catch (Hk3PortPayment.ChangeFailure known) { throw known; }
            catch (RuntimeException failure) {
                BigInteger actual = BigInteger.valueOf(energy.getEnergyStored()).subtract(BigInteger.valueOf(before));
                throw new Hk3PortPayment.ChangeFailure(actual, failure);
            }
        }
    }
}
