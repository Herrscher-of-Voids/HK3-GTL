package com.sirin.hk3gtl.common.machine.research;



/**
 * 【文件职责／本轮边界】团队共享任务、成员个人付款、全队离线暂停正式研究；实验固定速度续做，空闲不计算注视度。
 * 【变更记录 #3】2026-09-29 21:06:40（第 3 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：团队共享任务、成员个人付款、全队离线暂停正式研究；实验固定速度续做，空闲不计算注视度。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */

/** 【变更记录 · 内测5修订100】2026-09-29：落实已批准研究费用、三公式及离线账户规则。 */

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.GTValues;
import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.sirin.hk3gtl.common.gui.Hk3ResearchTerminalWidget;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.BlockHitResult;
import java.util.List;

/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-26 21:56:00（第 1 次备注 · 内测5修订75）
 * 删除：使用首项支付材料作为课题图标的逻辑。
 * 新增：独立研究成果图标目录及研究所不足聊天提示的具体阶级。
 * 修改：图标只影响显示；研究点、材料支付与用电规则保持原服务端流程。
 * 用途：课题列表显示可解锁成果，避免全部显示MAX电路；图标不授予成果。
 */
/** 【变更记录 #2】2026-09-29 18:57:18（内测5修订95）：真实研究完成时通知本人手机；不从静态标记或持有物造假。 */
/**
 * 【变更记录 #4】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：增加OPR入口、研究所课题权限与完整来源提示，保持未审批高阶结构不注册。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #5】2026-09-30 15:49:23（第5次编号备注 · 内测5修订109）
 * 删除：过期的计算或无运行依据的分支；保留历史备注。
 * 新增／修改：正式研究统一在线团队最高有效注视；按研究所位置查询真实锚，预览、付款与推进一致；实验离线政策不变。
 * 用途：统一注视与研究联动，服务端判定；不新增结构或贴图。
 */
/**
 * 【变更记录 #6】2026-09-30 16:20:43（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：研究/实验真实完成后投递给当前团队包括离线成员；真实课题名与开放摘要，基线不冒充完整实验或研究。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/** 【变更记录 #7】2026-10-01 04:21:47（修订128）：删除：旧固定上限或被替代的分支；新增/修改：正式研究完成回调仅给实际付款参与者可选旁注，不把实验完成或队友广播当亲历；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 04:58:34（修订128）：删除：旧固定上限或被替代的分支；新增/修改：研究完成旁注保存给真实付款者，离线时不丢失；不改变开题付款或完成资格；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #9】2026-10-01 05:47:22（修订128）：删除：无；新增/修改：最低速度直接取正式公式在注视上限、无抑制无加速的值；仅实际扣电推进后给付款者旁注，S01免压不算；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/**
 * 【变更记录 #10】2026-11-04 01:23:43（第10次备注 · 内测5修订194）
 * - 删除：领取退款后只等待背包与账本分别自动保存的调用。
 * - 新增：无；修改：领取入口接Hk3ResearchPayment.claimRefunds，真实库存分配不变。
 * - 用途：退款领取跨文件提交，硬崩后可重放且不重复发放，满包余量仍留账。
 */
public final class Hk3ResearchInstituteMachine extends Hk3WorkableMultiblockMachine {
    private final int lab;

    /** 阶级是注册定义常量，非法值拒绝；不通过NBT或玩家包升级研究所。 / Lab level is fixed by registration, never client/NBT-upgradable. */
    public Hk3ResearchInstituteMachine(IMachineBlockEntity holder, int lab) {
        super(holder); Hk3ResearchMath.slots(lab); this.lab=lab;
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override protected boolean enableMultiRecipe() { return false; }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override protected com.gregtechceu.gtceu.api.machine.trait.RecipeLogic createRecipeLogic(Object... args) {
        return new com.gregtechceu.gtceu.api.machine.trait.RecipeLogic(this) {
            @Override public void serverTick() { /* 中文说明：该处说明已按当前代码行为整理。*/ }
        };
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override public void onLoad() { super.onLoad(); if (!isRemote()) subscribeServerTick(this::researchTick); }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    private String facility() { return getLevel().dimension().location()+"@"+getPos().asLong(); }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private void researchTick() {
        if (isInValid() || !isFormed() || !getRecipeLogic().isWorkingEnabled() || getOwnerUUID()==null || getLevel().getServer()==null) return;
        var server=getLevel().getServer(); var scope=getResearchTeamUUID();
        var data=Hk3ResearchData.get(server);
        if(scope==null||!com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts
                .permitsMachine(data,scope,String.format(java.util.Locale.ROOT,"S%02d",lab),false))return;
        var jobs=data.activeResearch(scope,facility());
        if(jobs.isEmpty())return;
        var online=Hk3ResearchTeams.online(server,scope);
        double gaze=Hk3ResearchTeams.gaze(server,scope);
        double speed=Hk3ResearchMath.speed(lab,gaze,suppression(),false,false);
        // 锚与加速模块只有接入实际设施验证后才能启用，此处不凭附近方块外观假定运行。
        // 中文备注：该处备注已按当前代码行为整理，不使用问号占位。
        for (var job : jobs) {
            if (job.quote().lab()!=lab) continue;
            boolean[] energyPaid={false};
            var result=data.advanceResearch(scope, job.quote().topic(), facility(), server.overworld().getGameTime(),
                    true, !online.isEmpty(), speed, () -> {energyPaid[0]=debitEnergy(job.quote().eut());return energyPaid[0];});
            if(lab>1&&energyPaid[0]&&speed<=Hk3ResearchMath.speed(lab,com.sirin.hk3gtl.common.constants.Hk3Constants.GAZE_MAX,0,false,false)){
                var payerId=com.sirin.hk3gtl.common.research.Hk3ResearchData.payer(scope,job.quote());
                com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(server).produced(payerId,"receipt:47",1);
            }
            if (result==Hk3ResearchWorkQueue.Outcome.COMPLETED) {
                com.sirin.hk3gtl.common.phone.Hk3PhoneService.researchCompleted(server, scope, job.quote().topic());
                if(com.sirin.hk3gtl.common.research.Hk3LabExperimentRules.get(job.quote().topic())==null){
                    var payerId=com.sirin.hk3gtl.common.research.Hk3ResearchData.payer(scope,job.quote());
                    com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(server).produced(payerId,"receipt:165",1);
                }
                for (var member:online) {
                    Hk3ResearchManager.syncClientResearchState(member);

                }
            }
        }
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private boolean debitEnergy(long amount) {
        var energy=getEnergyContainer();
        if (energy.getEnergyStored()<amount) return false;
        long removed=energy.removeEnergy(amount);
        if (removed==amount) return true;
        if (removed>0) energy.addEnergy(removed);
        return false;
    }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    private boolean authorized(Player player) {
        if(player instanceof ServerPlayer sp) Hk3ResearchTeams.refresh(sp.server);
        if(player instanceof ServerPlayer sp && getResearchTeamUUID()!=null
                && !com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts.permitsMachine(
                        Hk3ResearchData.get(sp),getResearchTeamUUID(),String.format(java.util.Locale.ROOT,"S%02d",lab),false))return false;
        return !isInValid() && getOwnerUUID()!=null && player instanceof ServerPlayer sp && Hk3ResearchData.get(sp).isMember(player.getUUID(),getResearchTeamUUID())
                && getLevel()==player.level() && player.distanceToSqr(getPos().getX()+0.5, getPos().getY()+0.5, getPos().getZ()+0.5)<=64
                && getLevel().getBlockEntity(getPos()) instanceof IMachineBlockEntity be && be.getMetaMachine()==this;
    }

    @Override public boolean shouldOpenUI(Player player, InteractionHand hand, BlockHitResult hit) {
        return player.level().isClientSide || authorized(player);
    }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    @Override public ModularUI createUI(Player player) {
        Session session = new Session(player);
        return new ModularUI(Hk3ResearchTerminalWidget.WIDTH, Hk3ResearchTerminalWidget.HEIGHT, this, player)
                .widget(new Hk3ResearchTerminalWidget(session::snapshot, session::action));
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private final class Session {
        private final Player player;
        private String selected = Hk3ResearchPlans.all().keySet().iterator().next();
        private String feedback = "";
        private Session(Player player) { this.player = player; }

        /** 中文说明：该处说明已按当前代码行为整理。*/
        private CompoundTag snapshot() {
            CompoundTag view = new CompoundTag();
            if (!(player instanceof ServerPlayer server) || !authorized(server)) return view;
            var data = Hk3ResearchData.get(server);
            var owner = getResearchTeamUUID();
            view.putBoolean("authorized", true);
            view.putBoolean("formed", isFormed());
            view.putBoolean("enabled", getRecipeLogic().isWorkingEnabled());
            view.putInt("lab", lab);
            view.putInt("slots", Hk3ResearchMath.slots(lab));
            view.putInt("active", data.activeResearch(owner, facility()).size());
            view.putString("points", data.points(server.getUUID()).toString());
            view.putString("selected", selected);
            view.putString("feedback", feedback);
            ListTag topics = new ListTag();
            for (var plan : Hk3ResearchPlans.all().values()) {
                var definition = Hk3ResearchCatalog.bundled().get(plan.id());
                var job = data.displayJob(owner, plan.id());
                boolean done = data.completed(owner, plan.id());
                boolean ready = lab >= definition.lab() && data.hasExperiment(owner, plan.id())
                        && definition.prerequisites().stream().allMatch(id -> data.completed(owner, id));
                CompoundTag row = new CompoundTag();
                row.putString("id", plan.id());
                // 状态0锁定/1满足知识条件/2在研/3完成；成型与供电在独立状态栏呈现。
                // 中文备注：该处备注已按当前代码行为整理，不使用问号占位。
                row.putInt("state", done ? 3 : job != null ? 2 : ready ? 1 : 0);
                row.putInt("lab", definition.lab());
                row.put("icon", Hk3ResearchIcons.stack(plan.id()).save(new CompoundTag()));
                topics.add(row);
            }
            view.put("topics", topics);
            var plan = Hk3ResearchPlans.get(selected);
            var topic = Hk3ResearchCatalog.bundled().get(selected);
            var job = data.displayJob(owner, selected);
            view.putBoolean("labExperiment",job!=null && Hk3LabExperimentRules.get(job.quote().topic())!=null);
            view.putBoolean("canExperiment",isFormed() && job==null && !data.hasExperiment(owner,selected)
                    && !Hk3LabExperimentRules.next(selected,data.hasLabBaseline(owner)).isEmpty()
                    && lab>=topic.lab() && topic.prerequisites().stream().allMatch(p -> data.completed(owner,p)));
            view.putInt("requiredLab", topic.lab());
            view.putInt("tier", topic.tier());
            view.putString("evidence", plan.evidence());
            var contract=Hk3ResearchExecutionContracts.get(selected);
            view.putString("executionSource",contract.source());
            view.putString("executionSuccess",contract.success());
            view.putString("result", plan.result());
            view.putString("story", Hk3ResearchStory.get(selected));
            view.putString("blocker", blocker(server));
            view.putBoolean("experiment", data.hasExperiment(owner, selected));
            view.putLong("cost", plan.points());
            view.putLong("seconds", plan.ticks() / 20);
            view.putLong("eut", job == null ? plan.eut() : job.quote().eut());
            // 正式课题按前档供电；固定实验使用其已批准的MAX或QSV，不沿用课题档位。
            view.putInt("powerTier",job!=null && Hk3LabExperimentRules.get(job.quote().topic())!=null
                    ? (job.quote().topic().equals("LAB-ALE")||job.quote().topic().equals("LAB-OPR")?GTValues.MAX:19)
                    : Math.max(GTValues.MAX,13+topic.tier()));
            view.putBoolean("running", job != null);
            view.putBoolean("canCancel", job!=null && Hk3ResearchData.payer(owner,job.quote()).equals(server.getUUID()));
            view.putInt("refunds",data.refundItems(server.getUUID()).size());
            view.putBoolean("localJob", job != null && facility().equals(job.quote().facility()));
            view.putBoolean("done", data.completed(owner, selected));
            view.putDouble("progress", job == null ? (data.completed(owner, selected) ? 1 : 0)
                    : Math.min(1, Math.max(0, job.progress() / job.quote().ticks())));
            view.putLong("remaining", job == null ? plan.ticks() / 20
                    : (long)Math.ceil(Math.max(0, job.quote().ticks() - job.progress()) / 20.0));
            view.putBoolean("powered", getEnergyContainer().getEnergyStored() >= view.getLong("eut"));
            ListTag prerequisites = new ListTag();
            for (String parent : topic.prerequisites()) {
                CompoundTag prerequisite = new CompoundTag();
                prerequisite.putString("id", parent); prerequisite.putBoolean("done", data.completed(owner, parent));
                prerequisites.add(prerequisite);
            }
            view.put("prerequisites", prerequisites);
            ListTag materials = new ListTag();
            for (var cost : scaled(plan, server)) {
                CompoundTag material = new CompoundTag();
                material.putString("tag", cost.tag()); material.putLong("count", cost.count());
                material.put("item", representative(cost.tag()).save(new CompoundTag()));
                var tag = TagKey.create(Registries.ITEM, new ResourceLocation(cost.tag()));
                long available = 0;
                // 与实际扣费一致，仅主背包36槽；数量是提示，重叠标签仍由原支付分配器复核。
                // 中文备注：该处备注已按当前代码行为整理，不使用问号占位。
                for (int i = 0; i < 36; i++) {
                    ItemStack stack = server.getInventory().getItem(i);
                    if (stack.is(tag)) available += stack.getCount();
                }
                material.putLong("available", available); materials.add(material);
            }
            view.put("materials", materials);
            view.putBoolean("canStart", isFormed() && job == null && !data.completed(owner, selected)
                    && lab >= topic.lab() && data.hasExperiment(owner, selected)
                    && topic.prerequisites().stream().allMatch(id -> data.completed(owner, id))
                    && data.activeResearch(owner, facility()).size() < Hk3ResearchMath.slots(lab));
            return view;
        }

        /** 中文说明：该处说明已按当前代码行为整理。*/
        private ItemStack representative(String id) {
            var tag = TagKey.create(Registries.ITEM, new ResourceLocation(id));
            return BuiltInRegistries.ITEM.getTag(tag).flatMap(set -> set.stream()
                    .map(holder -> holder.value()).min(java.util.Comparator.comparing(item -> BuiltInRegistries.ITEM.getKey(item).toString())))
                    .map(ItemStack::new).orElse(ItemStack.EMPTY);
        }

        /** 中文说明：该处说明已按当前代码行为整理。*/
        private void action(String action) {
            if (!(player instanceof ServerPlayer server) || !authorized(player)) return;
            if ("cancel".equals(action)) {
                var data=Hk3ResearchData.get(server);var job=data.displayJob(getResearchTeamUUID(),selected);
                if(job!=null)data.cancelResearch(getResearchTeamUUID(),server.getUUID(),job.quote().topic()); return;
            }
            if ("claim".equals(action)) {
                com.sirin.hk3gtl.common.research.Hk3ResearchPayment.claimRefunds(server);
                server.inventoryMenu.broadcastChanges(); return;
            }
            if ("experiment".equals(action)) {
                var result=Hk3LabExperimentService.start(server,getResearchTeamUUID(),facility(),lab,isFormed(),selected);
                feedback="hk3gtl.research.start."+result.name().toLowerCase(java.util.Locale.ROOT); return;
            }
            if ("toggle".equals(action)) { getRecipeLogic().setWorkingEnabled(!getRecipeLogic().isWorkingEnabled()); return; }
            if (action.startsWith("select:")) {
                String id = action.substring(7);
                if (Hk3ResearchPlans.get(id) != null) { selected = id; feedback = ""; }
                return;
            }
            if (!("points".equals(action) || "materials".equals(action))) return;
            var result = requestResearch(server, selected, "points".equals(action));
            feedback = "hk3gtl.research.start." + result.name().toLowerCase(java.util.Locale.ROOT);
            // 即使长故事已滚动，开题结果仍通过聊天可见；失败不会扣款或授予实验。
            // 中文备注：该处说明已按当前代码行为整理。
            var message=net.minecraft.network.chat.Component.translatable(feedback);
            if(result==Hk3ResearchStartService.Result.LOCKED || result==Hk3ResearchStartService.Result.UNAVAILABLE
                    || result==Hk3ResearchStartService.Result.CAPACITY) {
                String reason=blocker(server);
                if(!reason.isEmpty()) {
                    var detail="hk3gtl.research.terminal.block.lab".equals(reason)
                            ? net.minecraft.network.chat.Component.translatable(reason,
                                    net.minecraft.network.chat.Component.translatable("hk3gtl.research.lab.grade."+
                                            Hk3ResearchCatalog.bundled().get(selected).lab()))
                            : net.minecraft.network.chat.Component.translatable(reason);
                    message.append(": ").append(detail);
                }
            }
            server.sendSystemMessage(message);
        }

        /** 中文说明：该处说明已按当前代码行为整理。*/
        private String blocker(ServerPlayer server) {
            var data=Hk3ResearchData.get(server); var id=getResearchTeamUUID();
            var topic=Hk3ResearchCatalog.bundled().get(selected);
            if(!authorized(server)) return "hk3gtl.research.lab.denied";
            if(!isFormed()) return "hk3gtl.research.lab.unformed";
            if(data.completed(id,selected)) return "hk3gtl.research.start.completed";
            if(data.displayJob(id,selected)!=null) return "hk3gtl.research.start.running";
            if(lab<topic.lab()) return "hk3gtl.research.terminal.block.lab";
            if(!topic.prerequisites().stream().allMatch(parent -> data.completed(id,parent))) return "hk3gtl.research.terminal.block.parents";
            if(!data.hasExperiment(id,selected)) return "hk3gtl.research.terminal.block."+("RN-HED".equals(selected)?"sampling":"experiment");
            if(data.activeResearch(id,facility()).size()>=Hk3ResearchMath.slots(lab)) return "hk3gtl.research.start.capacity";
            return "";
        }
    }

    /** 按研究所位置查询本队、同维度、实际扣电的稳定锚；尚无正式锚时返回零。 */
    private double suppression() {
        return getLevel() instanceof net.minecraft.server.level.ServerLevel level
                ? com.sirin.hk3gtl.common.gaze.Hk3ResearchSuppression.at(level, getPos(), getResearchTeamUUID()) : 0;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Hk3ResearchStartService.Result requestResearch(ServerPlayer player, String topic, boolean points) {
        return Hk3ResearchStartService.start(player, getResearchTeamUUID(), facility(), lab, authorized(player) && isFormed(),
                topic, points, Hk3ResearchTeams.gaze(player.server,getResearchTeamUUID()), suppression());
    }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    private List<Hk3ResearchPlans.Material> scaled(Hk3ResearchPlans.Plan plan, ServerPlayer player) {
        double gaze=Hk3ResearchTeams.gaze(player.server,getResearchTeamUUID());
        return Hk3ResearchStartService.materials(plan, lab, gaze, suppression());
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
