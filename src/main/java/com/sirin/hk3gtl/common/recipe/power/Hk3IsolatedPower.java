package com.sirin.hk3gtl.common.recipe.power;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import org.gtlcore.gtlcore.api.recipe.IAdvancedContentModifier;
import org.gtlcore.gtlcore.api.recipe.RecipeExtensionCopier;
import org.gtlcore.gtlcore.api.recipe.IGTRecipe;

import java.math.BigInteger;
import java.util.List;

public final class Hk3IsolatedPower {
    private Hk3IsolatedPower() {}

    public static long parallel(RecipeLogic logic, GTRecipe recipe, long limit) {
        BigInteger capacity = Hk3PortPayment.availablePower(Hk3PowerPorts.of(logic)).min(BigInteger.valueOf(Long.MAX_VALUE));
        BigInteger hw = Hk3DualEnergyCosts.getMergedCost(recipe);
        BigInteger batches = capacity.divide(Hk3RecipePower.cost(recipe));
        if (hw != null && hw.signum() > 0)
            batches = batches.min(HonkaiWirelessNetwork.getStoredAmount(Hk3RecipePower.externalPayer(logic.getMachine())).divide(hw));
        return batches.min(BigInteger.valueOf(limit)).longValueExact();
    }

    public static GTRecipe scale(GTRecipe recipe, long parallel) {
        GTRecipe scaled = parallel == 1 ? recipe.copy() : recipe.copy(IAdvancedContentModifier.preciseMultiplier(parallel), false);
        RecipeExtensionCopier.copy(recipe, scaled);
        Hk3RecipePower.scale(recipe, scaled, parallel);
        BigInteger hw = Hk3DualEnergyCosts.getMergedCost(recipe);
        if (hw != null) Hk3DualEnergyCosts.setMergedCost(scaled, hw.multiply(BigInteger.valueOf(parallel)));
        IGTRecipe.of(scaled).setRealParallels(parallel);
        return scaled;
    }

    public static List<Hk3PortPayment.Port> tickBudget(RecipeLogic logic) {
        return Hk3PowerPorts.of(logic).stream().<Hk3PortPayment.Port>map(port -> new Hk3PortPayment.Port() {
            private BigInteger left = port.power();
            @Override public BigInteger power() { return left; }
            @Override public BigInteger available() { return port.available(); }
            @Override public BigInteger change(BigInteger delta) {
                BigInteger changed = port.change(delta);
                left = left.add(changed);
                return changed;
            }
            @Override public Hk3RefundJournal.Action refund(BigInteger applied) { return port.refund(applied); }
        }).toList();
    }

    public static boolean pay(RecipeLogic logic, List<Hk3PortPayment.Port> ports, BigInteger eu, BigInteger hw) {
        var machine = logic.getMachine();
        if (!machine.getLevel().getServer().isSameThread()) return false;
        var pending = Hk3RefundJournal.resume(machine);
        if (pending != null && !pending.finish(false)) return false;
        var tick = Hk3RefundJournal.open(machine);
        boolean paid = false;
        try {
            paid = Hk3PortPayment.pay(ports, eu, tick)
                    && Hk3RecipePower.reserveHonkai(logic, hw, tick);
            return paid;
        } finally {
            tick.finish(paid);
        }
    }
}
