package com.sirin.hk3gtl.common.machine.research;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.common.machine.multiblock.part.ItemBusPartMachine;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.gaze.Hk3ResearchSuppression;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes;
import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.network.chat.Component;
import net.minecraft.nbt.CompoundTag;

import java.math.BigInteger;
import java.util.List;
import java.util.UUID;

/** 已批准R03持续场与暂定制造工艺分离；只有本刻足额扣电才能提供抑制。 */
public final class Hk3RealityStabilityAnchorMachine extends Hk3LateIndustrialMachine
        implements Hk3ResearchSuppression.Source {
    private long checkedTick = Long.MIN_VALUE;
    private long paidTick = Long.MIN_VALUE;
    private boolean paidEnhanced;
    private UUID paidTeam;
    private Hk3EnergyTick fieldRefund;

    public Hk3RealityStabilityAnchorMachine(IMachineBlockEntity holder) {
        super(holder, "I36");
    }

    @Override protected boolean enableMultiRecipe() { return false; }

    @Override protected boolean continuousMode() { return getRecipeType() == Hk3ResearchProcessTypes.get("I36"); }

    @Override protected boolean runContinuousProcess() {
        if (!continuousMode()) return false;
        updateField(); return true;
    }

    private boolean hasJudahModule() {
        var module = Hk3IndustrialContent.items().get("imitation_oath_of_judah").get();
        for (var part : getParts()) {
            if (!(part instanceof ItemBusPartMachine bus) || bus.getInventory().getHandlerIO() != IO.IN) continue;
            var inventory = bus.getInventory();
            for (int slot = 0; slot < inventory.getSlots(); slot++)
                if (inventory.getStackInSlot(slot).is(module)) return true;
        }
        return false;
    }

    private boolean enhancementAvailable() {
        return Hk3ResearchData.get(getLevel().getServer()).completed(getResearchTeamUUID(), "RN-JOK")
                && hasJudahModule();
    }

    private void updateField() {
        long now = getLevel().getGameTime();
        if (checkedTick == now) return;
        checkedTick = now;
        if (!isFormed() || getOwnerUUID() == null) return;
        if (!getRecipeLogic().isWorkingEnabled()) {
            getRecipeLogic().setStatus(RecipeLogic.Status.IDLE);
            return;
        }
        if (fieldRefund == null) fieldRefund = Hk3RefundJournal.resume(this);
        if (fieldRefund != null) {
            if (!fieldRefund.finish(false)) return;
            fieldRefund = null;
        }
        var team = getResearchTeamUUID();
        if (team == null || !Hk3ResearchData.get(getLevel().getServer()).completed(team, "RN-RAT")) {
            getRecipeLogic().setWaiting(Component.translatable("hk3gtl.machine.stability_anchor.research_required"));
            return;
        }
        boolean enhanced = enhancementAvailable();
        long cost = Hk3Values.VA_LONG[enhanced ? Hk3Tiers.QSV : GTValues.MAX];
        var payment = Hk3RefundJournal.open(this);
        boolean committed = false;
        try {
            if (!Hk3PortPayment.pay(Hk3PowerPorts.of(getRecipeLogic()), BigInteger.valueOf(cost), payment)) {
                getRecipeLogic().setWaiting(Component.translatable("hk3gtl.machine.stability_anchor.energy_required", cost));
                return;
            }
            payment.onCommit(() -> {
                paidTick = now;
                paidEnhanced = enhanced;
                paidTeam = team;
                recordPaidField(team, enhanced, cost, now);
                getRecipeLogic().setStatus(RecipeLogic.Status.WORKING);
            });
            committed = true;
        } finally {
            if (!payment.finish(committed)) fieldRefund = payment;
        }
    }

    private void recordPaidField(UUID team, boolean enhanced, long cost, long tick) {
        var data = Hk3ResearchData.get(getLevel().getServer());
        String fact = enhanced ? "anchor_enhanced" : "anchor_basic";
        if (data.hasProcessFact(team, fact)) return;
        var receipt = new CompoundTag();
        receipt.putUUID("Batch", UUID.randomUUID());
        receipt.putString("Facility", getLevel().dimension().location() + "@" + getPos());
        receipt.putString("Recipe", "hk3gtl:continuous_stability_field/" + fact);
        receipt.putLong("Tick", tick);
        var inputs = new CompoundTag();
        inputs.putLong("EU", cost);
        var outputs = new CompoundTag();
        outputs.putInt("SuppressionRadius", enhanced ? 128 : 64);
        outputs.putInt("SuppressionPercent", enhanced ? 75 : 50);
        receipt.put("Inputs", inputs);
        receipt.put("Outputs", outputs);
        data.recordProcessFact(team, fact, receipt);
    }

    @Override public long lastPaidTick() {
        // 查询先于锚自身tick时也结算同一刻；checkedTick禁止重复扣电。
        if (!continuousMode()) return Long.MIN_VALUE;
        updateField();
        return paidTeam != null && paidTeam.equals(getResearchTeamUUID()) ? paidTick : Long.MIN_VALUE;
    }

    @Override public boolean enhancedSuppression() { return paidEnhanced && enhancementAvailable(); }

    @Override public void addDisplayText(List<Component> lines) {
        super.addDisplayText(lines);
        lines.add(Component.translatable("hk3gtl.machine.stability_anchor.contract"));
        if (!isRemote() && paidTick == getLevel().getGameTime())
            lines.add(Component.translatable("hk3gtl.machine.stability_anchor.active",
                    paidEnhanced ? 128 : 64, paidEnhanced ? 75 : 50));
    }
}
