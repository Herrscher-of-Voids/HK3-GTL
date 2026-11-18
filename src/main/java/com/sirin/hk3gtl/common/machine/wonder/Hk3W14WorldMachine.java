package com.sirin.hk3gtl.common.machine.wonder;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.sirin.hk3gtl.common.machine.ParallelData;
import com.sirin.hk3gtl.common.worldbubble.Hk3W14WorldTaskService;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleData;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldOutputPorts;
import com.sirin.hk3gtl.mixin.overview.Hk3RecipeLogicOverviewAccessor;

import java.util.Set;

/** 批量模拟世界沿同一真实目标完成构筑、稳定与退役。 */
public final class Hk3W14WorldMachine extends Hk3AnimatedWonderMachine {
    public Hk3W14WorldMachine(IMachineBlockEntity holder) { super(holder, "W14"); }

    @Override public void onLoad() {
        super.onLoad();
        if (!isRemote()) subscribeServerTick(this::deliverWorldOutputs);
    }
    private void deliverWorldOutputs() {
        if (getLevel().getGameTime() % 20 != 0 || !isFormed() || getResearchTeamUUID() == null) return;
        Hk3WorldBubbleData.get(getLevel().getServer()).deliverOutputs(getLevel().getServer(), getResearchTeamUUID(), "W14",
                getLevel().dimension().location() + "@" + getPos(), Hk3WorldOutputPorts.of(this));
    }
    @Override protected boolean productionReady(GTRecipe recipe) {
        return super.productionReady(recipe) && Hk3W14WorldTaskService.ready(this, recipe);
    }
    @Override public GTRecipe fullModifyRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        var modified = super.fullModifyRecipe(recipe, params, result);
        if (modified != null) Hk3W14WorldTaskService.planned(modified, recipe);
        return modified;
    }
    @Override protected RecipeLogic createRecipeLogic(Object... args) {
        return new ProcessLogic(this) {
            @Override protected ParallelData calculateParallels(Set<GTRecipe> recipes) {
                var plan = super.calculateParallels(recipes);
                return plan == null ? null : Hk3W14WorldTaskService.limit(Hk3W14WorldMachine.this, plan,
                        recipe -> fullModifyRecipe(recipe, ocParams, ocResult));
            }
            @Override protected GTRecipe buildFinalNormalRecipe(ParallelData plan) {
                var running = super.buildFinalNormalRecipe(plan);
                if (running != null) Hk3W14WorldTaskService.planned(running, plan);
                return running;
            }
            @Override public void setupRecipe(GTRecipe recipe) {
                var next = recipe.copy(); next.data = recipe.data.copy(); Hk3W14WorldTaskService.reset(next);
                super.setupRecipe(next);
            }
            @Override protected boolean handleRecipeIO(GTRecipe recipe, IO io) {
                if (io == IO.IN && !Hk3W14WorldTaskService.ready(Hk3W14WorldMachine.this, recipe)) return false;
                boolean committed = super.handleRecipeIO(recipe, io);
                if (committed && io == IO.IN) {
                    Hk3W14WorldTaskService.started(Hk3W14WorldMachine.this, recipe);
                    Hk3W14WorldMachine.this.markDirty();
                }
                return committed;
            }
            @Override public void handleRecipeWorking() {
                var running = getLastRecipe(); int before = progress;
                super.handleRecipeWorking();
                if (running != getLastRecipe()) return;
                if (isWaiting() && ((Hk3RecipeLogicOverviewAccessor) (Object) this).hk3gtl$waitingReason().getContents()
                        instanceof net.minecraft.network.chat.contents.TranslatableContents text
                        && (text.getKey().equals("hk3gtl.recipe.power.balance")
                        || text.getKey().equals("hk3gtl.machine.honkai_payment_failed"))) {
                    progress = before; running.data.putInt("hk3gtlWorldEnergyPausedProgress", before); markLastRecipeDirty();
                } else if (running.data.contains("hk3gtlWorldEnergyPausedProgress")
                        && before == running.data.getInt("hk3gtlWorldEnergyPausedProgress") && progress == before + 1) {
                    running.data.remove("hk3gtlWorldEnergyPausedProgress"); markLastRecipeDirty();
                    com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(getLevel().getServer())
                            .produced(getOwnerUUID(), "receipt:166", 1);
                }
            }
        };
    }
    @Override protected void onRequiredProcessOutput(GTRecipe recipe) {
        super.onRequiredProcessOutput(recipe);
        Hk3W14WorldTaskService.completed(this, recipe);
    }
    @Override public void onMachineRemoved() {
        if (!isRemote()) Hk3W14WorldTaskService.cancel(this, getRecipeLogic().getLastRecipe());
        super.onMachineRemoved();
    }
}
