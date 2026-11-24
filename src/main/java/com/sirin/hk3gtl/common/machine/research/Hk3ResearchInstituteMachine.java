package com.sirin.hk3gtl.common.machine.research;

/**
 * 【文件职责／本轮边界】团队共享任务、成员个人付款、全队离线暂停正式研究；实验固定速度续做，空闲不计算注视度。
 */



import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.GTValues;
import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.lowdragmc.lowdraglib.misc.ItemStackTransfer;
import com.lowdragmc.lowdraglib.syncdata.annotation.Persisted;
import com.lowdragmc.lowdraglib.syncdata.field.ManagedFieldHolder;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.config.Hk3ResearchSettings;
import com.sirin.hk3gtl.common.gui.Hk3ResearchTerminalWidget;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
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
import java.math.BigInteger;
import java.util.List;

/** 实体ERM逐课题付费；W13请求接双边授权服务，仅真实母机可供能。 */
public final class Hk3ResearchInstituteMachine extends Hk3WorkableMultiblockMachine {
    private static final ManagedFieldHolder FIELDS = new ManagedFieldHolder(
            Hk3ResearchInstituteMachine.class, HK3_MANAGED_FIELD_HOLDER);
    private final int lab;
    @Persisted private final ItemStackTransfer erosionModule;
    @Persisted private boolean erosionEnabled;
    @Persisted private java.util.UUID researchServiceId = java.util.UUID.randomUUID();
    private boolean erosionActive, erosionPowerLimited;
    private Hk3EnergyTick researchRefund;
    private long researchPowerTick=Long.MIN_VALUE;
    private BigInteger researchPowerUsed=BigInteger.ZERO;

    /** 阶级是注册定义常量，非法值拒绝；不通过NBT或玩家包升级研究所。 / Lab level is fixed by registration, never client/NBT-upgradable. */
    public Hk3ResearchInstituteMachine(IMachineBlockEntity holder, int lab) {
        super(holder); Hk3ResearchMath.slots(lab); this.lab=lab;
        erosionModule = new ItemStackTransfer(1) {
            @Override public int getSlotLimit(int slot) { return 1; }
        };
        erosionModule.setFilter(stack -> stack.is(Hk3Items.EROSION_RESEARCH_MODULE.get()));
        erosionModule.setOnContentsChanged(this::markDirty);
    }

    @Override public ManagedFieldHolder getFieldHolder() { return FIELDS; }

    @Override public void onMachineRemoved() {
        super.onMachineRemoved();
        clearInventory(erosionModule);
    }

    private boolean erosionInstalled() {
        var module = erosionModule.getStackInSlot(0);
        return module.getCount() == 1 && module.is(Hk3Items.EROSION_RESEARCH_MODULE.get());
    }
    @Override protected boolean enableMultiRecipe() { return false; }

    @Override protected com.gregtechceu.gtceu.api.machine.trait.RecipeLogic createRecipeLogic(Object... args) {
        return new com.gregtechceu.gtceu.api.machine.trait.RecipeLogic(this) {
            @Override public void serverTick() { /* 中文说明：该处说明已按当前代码行为整理。*/ }
        };
    }

    @Override public void onLoad() { super.onLoad(); if (!isRemote()) subscribeServerTick(this::researchTick); }

    private String facility() { return getLevel().dimension().location()+"@"+getPos().asLong(); }

    public java.util.UUID researchServiceId() { return researchServiceId; }
    public Hk3W13ResearchData.Endpoint researchEndpoint() { return Hk3W13ResearchService.endpoint(this, researchServiceId); }

    private void researchTick() {
        erosionActive = false;
        erosionPowerLimited = false;
        if (!Hk3ResearchSettings.enabled()) return;
        if (isInValid() || !isFormed() || !getRecipeLogic().isWorkingEnabled() || getOwnerUUID()==null || getLevel().getServer()==null) return;
        if (researchRefund == null) researchRefund=Hk3RefundJournal.resume(this);
        if (researchRefund != null) {
            if (!researchRefund.finish(false)) return;
            researchRefund=null;
        }
        var server=getLevel().getServer(); var scope=getResearchTeamUUID();
        var data=Hk3ResearchData.get(server);
        if(scope==null||!com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts
                .permitsMachine(data,scope,String.format(java.util.Locale.ROOT,"S%02d",lab),false))return;
        var jobs=data.activeResearch(scope,facility());
        if(jobs.isEmpty())return;
        for (var job : jobs) if (job.quote().lab() == lab && !Hk3ResearchStartService.dedicatedToW13(job.quote().topic()))
            Hk3W13ResearchService.submit(this, job, (wonder, advanced) -> advanceJob(job, wonder, advanced));
    }

    private void advanceJob(Hk3ResearchWorkQueue.Snapshot expected, boolean wonder, Runnable advanced) {
        if (isInValid() || !isFormed() || !getRecipeLogic().isWorkingEnabled() || researchRefund!=null) return;
        var server=getLevel().getServer(); var scope=getResearchTeamUUID();
        var data=Hk3ResearchData.get(server);
        var job=data.researchJob(scope,expected.quote().topic());
        if(job==null || !job.id().equals(expected.id()))return;
        var online=Hk3ResearchTeams.online(server,scope);
        double gaze=Hk3ResearchTeams.gaze(server,scope);
        double suppression=suppression();
        boolean researched=data.completed(scope,"RN-ERM"), installed=erosionInstalled();
        long base=job.quote().eut();
        var ports=Hk3PowerPorts.of(getRecipeLogic());
        long tick=server.overworld().getGameTime();
        if (researchPowerTick!=tick) {
            researchPowerTick=tick;
            researchPowerUsed=BigInteger.ZERO;
        }
        long available=Hk3PortPayment.available(ports)
                .min(Hk3PortPayment.power(ports).subtract(researchPowerUsed).max(BigInteger.ZERO))
                .min(BigInteger.valueOf(Long.MAX_VALUE)).longValue();
        boolean boosted=Hk3ErosionResearch.boost(lab,researched,installed,erosionEnabled,
                job.quote().topic(),base,available);
        long cost=Hk3ErosionResearch.cost(base,boosted);
        double speed=Hk3ResearchMath.speed(lab,gaze,suppression,boosted,wonder);
        if (!boosted && !online.isEmpty() && job.progress()<job.quote().ticks()
                && Hk3ErosionResearch.boost(lab,researched,installed,erosionEnabled,
                job.quote().topic(),base,Long.MAX_VALUE)) erosionPowerLimited=true;
        boolean[] energyPaid={false};
        var payment=Hk3RefundJournal.open(this);
        Hk3ResearchWorkQueue.Outcome result;
        try {
            result=data.advanceResearch(scope, job.quote().topic(), facility(), tick,
                    true, !online.isEmpty(), speed, () -> {
                        energyPaid[0]=available>=cost && Hk3PortPayment.pay(ports,BigInteger.valueOf(cost),payment);
                        return energyPaid[0];
                    });
        } finally {
            if (energyPaid[0]) researchPowerUsed=researchPowerUsed.add(BigInteger.valueOf(cost));
            if (!payment.finish(energyPaid[0])) researchRefund=payment;
            if (energyPaid[0]) advanced.run();
        }
        if (boosted && energyPaid[0]) erosionActive=true;
        var experiment=com.sirin.hk3gtl.common.research.Hk3LabExperimentRules.get(job.quote().topic());
        if(result==Hk3ResearchWorkQueue.Outcome.PAUSED&&experiment!=null&&job.progress()>0
                &&job.progress()<job.quote().ticks()&&!online.isEmpty()&&available<cost)
            com.sirin.hk3gtl.common.easter.Hk3EggResearchScenes.paused(server,
                    Hk3ResearchData.payer(scope,job.quote()),job,experiment.research());
        if(lab>1&&energyPaid[0]&&speed<=Hk3ResearchMath.speed(lab,com.sirin.hk3gtl.common.constants.Hk3Constants.GAZE_MAX,0,false,false)){
            var payerId=com.sirin.hk3gtl.common.research.Hk3ResearchData.payer(scope,job.quote());
            com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(server).produced(payerId,"receipt:47",1);
        }
        if (result==Hk3ResearchWorkQueue.Outcome.COMPLETED || result==Hk3ResearchWorkQueue.Outcome.STAGE_COMPLETED) {
            if (result==Hk3ResearchWorkQueue.Outcome.COMPLETED) {
                com.sirin.hk3gtl.common.research.Hk3ResearchEvidenceAnalysis.researchCompleted(data,scope,lab,job,tick);
                if(com.sirin.hk3gtl.common.research.Hk3LabExperimentRules.get(job.quote().topic())==null)
                    com.sirin.hk3gtl.common.narrative.story.Hk3StoryService.teamFact(server,scope,"research_"+job.quote().topic());
            }
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

    @Override public ModularUI createUI(Player player) {
        Session session = new Session(player);
        return new ModularUI(Hk3ResearchTerminalWidget.WIDTH, Hk3ResearchTerminalWidget.HEIGHT, this, player)
                .widget(new Hk3ResearchTerminalWidget(session::snapshot, session::action));
    }

    private final class Session {
        private final Player player;
        private String selected = Hk3ResearchPlans.all().keySet().iterator().next();
        private String feedback = "";
        private String shown = "";
        private Session(Player player) { this.player = player; }

        private CompoundTag snapshot() {
            CompoundTag view = new CompoundTag();
            if (!(player instanceof ServerPlayer server) || !authorized(server)) return view;
            if(!shown.equals(selected)){
                shown=selected;
                com.sirin.hk3gtl.common.easter.Hk3EggResearchScenes.opened(server,selected);
            }
            var data = Hk3ResearchData.get(server);
            var owner = getResearchTeamUUID();
            view.putBoolean("authorized", true);
            view.putBoolean("formed", isFormed());
            view.putBoolean("enabled", getRecipeLogic().isWorkingEnabled());
            view.putInt("lab", lab);
            view.putInt("slots", Hk3ResearchMath.slots(lab));
            view.putInt("active", data.usedResearchSlots(facility()));
            view.putString("points", data.points(server.getUUID()).toString());
            boolean installed=erosionInstalled();
            boolean allowed=Hk3ErosionResearch.allowed(lab,data.completed(owner,"RN-ERM"));
            view.putBoolean("ermInstalled",installed);
            view.putBoolean("ermAllowed",allowed);
            view.putBoolean("ermEnabled",erosionEnabled);
            view.putString("ermState",!allowed?"locked":!installed?"missing":!erosionEnabled?"off"
                    :erosionActive?"active":erosionPowerLimited?"power":"idle");
            view.putString("w13State",Hk3W13ResearchService.status(Hk3ResearchInstituteMachine.this));
            view.putString("selected", selected);
            if (selected.equals(Hk3ResearchData.CORE_RESEARCH)) {
                ListTag circuits = new ListTag();
                for (var tag : com.gregtechceu.gtceu.data.recipe.CustomTags.CIRCUITS_ARRAY) {
                    String tier = tag.location().getPath().substring("circuits/".length());
                    CompoundTag row = new CompoundTag();
                    row.putString("tier", tier);
                    row.putBoolean("technology", data.hasCircuitTechnology(owner, tier));
                    row.putBoolean("analysis", data.hasCircuitAnalysis(owner, tier));
                    circuits.add(row);
                }
                view.put("circuits", circuits);
            }
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
            view.putBoolean("canExperiment",isFormed() && (job==null || selected.equals("RN-ERM") && data.awaitingLabAid(owner)) && !data.hasExperiment(owner,selected)
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
                for (int i = 0; i < 36; i++) {
                    ItemStack stack = server.getInventory().getItem(i);
                    if (stack.is(tag)) available += stack.getCount();
                }
                material.putLong("available", available); materials.add(material);
            }
            view.put("materials", materials);
            view.putBoolean("canStart", isFormed() && job == null && !data.completed(owner, selected)
                    && !Hk3ResearchStartService.dedicatedToW13(selected)
                    && lab >= topic.lab() && data.hasExperiment(owner, selected)
                    && topic.prerequisites().stream().allMatch(id -> data.completed(owner, id))
                    && data.activeResearch(owner, facility()).size() < Hk3ResearchMath.slots(lab));
            return view;
        }

        private ItemStack representative(String id) {
            var tag = TagKey.create(Registries.ITEM, new ResourceLocation(id));
            return BuiltInRegistries.ITEM.getTag(tag).flatMap(set -> set.stream()
                    .map(holder -> holder.value()).min(java.util.Comparator.comparing(item -> BuiltInRegistries.ITEM.getKey(item).toString())))
                    .map(ItemStack::new).orElse(ItemStack.EMPTY);
        }

        private void action(String action) {
            if (!(player instanceof ServerPlayer server) || !authorized(player)) return;
            if (action.startsWith("erm_")) {
                moduleAction(server,action);
                return;
            }
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

        /** 安装必须交出真实模块；取回不要求研究仍有效，避免归属变化后吞掉库存。 */
        private void moduleAction(ServerPlayer server,String action) {
            boolean allowed=Hk3ErosionResearch.allowed(lab,
                    Hk3ResearchData.get(server).completed(getResearchTeamUUID(),"RN-ERM"));
            if ("erm_remove".equals(action) && !erosionModule.getStackInSlot(0).isEmpty()) {
                var module=erosionModule.extractItem(0,1,false);
                erosionEnabled=false;
                server.getInventory().placeItemBackInInventory(module);
                feedback="hk3gtl.research.terminal.erm.removed";
            } else if ("erm_install".equals(action) && allowed && erosionModule.getStackInSlot(0).isEmpty()) {
                var held=server.getMainHandItem();
                if (!held.is(Hk3Items.EROSION_RESEARCH_MODULE.get())) {
                    feedback="hk3gtl.research.terminal.erm.held";
                    return;
                }
                if (!erosionModule.insertItem(0,held.copyWithCount(1),false).isEmpty()) return;
                held.shrink(1);
                erosionEnabled=false;
                feedback="hk3gtl.research.terminal.erm.installed";
            } else if ("erm_toggle".equals(action) && allowed && erosionInstalled()) {
                erosionEnabled=!erosionEnabled;
            } else {
                feedback="hk3gtl.research.terminal.erm.denied";
                return;
            }
            erosionActive=false;
            erosionPowerLimited=false;
            markDirty();
            server.inventoryMenu.broadcastChanges();
        }

        private String blocker(ServerPlayer server) {
            var data=Hk3ResearchData.get(server); var id=getResearchTeamUUID();
            var topic=Hk3ResearchCatalog.bundled().get(selected);
            if(!authorized(server)) return "hk3gtl.research.lab.denied";
            if(!isFormed()) return "hk3gtl.research.lab.unformed";
            if(data.completed(id,selected)) return "hk3gtl.research.start.completed";
            if(data.displayJob(id,selected)!=null) return "hk3gtl.research.start.running";
            if(Hk3ResearchStartService.dedicatedToW13(selected)) return "hk3gtl.research.terminal.block.w13";
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

    public Hk3ResearchStartService.Result requestResearch(ServerPlayer player, String topic, boolean points) {
        return Hk3ResearchStartService.start(player, getResearchTeamUUID(), facility(), lab, authorized(player) && isFormed(),
                topic, points, Hk3ResearchTeams.gaze(player.server,getResearchTeamUUID()), suppression());
    }

    private List<Hk3ResearchPlans.Material> scaled(Hk3ResearchPlans.Plan plan, ServerPlayer player) {
        double gaze=Hk3ResearchTeams.gaze(player.server,getResearchTeamUUID());
        return Hk3ResearchStartService.materials(plan, lab, gaze, suppression());
    }
}

