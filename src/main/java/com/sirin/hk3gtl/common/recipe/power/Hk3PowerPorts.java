package com.sirin.hk3gtl.common.recipe.power;

import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import com.gregtechceu.gtceu.api.capability.recipe.EURecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableEnergyContainer;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.hepdd.gtmthings.api.misc.WirelessEnergyManager;
import com.sirin.hk3gtl.common.capability.Hk3GridEnergyRefund;
import com.sirin.hk3gtl.common.capability.Hk3RefundActions;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.capability.Hk3RefundTarget;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.trait.Hk3PlayerGridEnergyTrait;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.UUID;

 






 





public final class Hk3PowerPorts {
    private Hk3PowerPorts() {}
    public static Hk3PortPayment.Port of(NotifiableEnergyContainer energy) { return new Buffer(energy); }

    public static List<Hk3PortPayment.Port> of(RecipeLogic logic) {
        var result = new ArrayList<Hk3PortPayment.Port>();
        var seen = Collections.newSetFromMap(new IdentityHashMap<IEnergyContainer, Boolean>());
        for (IO io : List.of(IO.IN, IO.BOTH)) {
            var handlers = logic.machine.getCapabilitiesProxy().get(io, EURecipeCapability.CAP);
            if (handlers == null) continue;
            for (var handler : handlers) {
                if (!(handler instanceof IEnergyContainer energy) || !seen.add(energy)) continue;
                if (energy instanceof Hk3PlayerGridEnergyTrait grid
                        && grid.getMachine() instanceof Hk3WorkableMultiblockMachine machine && machine.getOwnerUUID() != null)
                    result.add(new PlayerGrid(grid, machine.getOwnerUUID()));
                else if (standard(energy)) result.add(new Buffer((NotifiableEnergyContainer) energy));
            }
        }
        return result;
    }

    // 自家玩家网沿既有额定接口计功率，退款固定付款时的原团队账户。
    private static final class PlayerGrid implements Hk3PortPayment.Port {
        private final Hk3PlayerGridEnergyTrait energy;
        private final UUID owner;
        private Hk3GridEnergyRefund source;
        private PlayerGrid(Hk3PlayerGridEnergyTrait energy, UUID owner) { this.energy = energy; this.owner = owner; }
        @Override public BigInteger available() { return WirelessEnergyManager.getUserEU(owner).max(BigInteger.ZERO); }
        @Override public BigInteger power() {
            return BigInteger.valueOf(energy.getInputVoltage()).multiply(BigInteger.valueOf(energy.getInputAmperage()));
        }
        @Override public BigInteger change(BigInteger delta) {
            source = Hk3GridEnergyRefund.capture(energy.getMachine().getLevel().getServer(), owner);
            return WirelessEnergyManager.addEUToGlobalEnergyMap(owner, delta, energy.getMachine()) ? delta : BigInteger.ZERO;
        }
        @Override public Hk3RefundJournal.Action refund(BigInteger applied) { return Hk3RefundActions.grid(source, applied); }
    }
    private static boolean standard(IEnergyContainer energy) {
        try {
            return energy.getInputVoltage() > 0 && energy.getInputAmperage() > 0
                    && energy.getClass().getMethod("changeEnergy", long.class).getDeclaringClass() == NotifiableEnergyContainer.class
                    && energy.getClass().getMethod("getEnergyStored").getDeclaringClass() == NotifiableEnergyContainer.class;
        } catch (ReflectiveOperationException unsupported) { return false; }
    }
    public static Hk3PortPayment.Port restore(MinecraftServer server, CompoundTag address) {
        var target = new Hk3RefundTarget(server, address.copy());
        // 延迟取仓，区块尚未加载也保留整个原始退款栈。
        return new Hk3PortPayment.Port() {
            private Hk3PortPayment.Port resolve() {
                if (!(target.trait() instanceof NotifiableEnergyContainer energy) || !standard(energy))
                    throw new IllegalStateException("原能源仓不再支持安全退款");
                var buffer = new Buffer(energy);
                buffer.target = target;
                return buffer;
            }
            @Override public BigInteger available() { return resolve().available(); }
            @Override public BigInteger power() { return resolve().power(); }
            @Override public BigInteger change(BigInteger delta) { return resolve().change(delta); }
            @Override public CompoundTag refundTarget() { return address.copy(); }
        };
    }

    private static final class Buffer implements Hk3PortPayment.Port {
        private final NotifiableEnergyContainer energy;
        private Hk3RefundTarget target;
        private Buffer(NotifiableEnergyContainer energy) { this.energy = energy; }
        @Override public CompoundTag refundTarget() { return target == null ? null : target.address().copy(); }
        @Override public BigInteger available() { return BigInteger.valueOf(energy.getEnergyStored()).max(BigInteger.ZERO); }
        @Override public BigInteger power() {
            return BigInteger.valueOf(energy.getInputVoltage()).multiply(BigInteger.valueOf(energy.getInputAmperage()));
        }
        @Override public BigInteger change(BigInteger delta) {
            if (target == null) target = Hk3RefundTarget.capture(energy);
            if (target.trait() != energy) throw new IllegalStateException("能源仓已卸载或替换，保留退款");
            return changeObserved(energy, delta, () -> energy.getMachine().getHolder().getSelf().setChanged());
        }
    }

    static BigInteger changeObserved(IEnergyContainer energy, BigInteger delta, Runnable markDirty) {
        long before = energy.getEnergyStored();
        try {
            long reported;
            try { reported = energy.changeEnergy(delta.longValueExact()); }
            finally { markDirty.run(); }
            BigInteger actual = BigInteger.valueOf(energy.getEnergyStored()).subtract(BigInteger.valueOf(before));
            if (!actual.equals(BigInteger.valueOf(reported)))
                throw new Hk3PortPayment.ChangeFailure(actual, new IllegalStateException("能源仓回执与实际余额不一致"));
            return actual;
        } catch (RuntimeException failure) {
            BigInteger actual = BigInteger.valueOf(energy.getEnergyStored()).subtract(BigInteger.valueOf(before));
            throw new Hk3PortPayment.ChangeFailure(actual, failure);
        }
    }
}
