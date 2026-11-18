package com.sirin.hk3gtl.common.machine.wonder;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchProcessMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ProcessReceipts;

/** 完整实体验证、研究及二审均通过后才执行真实配方；调试不写生产回执。 */
public abstract class Hk3WonderProductionMachine extends Hk3ResearchProcessMachine {
    private static final java.util.Set<Hk3WonderProductionMachine> LOADED = java.util.concurrent.ConcurrentHashMap.newKeySet();
    protected Hk3WonderProductionMachine(IMachineBlockEntity holder, String role) { super(holder, role); }
    public abstract boolean verified();
    @Override public void onLoad() { super.onLoad(); if (!isRemote()) LOADED.add(this); }
    @Override public void onUnload() { LOADED.remove(this); super.onUnload(); }
    public static boolean formed(java.util.UUID team, String role) {
        return LOADED.stream().anyMatch(machine -> role.equals(machine.researchRole())
                && team.equals(machine.getResearchTeamUUID()) && machine.verified() && machine.isFormed());
    }
    public static boolean formed(net.minecraft.server.MinecraftServer server, java.util.UUID team, String role, String facility) {
        return LOADED.stream().anyMatch(machine -> machine.getLevel().getServer() == server
                && !machine.isInValid() && role.equals(machine.researchRole()) && team.equals(machine.getResearchTeamUUID())
                && facility.equals(machine.getLevel().dimension().location() + "@" + machine.getPos())
                && machine.verified() && machine.isFormed());
    }
    @Override public int getTier() { return getDefinition().getTier(); }
    @Override public long getMaxVoltage() {
        return Hk3Values.getV(com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessEnergy.executionVoltageTier(
                getDefinition().getRecipeTypes(), getTier()));
    }
    @Override public long getOverclockVoltage() { return getMaxVoltage(); }
    protected boolean productionReady(GTRecipe recipe) { return verified() && isFormed(); }
    @Override public boolean beforeWorking(GTRecipe recipe) { return productionReady(recipe) && super.beforeWorking(recipe); }
    @Override public GTRecipe fullModifyRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        return productionReady(recipe) ? super.fullModifyRecipe(recipe, params, result) : null;
    }
    @Override protected void onProcessOutput(GTRecipe recipe) {
        super.onProcessOutput(recipe);
        if (researchRole().equals("H01")) com.sirin.hk3gtl.common.easter.Hk3EggProduction.receipt(this,18);
        var data = Hk3ResearchData.get(getLevel().getServer());
        if (java.util.stream.IntStream.rangeClosed(1, 14).allMatch(i ->
                data.hasProcessFact(getResearchTeamUUID(), String.format(java.util.Locale.ROOT, "wonder_W%02d", i)))) {
            var receipt = Hk3ProcessReceipts.settle(Hk3ProcessReceipts.snapshot(recipe),
                    getLevel().dimension().location() + "@" + getPos(), getLevel().getGameTime());
            data.recordProcessFact(getResearchTeamUUID(), "all_fourteen_wonders", receipt);
        }
    }
}
