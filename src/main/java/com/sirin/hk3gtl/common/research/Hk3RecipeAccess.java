package com.sirin.hk3gtl.common.research;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.config.Hk3ResearchSettings;
import com.sirin.hk3gtl.common.easter.Hk3EggProduction;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.gtlcore.gtlcore.common.machine.multiblock.electric.SuprachronalAssemblyLineMachine;
import java.util.ArrayList;
import java.util.List;

public final class Hk3RecipeAccess {
    private Hk3RecipeAccess() {}

    public static Hk3ResearchRequirementPolicy.Requirements effectiveRequirements(GTRecipe recipe) {
        if (recipe == null) return Hk3ResearchRequirementPolicy.collect(
                List.of(), List.of(), false, Hk3RecipeResearchGate::isCurrentResearchId);
        var batch = new ArrayList<Object>();
        boolean malformed = recipe.data != null && recipe.data.getBoolean("hk3gtlMergedPlan")
                && !recipe.data.contains(Hk3ResearchRequirementPolicy.METADATA_KEY);
        if (recipe.data != null && recipe.data.contains(Hk3ResearchRequirementPolicy.METADATA_KEY)) {
            var raw = recipe.data.get(Hk3ResearchRequirementPolicy.METADATA_KEY);
            if (raw instanceof ListTag list) {
                if (list.getElementType() != Tag.TAG_END && list.getElementType() != Tag.TAG_STRING)
                    malformed = true;
                for (var tag : list) {
                    if (tag.getId() == Tag.TAG_STRING) batch.add(tag.getAsString());
                    else malformed = true;
                }
            } else malformed = true;
        }
        return Hk3ResearchRequirementPolicy.collect(Hk3RecipeResearchGate.getAllRequiredResearch(recipe.id),
                batch, malformed, Hk3RecipeResearchGate::isCurrentResearchId);
    }

    public static boolean blocks(GTRecipe recipe, MetaMachine machine) {
        if (recipe == null) return false;
        if ((recipe.data.contains(Hk3ResearchRecipeRuntime.PLAN) || recipe.data.contains(Hk3ResearchRecipeRuntime.MERGED))
                && !(machine instanceof com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine)
                && (machine == null || machine.getLevel() == null
                    || !machine.getLevel().isClientSide() && !Hk3ResearchRecipeRuntime.allowed(machine, recipe))) return true;
        if (!Hk3ResearchSettings.enabled()) return false;
        var requirements = effectiveRequirements(recipe);
        if (!requirements.valid()) return true;
        if (requirements.requirements().isEmpty()) return false;
        if (machine == null) return true;
        return !Hk3ResearchRequirementPolicy.evaluate(requirements,
                research -> !blocksResearch(research, machine)).allowed();
    }
    public static Component blockedReason(GTRecipe recipe, MetaMachine machine) {
        if (recipe.data.contains(Hk3ResearchRecipeRuntime.PLAN)
                && machine instanceof SuprachronalAssemblyLineMachine
                && machine.getLevel() instanceof ServerLevel) {
            var requirements = effectiveRequirements(recipe);
            if (requirements.valid() && !requirements.requirements().isEmpty()) {
                if (!((BlockEntity) machine.getHolder()).getPersistentData()
                        .hasUUID(Hk3EggProduction.OWNER))
                    return Component.translatable("hk3gtl.compat.research_owner_missing");
                var missing = Hk3ResearchRequirementPolicy.evaluate(requirements, id -> !blocksResearch(id, machine)).missing();
                if (!missing.isEmpty()) return Component.translatable("hk3gtl.compat.research_team_missing", String.join(", ", missing));
            }
            return Component.translatable("hk3gtl.compat.execution_plan_blocked");
        }
        return Component.translatable("hk3gtl.compat.research_locked");
    }

    private static boolean blocksResearch(String research, MetaMachine machine) {
        if (!Hk3RecipeResearchGate.isCurrentResearchId(research)) return true;
        var level = machine.getLevel();
        if (level == null) return true;
        if (level.isClientSide()) return false;
        if (machine instanceof Hk3WorkableMultiblockMachine owned) {
            if (owned.getOwnerUUID() == null || level.getServer() == null) return true;
            var scope = owned.getResearchTeamUUID();
            return scope == null || !Hk3ResearchData.get(level.getServer()).permits(scope, research);
        }
        if (level.getServer() == null || !(machine.getHolder() instanceof BlockEntity holder)
                || !holder.getPersistentData().hasUUID(Hk3EggProduction.OWNER)) return true;
        var owner = holder.getPersistentData().getUUID(Hk3EggProduction.OWNER);
        var scope = Hk3ResearchTeams.scope(level.getServer(), owner);
        return !Hk3ResearchData.get(level.getServer()).permits(scope, research);
    }
}

