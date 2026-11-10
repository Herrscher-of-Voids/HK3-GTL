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
import net.minecraft.network.chat.Component;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 【文件职责】I19至I28使用批准档位、固定职责与既有真实IO/研究结算；不创造暂定任务。
 * 【变更记录 #1】2026-10-26 19:57:03（修订177）
 * 删除：无。新增：单批发电、批准电压上限、仅接受同源计划和真实世界泡任务锁。
 * 修改：发电不超频、不无限倍乘，输出沿玩家电网工作票据；世界泡尚无可信目标接线时拒绝消费。
 * 用途：正式控制器可以成型、识别工作仓，工艺批准和真实任务实现仍独立核验。
 */
public class Hk3LateIndustrialMachine extends Hk3ResearchProcessMachine {
    // 2026-10-30（修订182）：I40–I45复用同角色、非暂定与额定电压校验，界面公开未接线能力。
    private static final Map<String, Hk3ResearchProcessPlans.Plan> PLANS = Hk3ResearchProcessPlans.all().stream()
            .collect(Collectors.toUnmodifiableMap(Hk3ResearchProcessPlans.Plan::id, p -> p));
    // 【变更记录 #2】2026-10-27（修订180）：模拟批次三机继续锁定任务，建筑接入不创造结算来源。
    private static final Set<String> WORLD_TASKS = Set.of("I26", "I27", "I28", "I29", "I30", "I31");

    public Hk3LateIndustrialMachine(IMachineBlockEntity holder, String role) {
        super(holder, role);
    }

    @Override public int getTier() { return getDefinition().getTier(); }
    @Override public long getMaxVoltage() { return Hk3Values.getV(getTier()); }
    @Override public long getOverclockVoltage() { return getMaxVoltage(); }
    @Override protected boolean enableMultiRecipe() { return !getDefinition().isGenerator(); }

    private boolean acceptsPlan(String id) {
        var plan = PLANS.get(id);
        return plan != null && plan.role().equals(researchRole()) && !plan.provisional()
                && plan.energyTier() <= getTier() && !WORLD_TASKS.contains(researchRole());
    }

    private boolean accepts(GTRecipe recipe) {
        if (recipe == null) return false;
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
        return accepts(recipe) ? super.fullModifyRecipe(recipe, params, result) : null;
    }

    @Override protected RecipeLogic createRecipeLogic(Object... args) {
        return new ProcessLogic(this) {
            @Override protected long getMaxParallel() {
                // 发电合同按一棒批次结算，避免高阶EU/t倍乘超过long后失真。
                return process.getDefinition().isGenerator() ? 1 : super.getMaxParallel();
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

    @Override public void addDisplayText(List<Component> lines) {
        super.addDisplayText(lines);
        lines.add(Component.translatable("hk3gtl.machine.late_industry.rated",
                com.gregtechceu.gtceu.api.GTValues.VNF[getTier()]));
        lines.add(Component.translatable(WORLD_TASKS.contains(researchRole())
                ? "hk3gtl.machine.late_industry.world_task_pending"
                : "hk3gtl.machine.industrial_extension.provisional_locked"));
        String pending = switch (researchRole()) {
            case "I41" -> "hk3gtl.machine.late_industry.dispatch_pending";
            case "I43" -> "hk3gtl.machine.late_industry.acceptance_rating_limit";
            case "I44" -> "hk3gtl.machine.late_industry.beacon_pending";
            case "I45" -> "hk3gtl.machine.late_industry.travel_pending";
            default -> null;
        };
        if (pending != null) lines.add(Component.translatable(pending));
        if (getDefinition().isGenerator())
            lines.add(Component.translatable("hk3gtl.machine.late_industry.grid_output"));
    }
}
