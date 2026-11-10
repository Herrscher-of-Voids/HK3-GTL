package com.sirin.hk3gtl.common.overview;

import com.gregtechceu.gtceu.api.capability.IWorkable;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.machine.feature.IUIMachine;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiController;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData.Descriptor;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData.Observation;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData.State;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import com.sirin.hk3gtl.mixin.overview.Hk3RecipeLogicOverviewAccessor;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.TranslatableContents;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.fml.ModList;

import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Set;

/**
 * 【文件职责】只读适配GT及其附属的公开机器接口，独立核验现场绑定权限。
 * 【变更记录 #1】2026-10-19 02:07:23（第1次备注 · 修订171）
 * 删除：无。新增：注册身份、公开工作状态、明确等待原因分类和现有领地主队权限校验。
 * 修改：无；没有明确归属的旧机器不按最近玩家、可打开界面或管理员绕过权限抢先认领。
 * 用途：为总览索引提供可审计快照；不检测结构、不模拟配方、不读库存、不启停机器、不加载区块。
 */
/**
 * 【变更记录 #2】2026-10-19 02:16:00（第2次备注 · 修订171）
 * 删除：对仅运行时引入的FTB Chunks编译期链接。
 * 新增：精确公开API反射桥；修改：依赖缺失、API签名变化或调用失败均拒绝绑定。
 * 用途：维持现有依赖边界，不为权限功能改换整合包；多方块部件类别不再统称仓室。
 */
public final class Hk3MachineOverviewAdapter {
    private Hk3MachineOverviewAdapter() {}

    public static Descriptor describe(MetaMachine machine) {
        String type = machine instanceof IMultiController ? "多方块控制器"
                : machine instanceof IMultiPart ? "多方块部件"
                : machine instanceof IRecipeLogicMachine ? "单方块配方机器" : "其他GT机器";
        return new Descriptor(machine.getDefinition().getId().toString(), machine.getDefinition().getDescriptionId(),
                type, machine instanceof IWorkable);
    }

    public static Observation sample(MetaMachine machine) {
        try {
            if (machine instanceof IMultiController controller && !controller.isFormed())
                return new Observation(State.UNFORMED, "控制器报告结构未成型");
            if (machine instanceof IRecipeLogicMachine recipeMachine) {
                var logic = recipeMachine.getRecipeLogic();
                Component reason = logic instanceof Hk3RecipeLogicOverviewAccessor access ? access.hk3gtl$waitingReason() : null;
                return recipeStatus(logic.isWorkingEnabled(), logic.isWorking(), logic.isWaiting(), reason);
            }
            if (machine instanceof IWorkable workable) {
                if (!workable.isWorkingEnabled()) return new Observation(State.STOPPED, "机器报告工作开关已关闭");
                return workable.isActive() ? new Observation(State.RUNNING, "机器公开工作接口报告活动")
                        : new Observation(State.UNKNOWN, "机器未活动；没有可区分的停机原因");
            }
            return new Observation(State.UNADAPTED, "仅登记身份；该控制器没有受支持的工作状态接口");
        } catch (RuntimeException | LinkageError failure) {
            return new Observation(State.UNKNOWN, "第三方控制器状态读取失败；未推断运行结果");
        }
    }

    /** 等待与空闲不等于缺电；只依据GT实际提供的能力翻译键分类。 */
    public static Observation recipeStatus(boolean enabled, boolean working, boolean waiting, Component reason) {
        if (!enabled) return new Observation(State.STOPPED, "配方工作开关已关闭");
        if (working) return new Observation(State.RUNNING, "配方逻辑报告正在运行");
        if (!waiting) return new Observation(State.UNKNOWN, "配方空闲；未确定缺料、输出阻塞或其他条件");
        Set<String> keys = translationKeys(reason);
        if (keys.contains("gtceu.recipe_logic.insufficient_in")) {
            if (keys.contains("recipe.capability.eu.name"))
                return new Observation(State.NEED_ENERGY, "GT报告输入电能不足");
            if (keys.contains("recipe.capability.item.name") || keys.contains("recipe.capability.fluid.name"))
                return new Observation(State.NEED_INPUT, "GT报告物品或流体输入不足");
        }
        if (keys.contains("gtceu.recipe_logic.insufficient_fuel"))
            return new Observation(State.NEED_INPUT, "GT报告燃料不足");
        if (keys.contains("gtceu.recipe_logic.insufficient_out"))
            return new Observation(State.UNKNOWN, "GT报告输出受阻；未误标为缺料或缺电");
        return new Observation(State.UNKNOWN, "配方正在等待；尚无可安全分类的原因");
    }

    /** 有限遍历组件树；不解析本地化文字，避免语言变化或字面伪装造成误分类。 */
    private static Set<String> translationKeys(Component reason) {
        Set<String> keys = new HashSet<>();
        if (reason == null) return keys;
        ArrayDeque<Component> pending = new ArrayDeque<>();
        pending.add(reason);
        int remaining = 64;
        while (!pending.isEmpty() && remaining-- > 0) {
            Component part = pending.removeFirst();
            if (part.getContents() instanceof TranslatableContents translated) {
                keys.add(translated.getKey());
                for (Object argument : translated.getArgs())
                    if (argument instanceof Component nested && pending.size() < 64) pending.addLast(nested);
            }
            for (Component sibling : part.getSiblings()) if (pending.size() < 64) pending.addLast(sibling);
        }
        return keys;
    }

    /** 此方法只确认现场权限；服务仍须拒绝覆盖账本里其他团队的既有归属。 */
    public static boolean canBind(ServerPlayer actor, MetaMachine machine) {
        if (actor == null || machine == null || actor.isSpectator() || !(machine.getLevel() instanceof ServerLevel level)
                || actor.level() != level || !level.getServer().isSameThread() || machine.isInValid()
                || actor.distanceToSqr(Vec3.atCenterOf(machine.getPos())) > 64 || !level.hasChunkAt(machine.getPos())
                || !(level.getBlockEntity(machine.getPos()) instanceof IMachineBlockEntity holder)
                || holder.getMetaMachine() != machine) return false;
        try {
            if (!(machine instanceof IUIMachine ui) || !ui.shouldOpenUI(actor, InteractionHand.MAIN_HAND,
                    new BlockHitResult(Vec3.atCenterOf(machine.getPos()), actor.getDirection().getOpposite(), machine.getPos(), false)))
                return false;
            if (machine instanceof Hk3WorkableMultiblockMachine local) {
                var team = local.getResearchTeamUUID();
                return team != null && team.equals(Hk3ResearchTeams.scope(actor.server, actor.getUUID()))
                        && Hk3ResearchTeams.canManage(actor.server, team, actor.getUUID());
            }
            return ModList.get().isLoaded("ftbchunks") && ClaimedPermission.allowed(actor, machine);
        } catch (RuntimeException | LinkageError failure) {
            return false;
        }
    }

    /** 可选领地API延迟解析；盟友、公共交互与管理员绕过均不等同主队身份。 */
    private static final class ClaimedPermission {
        private static boolean allowed(ServerPlayer actor, MetaMachine machine) {
            try {
                Class<?> apiType = Class.forName("dev.ftb.mods.ftbchunks.api.FTBChunksAPI$API");
                Class<?> managerType = Class.forName("dev.ftb.mods.ftbchunks.api.ClaimedChunkManager");
                Class<?> protectionType = Class.forName("dev.ftb.mods.ftbchunks.api.Protection");
                Class<?> positionType = Class.forName("dev.ftb.mods.ftblibrary.math.ChunkDimPos");
                Object api = Class.forName("dev.ftb.mods.ftbchunks.api.FTBChunksAPI").getMethod("api").invoke(null);
                if (!Boolean.TRUE.equals(apiType.getMethod("isManagerLoaded").invoke(api))) return false;
                Object manager = apiType.getMethod("getManager").invoke(api);
                Object position = positionType.getConstructor(net.minecraft.world.level.Level.class, net.minecraft.core.BlockPos.class)
                        .newInstance(actor.level(), machine.getPos());
                Object claim = managerType.getMethod("getChunk", positionType).invoke(manager, position);
                if (claim == null) return false;
                Object team = Class.forName("dev.ftb.mods.ftbchunks.api.ClaimedChunk").getMethod("getTeamData").invoke(claim);
                if (!Boolean.TRUE.equals(Class.forName("dev.ftb.mods.ftbchunks.api.ChunkTeamData")
                        .getMethod("isTeamMember", java.util.UUID.class).invoke(team, actor.getUUID()))) return false;
                Object protection = protectionType.getField("EDIT_AND_INTERACT_BLOCK").get(null);
                Object prevented = managerType.getMethod("shouldPreventInteraction", net.minecraft.world.entity.Entity.class,
                                InteractionHand.class, net.minecraft.core.BlockPos.class, protectionType, net.minecraft.world.entity.Entity.class)
                        .invoke(manager, actor, InteractionHand.MAIN_HAND, machine.getPos(), protection, null);
                return Boolean.FALSE.equals(prevented);
            } catch (ReflectiveOperationException | RuntimeException | LinkageError unavailable) {
                return false;
            }
        }
    }
}
