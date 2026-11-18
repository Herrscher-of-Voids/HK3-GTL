package com.sirin.hk3gtl.common.machine.research;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;
import com.sirin.hk3gtl.common.research.Hk3ResearchRecipeRuntime;
import net.minecraft.nbt.Tag;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldTaskService;
import com.sirin.hk3gtl.common.machine.ParallelData;
import com.sirin.hk3gtl.mixin.overview.Hk3RecipeLogicOverviewAccessor;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import java.math.BigInteger;
import net.minecraft.network.chat.Component;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

 






public class Hk3LateIndustrialMachine extends Hk3ResearchProcessMachine {
    // 2026-10-30（修订182）：I40–I45复用同角色、非暂定与额定电压校验，界面公开未接线能力。
    private static final Map<String, Hk3ResearchProcessPlans.Plan> PLANS = Hk3ResearchProcessPlans.all().stream()
            .collect(Collectors.toUnmodifiableMap(Hk3ResearchProcessPlans.Plan::id, p -> p));
     
    private static final Map<String, Integer> PROCESS_TIERS = PLANS.values().stream().filter(p -> !p.provisional())
            .collect(Collectors.toUnmodifiableMap(Hk3ResearchProcessPlans.Plan::role, Hk3ResearchProcessPlans.Plan::energyTier, Math::max));
    private static final Set<String> WORLD_TASKS = Set.of("I26", "I27", "I28", "I29", "I30", "I31");

    public Hk3LateIndustrialMachine(IMachineBlockEntity holder, String role) {
        super(holder, role);
    }

    @Override public void onLoad() {
        super.onLoad();
        if (!isRemote() && worldTask()) subscribeServerTick(this::deliverWorldOutputs);
    }

    private void deliverWorldOutputs() {
        if (getLevel().getGameTime() % 20 != 0 || !isFormed() || getResearchTeamUUID() == null) return;
        com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleData.get(getLevel().getServer()).deliverOutputs(
                getLevel().getServer(), getResearchTeamUUID(), researchRole(),
                getLevel().dimension().location() + "@" + getPos(),
                com.sirin.hk3gtl.common.worldbubble.Hk3WorldOutputPorts.of(this));
    }

    @Override public int getTier() { return getDefinition().getTier(); }
    @Override public com.lowdragmc.lowdraglib.gui.modular.ModularUI createUI(net.minecraft.world.entity.player.Player player) {
        return researchRole().equals("I41") && !player.isShiftKeyDown()
                ? com.sirin.hk3gtl.common.dispatch.Hk3EnergyDispatchUI.create(this, player) : super.createUI(player);
    }
    private int processTier() {
        return PROCESS_TIERS.getOrDefault(researchRole(), getTier());
    }
    @Override public long getMaxVoltage() { return Hk3Values.getV(Math.max(getTier(), processTier())); }
    @Override public long getOverclockVoltage() { return getMaxVoltage(); }
    private boolean worldTask() { return researchRole().equals("I25") || WORLD_TASKS.contains(researchRole()); }
    @Override protected boolean enableMultiRecipe() { return !getDefinition().isGenerator(); }

    private boolean acceptsPlan(String id) {
        var plan = PLANS.get(id);
        return plan != null && plan.role().equals(researchRole()) && !plan.provisional()
                && plan.energyTier() <= Math.max(getTier(), processTier());
    }

    private boolean accepts(GTRecipe recipe) {
        if (recipe == null || worldTask() && !Hk3WorldTaskService.ready(this, recipe)) return false;
        if (researchRole().equals("I38") && getOwnerUUID() == null) return false;
        if (!recipe.data.contains(Hk3ResearchRecipeRuntime.MERGED))
            return acceptsPlan(recipe.data.getString(Hk3ResearchRecipeRuntime.PLAN));
        if (!recipe.data.contains(Hk3ResearchRecipeRuntime.MERGED, Tag.TAG_LIST)) return false;
        var entries = recipe.data.getList(Hk3ResearchRecipeRuntime.MERGED, Tag.TAG_COMPOUND);
        if (entries.isEmpty()) return false;
        for (var raw : entries)
            if (!acceptsPlan(((net.minecraft.nbt.CompoundTag) raw).getString(Hk3ResearchRecipeRuntime.PLAN))) return false;
        return true;
    }

    @Override public boolean beforeWorking(GTRecipe recipe) {
        return accepts(recipe) && super.beforeWorking(recipe);
    }

    @Override public GTRecipe fullModifyRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        if (!accepts(recipe)) return null;
        int duration = recipe.duration;
        var modified = super.fullModifyRecipe(recipe, params, result);
        // 维护仓可调整耗时；发电必须保留注册工时，避免重算燃料总能量。
        if (modified != null && getDefinition().isGenerator()) modified.duration = duration;
        if (modified != null && worldTask()) Hk3WorldTaskService.planned(modified, recipe);
        return modified;
    }

    @Override protected RecipeLogic createRecipeLogic(Object... args) {
        return new ProcessLogic(this) {
            @Override protected GTRecipe buildFinalNormalRecipe(ParallelData plan) {
                var running = super.buildFinalNormalRecipe(plan);
                if (running != null && worldTask()) Hk3WorldTaskService.planned(running, plan);
                return running;
            }
            @Override public void handleRecipeWorking() {
                var running = getLastRecipe();
                int before = progress;
                super.handleRecipeWorking();
                if (!worldTask() || running != getLastRecipe()) return;
                if (isWaiting() && ((Hk3RecipeLogicOverviewAccessor) (Object) this).hk3gtl$waitingReason().getContents()
                        instanceof net.minecraft.network.chat.contents.TranslatableContents text
                        && (text.getKey().equals("hk3gtl.recipe.power.balance")
                        || text.getKey().equals("hk3gtl.machine.honkai_payment_failed"))) {
                    progress = before;
                    running.data.putInt("hk3gtlWorldEnergyPausedProgress", before);
                    markLastRecipeDirty();
                } else if (running.data.contains("hk3gtlWorldEnergyPausedProgress")
                        && before == running.data.getInt("hk3gtlWorldEnergyPausedProgress") && progress == before + 1) {
                    running.data.remove("hk3gtlWorldEnergyPausedProgress");
                    markLastRecipeDirty();
                    com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(getLevel().getServer())
                            .produced(getOwnerUUID(), "receipt:166", 1);
                }
            }
            @Override public void setupRecipe(GTRecipe recipe) {
                var next = recipe.copy();
                next.data = recipe.data.copy();
                Hk3WorldTaskService.reset(next);
                super.setupRecipe(next);
            }
            @Override protected boolean handleRecipeIO(GTRecipe recipe, IO io) {
                if (io == IO.IN && worldTask())
                    return Hk3WorldTaskService.start(Hk3LateIndustrialMachine.this, recipe, () -> super.handleRecipeIO(recipe, io));
                return super.handleRecipeIO(recipe, io);
            }
            @Override protected void doDamping() {
                if (!process.getDefinition().isGenerator()) super.doDamping();
            }
            @Override protected long getMaxParallel() {
                // 发电合同按一棒批次结算，避免高阶EU/t倍乘超过long后失真。
                if (process.getDefinition().isGenerator()) return 1;
                return worldTask() ? Math.min(super.getMaxParallel(), Hk3WorldTaskService.maxParallel(Hk3LateIndustrialMachine.this))
                        : super.getMaxParallel();
            }
        };
    }

    @Override
    public net.minecraft.world.InteractionResult onUse(net.minecraft.world.level.block.state.BlockState state,
            net.minecraft.world.level.Level world, net.minecraft.core.BlockPos pos,
            net.minecraft.world.entity.player.Player player, net.minecraft.world.InteractionHand hand,
            net.minecraft.world.phys.BlockHitResult hit) {
        if (!isFormed() && player.isShiftKeyDown() && player.getItemInHand(hand).isEmpty()) {
            if (!world.isClientSide())
                player.displayClientMessage(Component.translatable("hk3gtl.machine.late_industry.external_preview"), false);
            return net.minecraft.world.InteractionResult.SUCCESS;
        }
        return super.onUse(state, world, pos, player, hand, hit);
    }

    @Override protected void onRequiredProcessOutput(GTRecipe recipe) {
        if (researchRole().equals("I38")) {
            BigInteger credit = recipe.data.contains(CREDIT, Tag.TAG_STRING)
                    ? new BigInteger(recipe.data.getString(CREDIT)) : BigInteger.valueOf(recipe.data.getLong(CREDIT));
            HonkaiWirelessNetwork.insert(getOwnerUUID(), credit, false);
        }
        if (worldTask()) Hk3WorldTaskService.completed(this, recipe);
    }

    @Override public void onMachineRemoved() {
        if (!isRemote() && worldTask()) Hk3WorldTaskService.cancel(this, getRecipeLogic().getLastRecipe());
        super.onMachineRemoved();
    }

    @Override public void addDisplayText(List<Component> lines) {
        super.addDisplayText(lines);
        lines.add(Component.translatable("hk3gtl.machine.late_industry.rated",
                com.gregtechceu.gtceu.api.GTValues.VNF[getTier()]));
        lines.add(Component.translatable("hk3gtl.machine.late_industry.process_rating",
                com.gregtechceu.gtceu.api.GTValues.VNF[Math.max(getTier(), processTier())]));
        lines.add(Component.translatable("hk3gtl.machine.late_industry.processes_available"));
        if (getDefinition().isGenerator())
            lines.add(Component.translatable("hk3gtl.machine.late_industry.grid_output"));
    }
}
