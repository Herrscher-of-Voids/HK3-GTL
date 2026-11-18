package com.sirin.hk3gtl.common.research;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import net.minecraft.nbt.CompoundTag;

import java.math.BigInteger;
import java.util.UUID;

public final class Hk3ResearchHwLoad {
    private final Hk3WorkableMultiblockMachine machine;
    private UUID hwPayer;
    private UUID euPayer;
    private BigInteger hw = BigInteger.ZERO;
    private BigInteger eu = BigInteger.ZERO;

    public Hk3ResearchHwLoad(Hk3WorkableMultiblockMachine machine) { this.machine = machine; }

    public void honkai(UUID payer, BigInteger amount) { hwPayer = payer; hw = hw.add(amount); }
    public void grid(UUID payer, BigInteger amount) { euPayer = payer; eu = eu.add(amount); }

    public void worked(GTRecipe recipe) {
        if (hw.signum() <= 0 || eu.signum() <= 0 || !hwPayer.equals(euPayer)
                || !hwPayer.equals(machine.getOwnerUUID())) return;
        var level = machine.getLevel();
        var scope = machine.getResearchTeamUUID();
        var data = Hk3ResearchData.get(level.getServer());
        if (!data.isMember(hwPayer, scope) || data.hasProcessFact(scope, "hw_load")) return;
        var inputs = new CompoundTag();
        inputs.putString("HW", hw.toString());
        inputs.putString("EU", eu.toString());
        var outputs = new CompoundTag();
        outputs.putInt("ProgressTicks", 1);
        var receipt = new CompoundTag();
        receipt.putString("Recipe", recipe.id.toString());
        receipt.putString("Controller", machine.getDefinition().getId().toString());
        receipt.putUUID("Payer", hwPayer);
        receipt.putUUID("Team", scope);
        receipt.put("Inputs", inputs);
        receipt.put("Outputs", outputs);
        data.recordProcessFact(scope, "hw_load", Hk3ProcessReceipts.settle(receipt,
                level.dimension().location() + "@" + machine.getPos().asLong(), level.getGameTime()));
    }
}
